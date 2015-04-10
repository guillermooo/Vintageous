from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_QUIT_ALL_COMMAND
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('quall', 'qa')
class TokenQuitAllCommand(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__({},
                         TOKEN_COMMAND_QUIT_ALL_COMMAND,
                         'qall', *args, **kwargs)
        self.target_command = 'ex_quit_all'


def scan_command_quit_all_command(state):
    c = state.consume()

    bang = c == '!'

    state.expect(EOF)

    return None, [TokenQuitAllCommand(forced=bang), TokenEof()]
