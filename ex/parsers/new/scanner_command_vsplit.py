from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_VSPLIT
from .tokens_base import TokenOfCommand

from Vintageous.ex.ex_error import ERR_INVALID_ARGUMENT
from Vintageous.ex.ex_error import VimError
from Vintageous.ex import register_ex_command


@register_ex_command('vsplit', 'vs')
class TokenCommandVsplit(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                        TOKEN_COMMAND_VSPLIT,
                        'vsplit', *args, **kwargs)
        self.target_command = 'ex_vsplit'


def scan_command_vsplit(state):
    state.skip(' ')
    state.ignore()

    params = {
        'file_name': None
    }

    if state.consume() == EOF:
        return None, [TokenCommandVsplit(params), TokenEof()]

    state.backup()

    params['file_name'] = state.match(r'.+$').group(0).strip()

    return None, [TokenCommandVsplit(params), TokenEof()]
