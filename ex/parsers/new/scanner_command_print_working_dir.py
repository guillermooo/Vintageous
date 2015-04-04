from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_PRINT_WORKING_DIR
from .tokens_base import TokenOfCommand


class TokenPrintWorkingDir(TokenOfCommand):
	def __init__(self, *args, **kwargs):
		super().__init__({},
						 TOKEN_COMMAND_PRINT_WORKING_DIR,
						 'pwd', *args, **kwargs)
		self.target_command = 'ex_print_working_dir'


def scan_command_print_working_dir(state):
    state.expect(EOF)
    return None, [TokenPrintWorkingDir(), TokenEof()]
