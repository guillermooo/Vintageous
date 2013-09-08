import sublime
import sublime_plugin

import pprint

from Vintageous.state import VintageState
from Vintageous.vi import actions
from Vintageous.vi import motions
from Vintageous.vi import registers
from Vintageous.vi import utils
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import digraphs
from Vintageous.vi.constants import MODE_INSERT
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_NORMAL_INSERT
from Vintageous.vi.constants import mode_to_str
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.registers import REG_UNNAMED
from Vintageous.vi.registers import REG_SMALL_DELETE
from Vintageous.vi.registers import Registers
from Vintageous.vi.settings import SettingsManager
from Vintageous.vi.settings import SublimeSettings
from Vintageous.vi.settings import VintageSettings


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
    """Evaluates a full vim command. Everything that happens inside .run() will be left in the
       undo stack so that the "." command works as expected.
    """
    # TODO: Test me.
    def run(self, edit, **vi_cmd_data):
        self.debug("Data in ViRunCommand:", vi_cmd_data)

        state = VintageState(self.view)

        try:
            # Always save carets just in case.
            self.save_caret_pos()

            # If we're about to jump, we need to remember the current position so we can jump back
            # here. XXX creates_jump_at_current_position might be redundant.
            # TODO: Extract method.
            if vi_cmd_data['creates_jump_at_current_position'] or vi_cmd_data['is_jump']:
                self.add_to_jump_list(vi_cmd_data)

            sels_before_motion = list(self.view.sel())

            # XXX: Fix this. When should we run the motion exactly?
            if vi_cmd_data['action']:
                # If no motion is present, we know we just have to run the action (like ctrl+w, v).
                if ((vi_cmd_data['motion']) or
                    (vi_cmd_data['motion_required'] and
                     not view.has_non_empty_selection_region())):
                        self.do_whole_motion(vi_cmd_data)

                        # The motion didn't change the selections: abort action if so required.
                        # TODO: What to do with .post_action() and .restore_original_carets_if_needed() in this event?
                        if (vi_cmd_data['mode'] in (_MODE_INTERNAL_NORMAL, MODE_VISUAL) and
                            any([(old == new) for (old, new) in zip(sels_before_motion, list(self.view.sel()))]) and
                            vi_cmd_data['cancel_action_if_motion_fails']):
                                # TODO: There should be a method that lets us do this without modifying vi_cmd_data.
                                vi_cmd_data['restore_original_carets'] = True
                                # FIXME: This is redundant: we call the same method in 'finally' clause.
                                self.restore_original_carets_if_needed(vi_cmd_data)
                                utils.blink()
                                state.cancel_macro = True
                                return

                self.reorient_begin_to_end(vi_cmd_data)
                self.do_action(vi_cmd_data)
            else:
                self.do_whole_motion(vi_cmd_data)
                if (vi_cmd_data['mode'] == MODE_NORMAL and
                    any([(old == new) for (old, new) in zip(sels_before_motion, list(self.view.sel()))])):
                        state.cancel_macro = True
                        utils.blink()

        finally:
            # XXX: post_action should be run only if do_action succeeds (?).
            self.do_post_action(vi_cmd_data)

            # TODO: Extract method.
            if vi_cmd_data['must_update_xpos']:
                state = VintageState(self.view)
                state.update_xpos()

            self.do_modify_selections(vi_cmd_data)
            self.restore_original_carets_if_needed(vi_cmd_data)

            # TODO: Extract method.
            if vi_cmd_data['scroll_into_view']:
                if vi_cmd_data['scroll_command']:
                    self.view.run_command(*vi_cmd_data['scroll_command'])
                else:
                    # TODO: If moving by lines, scroll the minimum amount to display the new sels.
                    self.view.show(self.view.sel()[0])

            # We cannot run (maybe_)mark_undo_groups_for_gluing/glue_marked_undo_groups commands
            # within a command meant to be subsumed in the group to be glued. It won't work. So
            # let's save the data we need to transtion to the next mode, which will be taken care
            # of later by VintageState.reset().
            # XXX: This code can probably be moved to VintageState.run().
            # TODO: Extract method.
            state = VintageState(self.view)
            state.next_mode = vi_cmd_data['next_mode']
            state.next_mode_command = vi_cmd_data['follow_up_mode']

    def reorient_begin_to_end(self, vi_cmd_data):
        if vi_cmd_data['keep_selection_as_is']:
            return
        new_sel = []
        for s in self.view.sel():
            new_sel.append(sublime.Region(s.begin(), s.end()))
        self.view.sel().clear()
        self.view.sel().add_all(new_sel)

    # TODO: Test me.
    def save_caret_pos(self):
        self.old_sels = list(self.view.sel())

    # TODO: Test me.
    def do_whole_motion(self, vi_cmd_data):
        # If the action must be repeated, then the count cannot apply here; exit early.
        if vi_cmd_data['_repeat_action']:
            return

        self.do_pre_motion(vi_cmd_data)

        count = vi_cmd_data['count']
        for x in range(count):
            self.reorient_caret(vi_cmd_data)
            self.do_pre_every_motion(vi_cmd_data, x, count)

            if x != count - 1 or not vi_cmd_data['last_motion']:
                self.do_motion(vi_cmd_data)
                self.do_post_every_motion(vi_cmd_data, x, count)
            else:
                self.do_last_motion(vi_cmd_data)

        self.do_post_motion(vi_cmd_data)
        self.reposition_caret(vi_cmd_data)
        self.add_to_jump_list(vi_cmd_data)

    # TODO: Test me.
    # XXX: Is this method needed?
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

    # TODO: Test me.
    def reposition_caret(self, vi_cmd_data):
        if self.view.has_non_empty_selection_region():
            if vi_cmd_data['reposition_caret']:
                self.view.run_command(*vi_cmd_data['reposition_caret'])

    # TODO: Test me.
    def restore_original_carets_if_needed(self, vi_cmd_data):
        if vi_cmd_data['restore_original_carets'] == True:
            self.view.sel().clear()
            for s in self.old_sels:
                # XXX: If the buffer has changed, this won't work well.
                self.view.sel().add(s)

    # TODO: Test me.
    def do_modify_selections(self, vi_cmd_data):
        # Gives command a chance to modify the selection after the motion/action. Useful for
        # cases like 3yk, where we need to collapse to .b (== .begin()).
        if vi_cmd_data['selection_modifier']:
            self.view.run_command(*vi_cmd_data['selection_modifier'])

        if vi_cmd_data['align_with_xpos']:
            state = VintageState(self.view)
            self.view.run_command('_align_b_with_xpos', {'xpos': state.xpos})

    def do_motion(self, vi_cmd_data):
        cmd = vi_cmd_data['motion']['command']
        args = vi_cmd_data['motion']['args']
        self.debug("Vintageous: Motion command: ", cmd, args)
        self.view.run_command(cmd, args)

    def do_last_motion(self, vi_cmd_data):
        self.view.run_command(*vi_cmd_data['last_motion'])

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

            state = VintageState(self.view)
            # First of all, yank if we have to, before the selections get destroyed.
            state.registers.yank(vi_cmd_data)

            cmd = vi_cmd_data['action']['command']
            args = vi_cmd_data['action']['args']

            # Some actions that don't take a motion apply the count to the action. For example,
            # > in visual mode.
            i = vi_cmd_data['count'] if vi_cmd_data['_repeat_action'] else 1
            runner = self.view if not vi_cmd_data['is_window_command'] else self.view.window()
            if (vi_cmd_data['mode'] == _MODE_INTERNAL_NORMAL and
                vi_cmd_data['has_training_wheels']):
                    # TODO: Make this optional.
                    sels = list(self.view.sel())
                    sublime.set_timeout(lambda: self.view.erase_regions('vi_training_wheels'), 350)
                    self.view.add_regions('vi_training_wheels', sels, 'comment', '', sublime.DRAW_NO_FILL)
            for t in range(i):
                runner.run_command(cmd, args)

    def do_post_action(self, vi_cmd_data):
        if vi_cmd_data['post_action']:
            self.view.run_command(*vi_cmd_data['post_action'])

    def add_to_jump_list(self, vi_cmd_data):
        if vi_cmd_data['is_jump']:
            # It's a window command, but arguably this is prone to error.
            # FIXME: Devise a way to convey in the command name whether we're looking at a view
            # or a window command.
            self.view.window().run_command('vi_add_to_jump_list')

    def debug(self, *messages):
        state = VintageState(self.view)
        if state.settings.view['vintageous_verbose']:
            print("Vintageous:", *messages)
