from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_QUIT_ALL_COMMAND
from .tokens_base import TokenOfCommand


class TokenQuitAllCommand(TokenOfCommand):
	def __init__(self, params, *args, **kwargs):
		super().__init__([],
						 TOKEN_COMMAND_XXX,
						 'xxx', *args, **kwargs)
		self.target_command = 'ex_xxx'


def scan_command_quit_all_command(state):
	raise NotImplementedError()
	
