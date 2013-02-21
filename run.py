import sublime
import sublime_plugin

import pprint

from Vintageous.vi import motions
from Vintageous.vi import actions
from Vintageous.vi.constants import (MODE_INSERT, MODE_NORMAL, MODE_VISUAL,
                         MODE_VISUAL_LINE, MODE_NORMAL_INSERT,
                         _MODE_INTERNAL_NORMAL)
from Vintageous.vi.constants import mode_to_str
from Vintageous.vi.constants import digraphs
from Vintageous.vi.settings import SettingsManager, VintageSettings, SublimeSettings
from Vintageous.vi.registers import Registers, REG_UNNAMED
from Vintageous.vi import registers
from Vintageous.state import VintageState


class ViExecutionState(object):
    """This class' state must be reset at the end of each command.

       Tehrefore, use it only to communicate between different hooks, like _whatever_pre_motion,
       _whatever_post_every_motion, etc.

       If state was to change between different command invocations, there would be conflicts,
       because data would be mutated globally for all views and expected to be local for each of
       them using it.
    """
    select_word_begin_from_empty_line = False

    @staticmethod
    def reset_word_state():
        ViExecutionState.select_word_begin_from_empty_line = False

    @staticmethod
    def reset():
        ViExecutionState.reset_word_state()


class ViRunCommand(sublime_plugin.TextCommand):
    def run(self, edit, **vi_cmd_data):
        self.debug("Data in ViRunCommand:", vi_cmd_data)

        try:
            if vi_cmd_data['restore_original_carets']:
                self.save_caret_pos()

            # XXX: Fix this. When should we run the motion exactly?
            if vi_cmd_data['action']:
                # If no motion is present, we know we just have to run the action (like ctrl+w, v).
                if ((vi_cmd_data['motion']) or
                    (vi_cmd_data['motion_required'] and
                     not view.has_non_empty_selection_region())):
                        self.enter_visual_mode_if_needed(vi_cmd_data)
                        self.do_whole_motion(vi_cmd_data)

                # The motion didn't change the selections: abort action if so required.
                # TODO: What to do with .post_action() and .do_follow_up_mode() in this event?
                if (vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL and
                    all([v.empty() for v in self.view.sel()]) and
                    vi_cmd_data['cancel_action_if_motion_fails']):
                        return

                self.do_action(vi_cmd_data)
            else:
                self.do_whole_motion(vi_cmd_data)
        finally:
            self.do_post_action(vi_cmd_data)
            self.do_follow_up_mode(vi_cmd_data)

            if vi_cmd_data['must_update_xpos']:
                state = VintageState(self.view)

                first_sel = self.view.sel()[0]
                xpos = 0
                if state.mode == MODE_VISUAL:
                    if first_sel.a < first_sel.b:
                        xpos = self.view.rowcol(first_sel.b - 1)[1]
                    elif first_sel.a > first_sel.b:
                        xpos = self.view.rowcol(first_sel.b)[1]

                elif state.mode == MODE_NORMAL:
                    xpos = self.view.rowcol(first_sel.b)[1]

                state.xpos = xpos

            if vi_cmd_data['scroll_into_view']:
                # TODO: If moving by lines, scroll the minimum amount to display the new sels.
                self.view.show(self.view.sel()[0])

            state = VintageState(self.view)
            state.reset(next_mode=vi_cmd_data['next_mode'])

    def save_caret_pos(self):
        self.old_sels = list(self.view.sel())

    def do_whole_motion(self, vi_cmd_data):
        # If the action must be repeated, then the count cannot apply here; exit early.
        if vi_cmd_data['_repeat_action']:
            return

        self.do_pre_motion(vi_cmd_data)

        count = vi_cmd_data['count']
        for x in range(count):
            self.reorient_caret(vi_cmd_data)
            self.do_pre_every_motion(vi_cmd_data, x, count)
            self.do_motion(vi_cmd_data)
            self.do_post_every_motion(vi_cmd_data, x, count)

        self.do_post_motion(vi_cmd_data)
        self.reposition_caret(vi_cmd_data)

        self.add_to_jump_list(vi_cmd_data)

    def reorient_caret(self, vi_cmd_data):
        if not vi_cmd_data['__reorient_caret']:
            return

        if self.view.has_non_empty_selection_region():
            if (vi_cmd_data['motion'] and 'args' in vi_cmd_data['motion'] and
                (vi_cmd_data['motion']['args'].get('by') == 'characters' or
                 vi_cmd_data['motion']['args'].get('by') == 'lines' or
                 vi_cmd_data['motion']['args'].get('by') == 'words')):
                    if vi_cmd_data['motion']['args'].get('forward'):
                        self.view.run_command('reorient_caret', {'mode': vi_cmd_data['mode']})
                    else:
                        self.view.run_command('reorient_caret', {'forward': False, 'mode': vi_cmd_data['mode']})

    def reposition_caret(self, vi_cmd_data):
        if self.view.has_non_empty_selection_region():
            if vi_cmd_data['reposition_caret']:
                # XXX ??? ??? ???
                pass
                self.view.run_command(*vi_cmd_data['reposition_caret'])

    def enter_visual_mode_if_needed(self, vi_cmd_data):
        # FIXME: We shouldn't be adding args here; do this in the motion parsing phase instead.
        if vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL:
            vi_cmd_data['motion']['args']['extend'] = True
            return

        # XXX: We're assuming there's a motion available - why?
        # XXX: What are examples of commands that would pass this test?
        if (not self.view.has_non_empty_selection_region() and
            vi_cmd_data['action']):
                self.view.run_command('vi_enter_visual_mode')
                vi_cmd_data['motion']['args']['extend'] = True
                args = vi_cmd_data['motion'].get('args')
                if args.get('by') == 'characters':
                    vi_cmd_data['count'] = vi_cmd_data['count'] - 1

    # XXX: Change name to .do_coda() or .transition_to_text_mode() or something else that suggests
    # something mode than barely changing the mode.
    def do_follow_up_mode(self, vi_cmd_data):
        if vi_cmd_data['restore_original_carets'] == True:
            self.view.sel().clear()
            for s in self.old_sels:
                # XXX: If the buffer has changed, this won't work well.
                self.view.sel().add(s)

        if vi_cmd_data['follow_up_mode']:
            self.view.run_command(vi_cmd_data['follow_up_mode'])

    def do_motion(self, vi_cmd_data):
        cmd = vi_cmd_data['motion']['command']
        args = vi_cmd_data['motion']['args']
        self.debug("Vintageous: Motion command: ", cmd, args)
        self.view.run_command(cmd, args)

    def do_pre_every_motion(self, vi_cmd_data, current, total):
        """ST command classes used as 'pre_every_motion' hooks need to take
           two parameters: `current_iteration` and `total_iterations`.
        """
        if vi_cmd_data['pre_every_motion']:
            try:
                cmd, args = vi_cmd_data['pre_every_motion']
            except ValueError:
                cmd = vi_cmd_data['pre_every_motion'][0]
                args = {}

            args.update({'current_iteration': current, 'total_iterations': total})
            self.view.run_command(cmd, args)

    def do_post_every_motion(self, vi_cmd_data, current, total):
        """ST command classes used as 'post_every_motion' hooks need to take
           two parameters: `current_iteration` and `total_iterations`.
        """
        if vi_cmd_data['post_every_motion']:
            try:
                cmd, args = vi_cmd_data['post_every_motion']
            except ValueError:
                cmd = vi_cmd_data['post_every_motion'][0]
                args = {}

            args.update({'current_iteration': current, 'total_iterations': total})
            self.view.run_command(cmd, args)

    def do_pre_motion(self, vi_cmd_data):
        if vi_cmd_data['pre_motion']:
            self.view.run_command(*vi_cmd_data['pre_motion'])

    def do_post_motion(self, vi_cmd_data):
        for post_motion in vi_cmd_data['post_motion']:
            self.view.run_command(*post_motion)

    def do_action(self, vi_cmd_data):
        self.debug("Vintageous: Action command: ", vi_cmd_data['action'])
        if vi_cmd_data['action']:

            # Populate registers if we have to.
            if vi_cmd_data['can_yank']:
                state = VintageState(self.view)
                if vi_cmd_data['register']:
                    state.registers[vi_cmd_data['register']] = self.get_selected_text(vi_cmd_data)
                else:
                    # TODO: Encapsulate this in registers.py. We could have a
                    # .yank() method there that knows about all the details.
                    state.registers[REG_UNNAMED] = self.get_selected_text(vi_cmd_data)

            cmd = vi_cmd_data['action']['command']
            args = vi_cmd_data['action']['args']

            # Some actions that don't take a motion apply the count to the action. For example,
            # > in visual mode.
            i = vi_cmd_data['count'] if vi_cmd_data['_repeat_action'] else 1
            for t in range(i):
                self.view.run_command(cmd, args)

    def get_selected_text(self, vi_cmd_data):
        fragments = [self.view.substr(r) for r in list(self.view.sel())]
        if fragments and vi_cmd_data['yanks_linewise']:
            for i, f in enumerate(fragments):
                # When should we add a newline character?
                #  * always except when we have a non-\n-only string followed by a newline char.
                if (not f.endswith('\n')) or (f == '\n') or f.endswith('\n\n'):
                    fragments[i] = f + '\n'
        return fragments

    def do_post_action(self, vi_cmd_data):
        if vi_cmd_data['post_action']:
            self.view.run_command(*vi_cmd_data['post_action'])

    def add_to_jump_list(self, vi_cmd_data):
        if vi_cmd_data['is_jump']:
            self.view.run_command('vi_add_to_jump_list')

    def debug(self, *messages):
        state = VintageState(self.view)
        if state.settings.view['vintageous_verbose']:
            print("Vintageous:", *messages)
