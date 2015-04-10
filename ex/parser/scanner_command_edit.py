from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_EDIT
from .tokens_base import TokenOfCommand

from Vintageous.ex.ex_error import ERR_INVALID_ARGUMENT
from Vintageous import ex


plus_plus_translations = {
    'ff': 'fileformat',
    'bin': 'binary',
    'enc': 'fileencoding',
    'nobin': 'nobinary',
}


@ex.command('edit', 'e')
class TokenEdit(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_EDIT,
                         'edit', *args, **kwargs)
        self.target_command = 'ex_edit'

    @property
    def plusplus(self):
        return self.params ['++']

    @property
    def command(self):
        return self.params ['cmd']

    @property
    def file_name(self):
        return self.params ['file_name']

    @property
    def count(self):
        return self.params ['count']


def scan_command_edit(state):
    params = {
        '++': None,
        'cmd': None,
        'file_name': None,
        'count': None,
    }

    c = state.consume()

    if c == EOF:
        return None, [TokenEdit(params), TokenEof()]

    bang = c == '!'
    if not bang:
        state.backup()

    while True:
        c = state.consume()

        if c == EOF:
            return None, [TokenEdit(params, forced=bang), TokenEof()]

        if c == '+':
            k = state.consume()

            if k == '+':
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
                continue

            state.backup()
            state.ignore()
            state.expect_match(r'.+$')
            params['cmd'] = state.emit()
            raise NotImplementedError('param not implemented')
            continue

        if c != ' ':
            state.match(r'.*')
            params['file_name'] = state.emit().strip()

            state.skip(' ')
            state.ignore()
            continue

        if c == '#':
            state.ignore()
            m = state.expect_match(r'\d+')
            params['count'] = m.group(0)
            raise NotImplementedError('param not implemented')
            continue

    return None, [TokenEdit(params, forced=bang), TokenEof()]
