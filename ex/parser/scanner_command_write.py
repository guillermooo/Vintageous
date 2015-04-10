from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_WRITE
from .tokens_base import TokenOfCommand

from Vintageous.ex.ex_error import ERR_INVALID_ARGUMENT
from Vintageous.ex.ex_error import VimError
from Vintageous import ex


plus_plus_translations = {
    'ff': 'fileformat',
    'bin': 'binary',
    'enc': 'fileencoding',
    'nobin': 'nobinary',
}

@ex.command('write', 'w')
class TokenCommandWrite(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                        TOKEN_COMMAND_WRITE,
                        'write', *args, **kwargs)
        self.addressable = True
        self.target_command = 'ex_write_file'

    @property
    def options(self):
        return self.params['++']

    @property
    def target_file(self):
        return self.params['file_name']

    @property
    def appends(self):
        return self.params['>>']

    @property
    def command(self):
        return self.params['cmd']


def scan_command_write(state):

    params = {
        '++': '',
        'file_name': '',
        '>>': False,
        'cmd': '',
    }

    bang = state.consume()

    if bang == EOF:
        return None, [TokenCommandWrite(params), TokenEof()]

    if bang != '!':
        bang = False
        state.backup()

    state.skip(' ')
    state.ignore()

    while True:
        c = state.consume()

        if c == EOF:
            # TODO: forced?
            return None, [TokenCommandWrite(params, forced=bang), TokenEof()]

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

        if c == '>':
            state.expect('>')
            state.ignore()
            params ['>>'] = True
            state.match(r'.*$')
            params['file_name'] = state.emit().strip()
            continue

        if c == '!':
            state.ignore()
            state.match(r'.*$')
            params ['cmd'] = state.emit()
            continue

        if c != ' ':
            state.match(r'.*')
            params['file_name'] = state.emit().strip()

            state.skip(' ')
            state.ignore()

    state.expect(EOF)
    return None, [TokenCommandWrite (params, forced=bang == '!'), TokenEof ()]
