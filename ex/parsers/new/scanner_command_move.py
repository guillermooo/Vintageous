from .parser import parse_ex_command
from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_MOVE
from .tokens_base import TokenOfCommand


class TokenMove(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_MOVE,
                         'move', *args, **kwargs)
        self.addressable = True
        self.target_command = 'ex_move'

    @property
    def address(self):
        return self.params['address']


def scan_command_move(state):
    params = {
        'address': None
    }

    state.skip (' ')
    state.ignore()

    m = state.match(r'(?P<address>.*$)')
    if m:
        address_command_line = m.group(0).strip() or '.'
        params['address'] = parse_ex_command(address_command_line).line_range

    return None, [TokenMove(params), TokenEof()]


