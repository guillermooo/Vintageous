from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_TAB_PREV_COMMAND
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('tabprev', 'tabp')
class TokenTabPrevCommand(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__([],
                         TOKEN_COMMAND_TAB_PREV_COMMAND,
                         'tabprev', *args, **kwargs)
        self.target_command = 'ex_tabprev'


def scan_command_tab_prev_command(state):
    c = state.consume()

    if c == EOF:
        return None, [TokenTabPrevCommand(), TokenEof()]

    bang = c == '!'
    return None, [TokenTabPrevCommand(forced=bang), TokenEof()]
