from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_DOUBLE_AMPERSAND
from .tokens_base import TokenOfCommand
from Vintageous.ex import register_ex_command


@register_ex_command('&&', '&&')
class TokenDoubleAmpersand(TokenOfCommand):
	def __init__(self, params, *args, **kwargs):
		super().__init__(params,
						 TOKEN_COMMAND_DOUBLE_AMPERSAND,
						 '&&', *args, **kwargs)
		self.addressable = True
		self.target_command = 'ex_double_ampersand'


def scan_command_double_ampersand(state):
	params = {
		'flags': [],
		'count': '',
	}

	m = state.match(r'\s*([cgr])*\s*(\d*)\s*$')
	params['flags'] = list(m.group(1)) if m.group(1) else []
	params['count'] = m.group(2) or ''

	state.expect(EOF)

	return None, [TokenDoubleAmpersand(params), TokenEof()]
