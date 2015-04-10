from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_QUIT_COMMAND
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('quit', 'q')
class TokenQuitCommand(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__({},
                         TOKEN_COMMAND_QUIT_COMMAND,
                         'quit', *args, **kwargs)
        self.target_command = 'ex_quit'


def scan_command_quit_command(state):
    c = state.consume()

    bang = c == '!'

    state.expect(EOF)

    return None, [TokenQuitCommand(forced=bang), TokenEof()]
