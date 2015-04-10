from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_ONLY
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('only', 'on')
class TokenCommandOnly(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__({},
                        TOKEN_COMMAND_ONLY,
                        'only', *args, **kwargs)
        self.target_command = 'ex_only'


def scan_command_only(state):
    bang = state.consume()

    if bang == '!':
        state.ignore()
        state.expect(EOF)
        return None, [TokenCommandOnly(forced=True), TokenEof()]

    assert bang == EOF, 'trailing characters'
    return None, [TokenCommandOnly(), TokenEof()]
