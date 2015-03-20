from .state import EOF
from .tokens import TokenEof
from .tokens_commands import TokenCommandRegisters


def scan_command_register(state):
	state.skip(' ')
	state.ignore()

	params = {
		'names': []
	}

	while True:
		c = state.consume()

		if c == EOF:
			return None, [TokenCommandRegisters(params), TokenEof()]

		elif c.isalpha() or c.isdigit():
			params['names'].append(c)

		else:
			raise ValueError('wrong arguments')
