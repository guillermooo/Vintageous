from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_WRITE_AND_QUIT_COMMAND
from .tokens_base import TokenOfCommand
from Vintageous.ex import register_ex_command


plus_plus_translations = {
    'ff': 'fileformat',
    'bin': 'binary',
    'enc': 'fileencoding',
    'nobin': 'nobinary',
}


@register_ex_command('wq', 'wq')
class TokenWriteAndQuitCommand(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_WRITE_AND_QUIT_COMMAND,
                         'wq', *args, **kwargs)
        self.target_command = 'ex_write_and_quit'


def scan_command_write_and_quit_command(state):
    params = {
        '++': None,
        'file': None,
    }

    c = state.consume()

    if c == EOF:
        return None, [TokenWriteAndQuitCommand(params), TokenEof()]

    bang == c == '!'

    if not bang:
        state.backup()

    c = state.consume()

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
        raise NotImplementedError('param not implemented')

    if c == EOF:
        return None, [TokenWriteAndQuitCommand(params), TokenEof()]

    m = state.expect_match(r'.+$')
    params['file'] = m.group(0).strip()

    return None, [TokenWriteAndQuitCommand(params), TokenEof()]
