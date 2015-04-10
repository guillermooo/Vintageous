from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_MAP
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('map', 'map')
class TokenCommandMap(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_MAP,
                         'map', *args, **kwargs)
        self.target_command = 'ex_map'

    @property
    def keys(self):
        return self.params['keys']

    @property
    def command(self):
        return self.params['command']


def scan_command_map(state):
    params = {
        'keys': None,
        'command': None,
    }

    m = state.match(r'\s*(?P<keys>.+?)\s+(?P<command>.+?)\s*$')

    if m:
        params.update(m.groupdict())

    return None, [TokenCommandMap(params), TokenEof()]
