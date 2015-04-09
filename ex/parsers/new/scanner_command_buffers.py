from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_BUFFERS
from .tokens_base import TokenOfCommand

from Vintageous.ex.ex_error import ERR_INVALID_ARGUMENT
from Vintageous.ex.ex_error import VimError
from Vintageous.ex import register_ex_command


@register_ex_command('buffers', 'buffers')
@register_ex_command('files', 'files')
@register_ex_command('ls', 'ls')
class TokenCommandBuffers(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__({},
                        TOKEN_COMMAND_BUFFERS,
                        'write', *args, **kwargs)
        self.target_command = 'ex_prompt_select_open_file'


def scan_command_buffers(state):
    try:
        state.expect(EOF)
    except ValueError:
        raise VimError('trailing characters')

    return None, [TokenCommandBuffers(), TokenEof()]
