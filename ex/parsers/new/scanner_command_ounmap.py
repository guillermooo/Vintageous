from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_OUNMAP
from .tokens_base import TokenOfCommand
from Vintageous.ex import register_ex_command


@register_ex_command('ounmap', 'ounm')
class TokenCommandOunmap(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_OUNMAP,
                         'ounmap', *args, **kwargs)
        self.target_command = 'ex_ounmap'

    @property
    def keys(self):
        return self.params['keys']


def scan_command_ounmap(state):
    params = {
        'keys': None,
    }

    m = state.match(r'\s*(?P<keys>.+?)\s*$')

    if m:
        params.update(m.groupdict())

    return None, [TokenCommandOunmap(params), TokenEof()]
