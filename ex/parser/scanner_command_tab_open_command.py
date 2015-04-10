from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_TAB_OPEN_COMMAND
from .tokens_base import TokenOfCommand


class TokenTabOpenCommand(TokenOfCommand):
	def __init__(self, params, *args, **kwargs):
		super().__init__([],
						 TOKEN_COMMAND_XXX,
						 'xxx', *args, **kwargs)
		self.target_command = 'ex_xxx'


def scan_command_tab_open_command(state):
	raise NotImplementedError()
	
