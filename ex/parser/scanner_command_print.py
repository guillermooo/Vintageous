from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_PRINT
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('print', 'p')
class TokenCommandPrint(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_PRINT,
                         'print', *args, **kwargs)
        self.addressable = True
        self.cooperates_with_global = True
        self.target_command = 'ex_print'

    def __str__(self):
        return "{0} {1} {2}".format(self.content, ''.join(self.flags), self.count).strip()

    @property
    def count(self):
        return self.params['count']

    @property
    def flags(self):
        return self.params['flags']


def scan_command_print(state):
    params = {
        'count': '',
        'flags': [],
    }

    while True:
        c = state.consume()

        state.skip(' ')
        state.ignore()

        if c == EOF:
            return None, [TokenCommandPrint(params), TokenEof()]

        if c.isdigit():
            state.match(r'\d*')
            params['count'] = state.emit()
            continue

        m = state.expect_match(r'[l#p]+')
        params['flags'] = list(m.group(0))
        state.ignore()
        state.expect(EOF)
        break

    return None, [TokenCommandPrint(params), TokenEof()]
