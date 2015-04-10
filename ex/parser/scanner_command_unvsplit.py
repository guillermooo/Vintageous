from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_UNVSPLIT
from .tokens_base import TokenOfCommand

from Vintageous.ex.ex_error import ERR_INVALID_ARGUMENT
from Vintageous.ex.ex_error import VimError
from Vintageous import ex


@ex.command('unvsplit', 'unvsplit')
class TokenCommandUnvsplit(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__({},
                        TOKEN_COMMAND_UNVSPLIT,
                        'vsplit', *args, **kwargs)
        self.target_command = 'ex_unvsplit'


def scan_command_unvsplit(state):
    state.expect(EOF)
    return None, [TokenCommandUnvsplit(), TokenEof()]
