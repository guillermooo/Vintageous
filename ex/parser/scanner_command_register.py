from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_REGISTERS
from .tokens_base import TokenOfCommand
from Vintageous import ex


@ex.command('registers', 'reg')
class TokenCommandRegisters(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                        TOKEN_COMMAND_REGISTERS,
                        'registers', *args, **kwargs)
        self.target_command = 'ex_list_registers'


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
