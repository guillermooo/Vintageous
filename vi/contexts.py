import sublime

from Vintageous.vi.constants import MODE_NORMAL, MODE_NORMAL_INSERT, MODE_INSERT, ACTIONS_EXITING_TO_INSERT_MODE, MODE_VISUAL_LINE, MODE_VISUAL
from Vintageous.vi import constants


class KeyContext(object):
    def __init__(self, state=None):
        self.state = state

    def __get__(self, instance, owner):
        if instance is not None:
            return KeyContext(instance)
        return KeyContext()

    def vi_must_change_mode(self, key, operator, operand, match_all):
        is_normal_mode = self.state.settings.view['command_mode']
        is_exit_mode_insert = (self.state.action in ACTIONS_EXITING_TO_INSERT_MODE)
        if (is_normal_mode and is_exit_mode_insert):
            return self._check(True, operator, operand, match_all)

        if self.state.mode == MODE_NORMAL_INSERT:
            return True

        if self.state.mode == MODE_INSERT:
            return True

        # check if we are NOT in normal mode -- if NOT, we need to change modes
        if self.state.mode != MODE_NORMAL:
            return True

    def vi_is_buffer(self, key, operator, operand, match_all):
        # !! The following check is based on an implementation detail of Sublime Text. !!
        is_console = False if (getattr(self.state.view, 'settings') is not None) else True
        is_widget = self.state.view.settings().get('is_widget')
        value = (is_console or is_widget)
        return self._check(value, operand, operand, match_all)

    def vi_must_exit_to_insert_mode(self, key, operator, operand, match_all):
        # XXX: This conext most likely not needed any more.
        is_normal_mode = self.state.settings.view['command_mode']
        is_exit_mode_insert = (self.state.action in ACTIONS_EXITING_TO_INSERT_MODE)
        value = (is_normal_mode and is_exit_mode_insert)
        return self._check(value, operator, operand, match_all)

    def vi_use_ctrl_keys(self, key, operator, operand, match_all):
        value = self.state.settings.view['vintageous_use_ctrl_keys']
        return self._check(value, operator, operand, match_all)

    def vi_has_incomplete_action(self, key, operator, operand, match_all):
        value = self.state.action in constants.INCOMPLETE_ACTIONS
        return self._check(value, operator, operand, match_all)

    def vi_has_action(self, key, operator, operand, match_all):
        value = self.state.action
        value = value and (value not in constants.INCOMPLETE_ACTIONS)
        return self._check(value, operator, operand, match_all)

    def vi_has_motion_count(self, key, operator, operand, match_all):
        value = self.state.motion_digits
        return self._check(value, operator, operand, match_all)

    def vi_mode_normal_insert(self, key, operator, operand, match_all):
        value = self.state.mode == MODE_NORMAL_INSERT
        return self._check(value, operator, operand, match_all)

    def vi_mode_cannot_push_zero(self, key, operator, operand, match_all):
        value = False
        if operator == sublime.OP_EQUAL:
            value = not (self.state.motion_digits or
                             self.state.action_digits)

        return self._check(value, operator, operand, match_all)

    def vi_mode_visual_any(self, key, operator, operand, match_all):
        value = self.state.mode in (MODE_VISUAL_LINE, MODE_VISUAL)
        return self._check(value, operator, operand, match_all)

    def vi_mode_visual_line(self, key, operator, operand, match_all):
        value = self.state.mode == MODE_VISUAL_LINE
        return self._check(value, operator, operand, match_all)

    def vi_mode_insert(self, key, operator, operand, match_all):
        value = self.state.mode == MODE_INSERT
        return self._check(value, operator, operand, match_all)

    def vi_mode_visual(self, key, operator, operand, match_all):
        value = self.state.mode == MODE_VISUAL
        return self._check(value, operator, operand, match_all)

    def vi_mode_normal(self, key, operator, operand, match_all):
        value = self.state.mode == MODE_NORMAL
        return self._check(value, operator, operand, match_all)

    def vi_state_next_character_is_user_input(self, key, operator, operand, match_all):
        value = (self.state.expecting_user_input or
                 self.state.expecting_register)
        return self._check(value, operator, operand, match_all)

    def vi_state_expecting_user_input(self, key, operator, operand, match_all):
        value = self.state.expecting_user_input
        return self._check(value, operator, operand, match_all)

    def vi_state_expecting_register(self, key, operator, operand, match_all):
        value = self.state.expecting_register
        return self._check(value, operator, operand, match_all)

    def vi_mode_can_push_digit(self, key, operator, operand, match_all):
        motion_digits = not self.state.motion
        action_digits = self.state.motion
        value = motion_digits or action_digits
        return self._check(value, operator, operand, match_all)

    def check(self, key, operator, operand, match_all):
        func = getattr(self, key, None)
        if func:
            return func(key, operator, operand, match_all)
        else:
            return None

    def _check(self, value, operator, operand, match_all):
        if operator == sublime.OP_EQUAL:
            if operand == True:
                return value
            elif operand == False:
                return not value
        elif operator == sublime.OP_NOT_EQUAL:
            if operand == True:
                return not value
            elif operand == False:
                return value
