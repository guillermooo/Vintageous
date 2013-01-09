import sublime
import sublime_plugin

import pprint

from Vintageous.vi import motions
from Vintageous.vi import actions
from Vintageous.vi.constants import (MODE_INSERT, MODE_NORMAL, MODE_VISUAL,
                         MODE_VISUAL_LINE, MODE_NORMAL_INSERT,
                         _MODE_INTERNAL_VISUAL)
from Vintageous.vi.constants import mode_to_str
from Vintageous.vi.constants import digraphs
from Vintageous.vi.settings import SettingsManager, VintageSettings, SublimeSettings
from Vintageous.vi.registers import Registers
from Vintageous.vi import registers
from Vintageous.state import VintageState


class ViExecutionState(object):
    # So far, I've encountered one case where global state for the command execution seems
    # necessary: When issuing *w* from an EMPTYLINE in VISUALMODE, the FIRSTCHARACTER of the
    # FIRSTWORD on the NEXTLINE is selected. By issuing *w* again after that, we should advance to
    # the NEXTWORD. However, due to the way *w* motions are adjusted now in a post motion hook,
    # the second case is indistinguishable from the first one, so this helps to disambiguate.
    # XXX: Resetting this class should be done in many places, like when changing modes (???).
    # XXX: Use view settings for storage as in VintageState. Otherwise there'll be conflicts when
    # switching between views.
    dont_shrink_word = False

    @staticmethod
    def reset_word_state():
        ViExecutionState.dont_shrink_word = False

    @staticmethod
    def reset():
        ViExecutionState.reset_word_state()


class ViRunCommand(sublime_plugin.TextCommand):
    def run(self, edit, **vi_cmd_data):
        print("Data in ViRunCommand:", vi_cmd_data)

        sels_before = list(self.view.sel())

        try:
            # XXX: Fix this. When should we run the motion exactly?
            if vi_cmd_data['action']:
                if ((vi_cmd_data['motion']) or
                    (vi_cmd_data['motion_required'] and
                     not view.has_non_empty_selection_region())):
                        self.enter_visual_mode(vi_cmd_data)
                        self.do_whole_motion(vi_cmd_data)

                sels_after = list(self.view.sel())

                # The motion didn't change the selections: abort action if so required.
                # TODO: What to do with .post_action() and .do_follow_up_mode() in this event?
                if vi_cmd_data['cancel_action_if_motion_fails'] and (sels_after == sels_before):
                    return

                self.do_action(vi_cmd_data)
            else:
                self.do_whole_motion(vi_cmd_data)
        finally:
            self.do_post_action(vi_cmd_data)
            self.do_follow_up_mode(vi_cmd_data)

    def do_whole_motion(self, vi_cmd_data):
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
                        self.view.run_command('reorient_caret', {'mode': vi_cmd_data['mode'] ,'_internal_mode': vi_cmd_data['_internal_mode']})
                    else:
                        self.view.run_command('reorient_caret', {'forward': False, 'mode': vi_cmd_data['mode'], '_internal_mode': vi_cmd_data['_internal_mode']})

    def reposition_caret(self, vi_cmd_data):
        if self.view.has_non_empty_selection_region():
            if vi_cmd_data['reposition_caret']:
                # XXX ??? ??? ???
                pass
                self.view.run_command(*vi_cmd_data['reposition_caret'])

    def enter_visual_mode(self, vi_cmd_data):
        # TODO: This step may be duplicated. Check motion definitions as well.
        if vi_cmd_data['_internal_mode'] == _MODE_INTERNAL_VISUAL:
            vi_cmd_data['motion']['args']['extend'] = True
            return

        if vi_cmd_data['action'] and not self.view.has_non_empty_selection_region():
            self.view.run_command('vi_enter_visual_mode')
            vi_cmd_data['motion']['args']['extend'] = True
            args = vi_cmd_data['motion'].get('args')
            if args.get('by') == 'characters':
                vi_cmd_data['count'] = vi_cmd_data['count'] - 1

    def do_follow_up_mode(self, vi_cmd_data):
        if vi_cmd_data['follow_up_mode']:
            self.view.run_command(vi_cmd_data['follow_up_mode'])

    def do_motion(self, vi_cmd_data):
        cmd = vi_cmd_data['motion']['command']
        args = vi_cmd_data['motion']['args']
        print("Motion command:", cmd, args)
        self.view.run_command(cmd, args)

    def do_pre_every_motion(self, vi_cmd_data, current, total):
        # XXX: This is slow. Make it faster.
        # ST command classes used as 'pre_every_motion' hooks need to take
        # two parameters: current_iteration and total_iterations.
        if vi_cmd_data['pre_every_motion']:
            try:
                cmd, args = vi_cmd_data['pre_every_motion']
            except ValueError:
                cmd = vi_cmd_data['pre_every_motion'][0]
                args = {}

            args.update({'current_iteration': current, 'total_iterations': total})
            self.view.run_command(cmd, args)

    def do_post_every_motion(self, vi_cmd_data, current, total):
        # XXX: This is slow. Make it faster.
        # ST command classes used as 'post_every_motion' hooks need to take
        # two parameters: current_iteration and total_iterations.
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
        print("Action command:", vi_cmd_data['action'])
        if vi_cmd_data['action']:

            # Populate registers if we have to.
            if vi_cmd_data['can_yank']:
                state = VintageState(self.view)
                if vi_cmd_data['register']:
                    state.registers[vi_cmd_data['register']] = self.get_selected_text(vi_cmd_data)
                else:
                    # TODO: Encapsulate this in registers.py.
                    state.registers['"'] = self.get_selected_text(vi_cmd_data)

            cmd = vi_cmd_data['action']['command']
            args = vi_cmd_data['action']['args']
            self.view.run_command(cmd, args)

    def get_selected_text(self, vi_cmd_data):
        text = '\n'.join([self.view.substr(r) for r in list(self.view.sel())])
        if text and vi_cmd_data['yanks_linewise']:
            if not text.startswith('\n'):
                text = '\n' + text
            if not text.endswith('\n'):
                text = text + '\n'
        return text

    def do_post_action(self, vi_cmd_data):
        if vi_cmd_data['post_action']:
            self.view.run_command(*vi_cmd_data['post_action'])

    def add_to_jump_list(self, vi_cmd_data):
        if vi_cmd_data['is_jump']:
            self.view.run_command('vi_add_to_jump_list')
