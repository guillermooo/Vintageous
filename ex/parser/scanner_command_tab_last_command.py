from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_TAB_LAST_COMMAND
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('tablast', 'tabl')
class TokenTabLastCommand(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__([],
                         TOKEN_COMMAND_TAB_LAST_COMMAND,
                         'tablast', *args, **kwargs)
        self.target_command = 'ex_tablast'


def scan_command_tab_last_command(state):
    c = state.consume()

    if c == EOF:
        return None, [TokenTabLastCommand(), TokenEof()]

    bang = c == '!'
    return None, [TokenTabLastCommand(forced=bang), TokenEof()]
