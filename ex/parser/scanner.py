'''
Tokenization for the Vim command line.
'''

from Vintageous.ex.ex_error import ERR_UNKNOWN_COMMAND
from Vintageous.ex.ex_error import VimError

from . import subscanners
from .state import EOF
from .state import ScannerState
from .tokens import TokenComma
from .tokens import TokenDigits
from .tokens import TokenDollar
from .tokens import TokenDot
from .tokens import TokenEof
from .tokens import TokenMark
from .tokens import TokenOffset
from .tokens import TokenPercent
from .tokens import TokenSearchBackward
from .tokens import TokenSearchForward
from .tokens import TokenSemicolon


# TODO: make this a function. We don't need state.
class Scanner(object):
    '''
    Produces ex command-line tokens from a string.
    '''
    def __init__(self, source):
        self.state = ScannerState(source)

    def scan(self):
        '''
        Generates ex command-line tokens for `source`.

        The scanner works its way through the source string by passing the
        current state to the next scanning function.
        '''
        next_func = scan_range
        while True:
            # We return multiple tokens so that we can work around cyclic imports:
            # functions that need to, return TokenEof without having to call
            # a function in this module from a separate module.
            #
            # Keep scanning while we get a scanning function.
            (next_func, items) = next_func(self.state)
            yield from items
            if not next_func:
                break


def scan_range(state):
    '''
    Produces tokens found in a command line range.

    http://vimdoc.sourceforge.net/htmldoc/cmdline.html#cmdline-ranges
    '''
    c = state.consume()

    if c == EOF:
        return None, [TokenEof()]

    if c == '.':
        state.emit()
        return scan_range, [TokenDot()]

    if c == '$':
        state.emit()
        return scan_range, [TokenDollar()]

    if c in ',;':
        token = TokenComma if c == ',' else TokenSemicolon
        state.emit()
        return scan_range, [token()]

    if c == "'":
        return scan_mark(state)

    if c in '/?':
        return scan_search(state)

    if c in '+-':
        return scan_offset(state)

    if c == '%':
        state.emit()
        return scan_range, [TokenPercent()]

    if c in '\t ':
        state.skip_run(' \t')
        state.ignore()

    if c.isdigit():
        return scan_digits(state)

    state.backup()
    return scan_command, []


def scan_mark(state):
    c = state.expect_match(r'[a-zA-Z\[\]()<>]')
    return scan_range, [TokenMark(c.group(0))]


def scan_digits(state):
    while True:
        c = state.consume()
        if not c.isdigit():
            if c == EOF:
                return None, [TokenDigits(state.emit()), TokenEof()]
            state.backup()
            break
    return scan_range, [TokenDigits(state.emit())]


def scan_search(state):
    delim = state.source[state.position - 1]
    while True:
        c = state.consume()

        if c == delim:
            state.start += 1
            state.backup()
            content = state.emit()
            state.consume()
            token = TokenSearchForward if c == '/' else TokenSearchBackward
            return scan_range , [token(content)]

        elif c == EOF:
            raise ValueError('unclosed search pattern: {0}'.format(state.source))


def scan_offset(state):
    offsets = []
    to_int = lambda x: int(x, 10)
    sign = '-' if state.source[state.position - 1] == '-' else ''

    digits = state.expect_match(r'\s*(\d+)')
    offsets.append(sign + digits.group(1))

    while True:
        c = state.consume()

        if c == EOF:
            state.ignore()
            return None, [TokenOffset(list(map(to_int, offsets))), TokenEof()]

        if c == '+' or c == '-':
            digits = state.expect_match(r'\s*(\d+)')
            sign = '-' if state.source[state.position - 1] == '-' else ''
            offsets.append(sign + digits.group(1))
            continue

        if not c.isdigit():
            state.backup()
            state.ignore()
            return scan_range, [TokenOffset(list(map(to_int, offsets)))]


def scan_command(state):
    for (pattern, subscanner) in subscanners.patterns.items():
        if state.match(pattern):
            state.ignore()
            return subscanner(state)

    state.expect(EOF, lambda: VimError(ERR_UNKNOWN_COMMAND))
    return None, [TokenEof()]
