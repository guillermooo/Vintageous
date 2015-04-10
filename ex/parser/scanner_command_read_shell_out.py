from Vintageous.ex.ex_error import VimError
from Vintageous.ex.ex_error import ERR_INVALID_ARGUMENT

from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_READ_SHELL_OUT
from .tokens_base import TokenOfCommand
from Vintageous import ex


plus_plus_translations = {
    'ff': 'fileformat',
    'bin': 'binary',
    'enc': 'fileencoding',
    'nobin': 'nobinary',
}


@ex.command('read', 'r')
class TokenReadShellOut(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_READ_SHELL_OUT,
                         'read', *args, **kwargs)
        self.target_command = 'ex_read_shell_out'

    @property
    def command(self):
        return self.params['cmd']

    @property
    def file_name(self):
        return self.params['file_name']

    @property
    def plusplus(self):
        return self.params['++']


def scan_command_read_shell_out(state):
    params = {
        'cmd': None,
        '++': [],
        'file_name': None,
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
        raise NotImplementedError('++opt not implemented')

    elif c == '!':
        m = state.match(r'(?P<cmd>.+)')
        params.update(m.groupdict())

    else:
        state.backup()
        m = state.match(r'(?P<file_name>.+)$')
        params.update(m.groupdict())

    state.expect(EOF)

    return None, [TokenReadShellOut(params), TokenEof()]
