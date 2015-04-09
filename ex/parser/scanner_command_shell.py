from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_SHELL
from .tokens_base import TokenOfCommand
from Vintageous.ex import register_ex_command


@register_ex_command('shell', 'shell')
class TokenShell(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__({},
                         TOKEN_COMMAND_SHELL,
                         'shell', *args, **kwargs)
        self.target_command = 'ex_shell'


def scan_command_shell(state):
    state.expect(EOF)
    return None, [TokenShell(), TokenEof()]
