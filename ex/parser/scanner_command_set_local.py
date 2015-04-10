from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_SET_LOCAL
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('setlocal', 'setlocal')
class TokenSet(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_SET_LOCAL,
                         'setlocal', *args, **kwargs)
        self.target_command = 'ex_set_local'

    @property
    def value(self):
        return self.params['value']

    @property
    def option(self):
        return self.params['option']


def scan_command_set_local(state):
    params = {
        'option': None,
        'value': None,
    }

    state.skip(' ')
    state.ignore()

    # TODO(guillermooo): implement other options.
    m = state.expect_match(r'(?P<option>.+?)(?:[:=](?P<value>.+?))?$')
    params.update(m.groupdict())

    return None, [TokenSet(params), TokenEof()]
