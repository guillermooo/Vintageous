from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_ABBREVIATE
from .tokens_base import TokenOfCommand

from Vintageous.ex.ex_error import ERR_INVALID_ARGUMENT
from Vintageous.ex.ex_error import VimError
from Vintageous import ex


@ex.command('abbreviate', 'ab')
class TokenCommandAbbreviate(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                        TOKEN_COMMAND_ABBREVIATE,
                        'write', *args, **kwargs)
        self.target_command = 'ex_abbreviate'

    @property
    def short(self):
        return self.params['short']

    @property
    def full(self):
        return self.params['full']


def scan_command_abbreviate(state):
    params = {
        'short': None,
        'full': None,
    }

    state.expect(' ')
    state.skip(' ')
    state.ignore()

    if state.consume() == EOF:
        return None, [TokenCommandAbbreviate({}), TokenEof()]

    state.backup()

    m = state.match(r'(?P<short>.+?)(?: +(?P<full>.+))?$')
    params.update(m.groupdict())

    return None, [TokenCommandAbbreviate(params), TokenEof()]
