from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_CDD_COMMAND
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('cdd', 'cdd')
class TokenCddCommand(TokenOfCommand):
	def __init__(self, *args, **kwargs):
		super().__init__({},
						 TOKEN_COMMAND_CDD_COMMAND,
						 'cdd', *args, **kwargs)
		self.target_command = 'ex_cdd'


def scan_command_cdd_command(state):
	c = state.consume()

	if c == EOF:
		return None, [TokenCddCommand(), TokenEof()]

	bang = c == '!'
	if not bang:
		state.backup()

	state.expect(EOF)

	return None, [TokenCddCommand(forced=bang), TokenEof()]
