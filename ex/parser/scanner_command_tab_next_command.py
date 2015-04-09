from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_TAB_NEXT_COMMAND
from .tokens_base import TokenOfCommand
from Vintageous.ex import register_ex_command


@register_ex_command('tabnext', 'tabn')
class TokenTabNextCommand(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__([],
                         TOKEN_COMMAND_TAB_NEXT_COMMAND,
                         'tabnext', *args, **kwargs)
        self.target_command = 'ex_tabnext'


def scan_command_tab_next_command(state):
    c = state.consume()

    if c == EOF:
        return None, [TokenTabNextCommand(), TokenEof()]

    bang = c == '!'
    return None, [TokenTabNextCommand(forced=bang), TokenEof()]
