from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_TAB_FIRST_COMMAND
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('tabfirst', 'tabfir')
@ex.command('tabrewind', 'tabr')
class TokenTabFirstCommand(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__([],
                         TOKEN_COMMAND_TAB_FIRST_COMMAND,
                         'tabfirst', *args, **kwargs)
        self.target_command = 'ex_tabfirst'


def scan_command_tab_first_command(state):
    c = state.consume()

    if c == EOF:
        return None, [TokenTabFirstCommand(), TokenEof()]

    bang = c == '!'
    return None, [TokenTabFirstCommand(forced=bang), TokenEof()]
