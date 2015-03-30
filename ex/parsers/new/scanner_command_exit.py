from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_EXIT
from .tokens_base import TokenOfCommand


class TokenCommandExit(TokenOfCommand):
	def __init__(self, params, *args, **kwargs):
		super().__init__(params,
						 TOKEN_COMMAND_EXIT,
						 'exit', *args, **kwargs)
		self.addressable = True
		self.target_command = 'ex_exit'


def scan_command_exit(state):
    params = {
        'file_name': '',
    }

    bang = state.consume()

    if bang == EOF:
        return None, [TokenCommandExit(params), TokenEof()]

    bang = bang == '!'
    if not bang:
        state.backup()

    state.skip(' ')
    state.ignore()

    while True:
        c = state.consume()

        if c == EOF:
            return None, [TokenCommandExit(params, forced=bang), TokenEof()]

        if c == '+':
            state.expect('+')
            state.ignore()
            # TODO: expect_match should work with emit()
            # http://vimdoc.sourceforge.net/htmldoc/editing.html#[++opt]
            m = state.expect_match(
                    r'(?:f(?:ile)?f(?:ormat)?|(?:file)?enc(?:oding)?|(?:no)?bin(?:ary)?|bad|edit)(?=\s|$)',
                    lambda: VimError(ERR_INVALID_ARGUMENT))
            name = m.group(0)
            params['++'] = plus_plus_translations.get(name, name)
            state.ignore()
            continue

        if c != ' ':
            state.match(r'.*')
            params['file_name'] = state.emit().strip()
            state.skip(' ')
            state.ignore()

    state.expect(EOF)
    return None, [TokenCommandExit (params, forced=bang == '!'), TokenEof ()]