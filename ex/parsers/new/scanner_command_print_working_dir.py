from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_PRINT_WORKING_DIR
from .tokens_base import TokenOfCommand


class TokenPrintWorkingDir(TokenOfCommand):
	def __init__(self, params, *args, **kwargs):
		super().__init__([],
						 TOKEN_COMMAND_XXX,
						 'xxx', *args, **kwargs)
		self.target_command = 'ex_xxx'


def scan_command_print_working_dir(state):
	raise NotImplementedError()
	
