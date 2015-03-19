from .state import EOF
from .tokens import TokenEof
from .tokens_commands import TokenCommandOnly


def scan_command_only(state):
    bang = state.consume()

    if bang == '!':
        state.ignore()
        state.expect(EOF)
        return None, [TokenCommandOnly(forced=True), TokenEof()]

    assert bang == EOF, 'trailing characters'
    return None, [TokenCommandOnly(), TokenEof()]
