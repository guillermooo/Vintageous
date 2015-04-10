from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_DELETE
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('delete', 'd')
class TokenDelete(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_DELETE,
                         'delete', *args, **kwargs)
        self.addressable = True
        self.target_command = 'ex_delete'

    @property
    def register(self):
        return self.params['register']

    @property
    def count(self):
        return self.params['count']


def scan_command_delete(state):
    params = {
        'register': '"',
        'count': None,
    }

    state.skip(' ')
    state.ignore()

    c = state.consume()

    if c == EOF:
        return None, [TokenDelete(params), TokenEof()]

    state.backup()
    state.skip(' ')
    state.ignore()

    m = state.expect_match(r'(?P<register>[a-zA-Z0-9"])(?:\s+(?P<count>\d+))?\s*$')
    params.update(m.groupdict())

    if params ['count']:
        raise NotImplementedError('parameter not implemented')

    return None, [TokenDelete(params), TokenEof()]
