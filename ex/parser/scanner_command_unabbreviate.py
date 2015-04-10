from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_UNABBREVIATE
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('unabbreviate', 'una')
class TokenUnabbreviate(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_UNABBREVIATE,
                         'unabbreviate', *args, **kwargs)
        self.target_command = 'ex_unabbreviate'

    @property
    def short(self):
        return self.params['lhs']


def scan_command_unabbreviate(state):
    params = {
        'lhs': None
    }
    m = state.expect_match(r'\s+(?P<lhs>.+?)\s*$')
    params.update(m.groupdict())
    return None, [TokenUnabbreviate(params), TokenEof()]
