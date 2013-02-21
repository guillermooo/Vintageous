import sublime

from Vintageous.vi.constants import MODE_NORMAL, MODE_NORMAL_INSERT, MODE_INSERT, ACTIONS_EXITING_TO_INSERT_MODE

class KeyContext(object):
    def __init__(self, state=None):
        self.state = state

    def __get__(self, instance, owner):
        if instance is not None:
            return KeyContext(instance)
        return KeyContext()

    def change_vi_mode(self, key, operator, operand, match_all):
        is_normal_mode = self.state.settings.view['command_mode']
        is_exit_mode_insert = (self.state.action in ACTIONS_EXITING_TO_INSERT_MODE)
        if (is_normal_mode and is_exit_mode_insert):
            return self.check(True, operator, operand, match_all)

        if self.state.mode == MODE_NORMAL_INSERT:
            return True

        if self.state.mode == MODE_INSERT:
            return True

        # check if we are NOT in normal mode -- if NOT, we need to change modes
        if self.state.mode != MODE_NORMAL:
            return True

    def check(self, value, operator, operand, match_all):
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
