from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_WRITE_AND_QUIT_ALL
from .tokens_base import TokenOfCommand

from Vintageous import ex
from Vintageous.ex.ex_error import ERR_INVALID_ARGUMENT
from Vintageous.ex.ex_error import VimError


plus_plus_translations = {
    'ff': 'fileformat',
    'bin': 'binary',
    'enc': 'fileencoding',
    'nobin': 'nobinary',
}


@ex.command('wqall', 'wqa')
@ex.command('xall', 'xa')
class TokenCommandWriteAndQuitAll(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                        TOKEN_COMMAND_WRITE_AND_QUIT_ALL,
                        'wqall', *args, **kwargs)
        self.addressable = True
        self.target_command = 'ex_write_and_quit_all'

    @property
    def options(self):
        return self.params['++']


def scan_command_write_and_quit_all(state):
    params = {
        '++': '',
    }

    state.skip(' ')
    state.ignore()

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

    state.expect(EOF)
    return None, [TokenCommandWriteAndQuitAll(params), TokenEof()]
