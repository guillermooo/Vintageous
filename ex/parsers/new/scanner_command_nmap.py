from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_NMAP
from .tokens_base import TokenOfCommand
from Vintageous.ex import register_ex_command


@register_ex_command('nmap', 'nm')
class TokenCommandNmap(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_NMAP,
                         'nmap', *args, **kwargs)
        self.target_command = 'ex_nmap'

    @property
    def keys(self):
        return self.params['keys']

    @property
    def command(self):
        return self.params['command']


def scan_command_nmap(state):
    params = {
        'keys': None,
        'command': None,
    }

    m = state.match(r'\s*(?P<keys>.+?)\s+(?P<command>.+?)\s*$')

    if m:
        params.update(m.groupdict())

    return None, [TokenCommandNmap(params), TokenEof()]
