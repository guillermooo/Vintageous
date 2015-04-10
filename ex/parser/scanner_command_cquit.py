from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_CQUIT
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('cquit', 'cq')
class TokenCquit(TokenOfCommand):
	def __init__(self, *args, **kwargs):
		super().__init__({},
						 TOKEN_COMMAND_CQUIT,
						 'cquit', *args, **kwargs)
		self.target_command = 'ex_cquit'


def scan_command_cquit(state):
	state.expect(EOF)

	return None, [TokenCquit(), TokenEof()]

