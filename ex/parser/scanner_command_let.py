from Vintageous.ex.ex_error import ERR_UNDEFINED_VARIABLE
from Vintageous.ex.ex_error import VimError

from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_LET
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('let', 'let')
class TokenCommandLet(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_LET,
                         'let', *args, **kwargs)
        self.target_command = 'ex_let'

    @property
    def variable_name(self):
        return self.params['name']

    @property
    def variable_value(self):
        return self.params['value']


def scan_command_let(state):
    params = {
        'name': None,
        'value': None,
    }

    # TODO(guillermooo): :let has many more options.

    m = state.expect_match(r'(?P<name>.+?)\s*=\s*(?P<value>.+?)\s*$',
        on_error=lambda: VimError(ERR_UNDEFINED_VARIABLE))

    params.update(m.groupdict())

    return None, [TokenCommandLet(params), TokenEof()]
