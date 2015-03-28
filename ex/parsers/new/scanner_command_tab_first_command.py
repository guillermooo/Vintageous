from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_TAB_FIRST_COMMAND
from .tokens_base import TokenOfCommand


class TokenTabFirstCommand(TokenOfCommand):
	def __init__(self, params, *args, **kwargs):
		super().__init__([],
						 TOKEN_COMMAND_XXX,
						 'xxx', *args, **kwargs)
		self.target_command = 'ex_xxx'


def scan_command_tab_first_command(state):
	raise NotImplementedError()
	
