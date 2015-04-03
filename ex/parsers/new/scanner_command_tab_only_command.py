from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_TAB_ONLY_COMMAND
from .tokens_base import TokenOfCommand


class TokenTabOnlyCommand(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__([],
                         TOKEN_COMMAND_TAB_ONLY_COMMAND,
                         'tabonly', *args, **kwargs)
        self.target_command = 'ex_tabonly'


def scan_command_tab_only_command(state):
    c = state.consume()

    if c == EOF:
        return None, [TokenTabOnlyCommand(), TokenEof()]

    bang = c == '!'
    return None, [TokenTabOnlyCommand(forced=bang), TokenEof()]
