from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_COPY
from .tokens_base import TokenOfCommand
from .parser import parse_ex_command
from Vintageous import ex


@ex.command('copy', 'co')
class TokenCopy(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_COPY,
                         'copy', *args, **kwargs)
        self.addressable = True
        self.target_command = 'ex_copy'

    @property
    def address(self):
        return self.params['address']

    def calculate_address(self):
        # TODO: must calc only the first line ref?
        calculated = parse_ex_command(self.address)
        if calculated is None:
            return None

        assert calculated.command is None, 'bad address'
        assert calculated.line_range.separator is None, 'bad address'

        return calculated.line_range


def scan_command_copy(state):
    params = {
        'address': None
    }

    m = state.expect_match(r'\s*(?P<address>.+?)\s*$')
    params.update(m.groupdict())

    return None, [TokenCopy(params), TokenEof()]
