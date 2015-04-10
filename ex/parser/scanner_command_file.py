from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_FILE
from .tokens_base import TokenOfCommand

from Vintageous.ex.ex_error import ERR_TRAILING_CHARS
from Vintageous.ex.ex_error import VimError
from Vintageous import ex


@ex.command('file', 'f')
class TokenCommandFile(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__({},
                         TOKEN_COMMAND_FILE,
                         'file', *args, **kwargs)
        self.target_command = 'ex_file'


def scan_command_file(state):
    bang = state.consume()

    if bang == EOF:
        return None, [TokenCommandFile(), TokenEof()]

    bang = bang == '!'
    if not bang:
        raise VimError(ERR_TRAILING_CHARS)

    state.expect(EOF, on_error=lambda: VimError(ERR_TRAILING_CHARS))

    return None, [TokenCommandFile (forced=bang == '!'), TokenEof ()]
