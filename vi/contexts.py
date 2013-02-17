from Vintageous.vi.constants import MODE_NORMAL, MODE_NORMAL_INSERT, MODE_INSERT, ACTIONS_EXITING_TO_INSERT_MODE

class KeyContext(object):
    def __init__(self, state=None):
        self.state = state

    def change_vi_mode(self, key, operator, operand, match_all):
        is_normal_mode = self.state.settings.view['command_mode']
        is_exit_mode_insert = (self.state.action in ACTIONS_EXITING_TO_INSERT_MODE)
        if (is_normal_mode and is_exit_mode_insert):
            return True

        if self.state.mode == MODE_NORMAL_INSERT:
            return True

        if self.state.mode == MODE_INSERT:
            return True

        # check if we are NOT in normal mode -- if NOT, we need to change modes
        if self.state.mode != MODE_NORMAL:
            return True

 