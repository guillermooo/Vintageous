from .state import EOF
from .tokens import TokenEof
from .tokens_commands import TokenCommandWrite


plus_plus_translations = {
    'ff': 'fileformat',
    'bin': 'binary',
    'enc': 'fileencoding',
    'nobin': 'nobinary',
}


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
            m = state.expect_match(r'(?:f(?:ile)?f(?:ormat)?|(?:file)?enc(?:oding)?|(?:no)?bin(?:ary)?|bad|edit)(?=\s|$)')
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
