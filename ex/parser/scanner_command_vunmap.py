from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_VUNMAP
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('vunmap', 'vu')
class TokenCommandVunmap(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_VUNMAP,
                         'vunmap', *args, **kwargs)
        self.target_command = 'ex_vunmap'

    @property
    def keys(self):
        return self.params['keys']


def scan_command_vunmap(state):
    params = {
        'keys': None,
    }

    m = state.match(r'\s*(?P<keys>.+?)\s*$')

    if m:
        params.update(m.groupdict())

    return None, [TokenCommandVunmap(params), TokenEof()]
