from .state import EOF
from .tokens import TokenEof
from .tokens_commands import TokenCommandSubstitute


def scan_command_substitute(state):
    delim = state.consume()

    if delim == EOF:
        return None, [TokenCommandSubstitute(None), TokenEof()]

    return scan_command_substitute_params(state)


def scan_command_substitute_params(state):
    state.backup()
    delim = state.consume()

    params = {
        "search_term": None,
        "replacement": None,
        "count": 1,
        "flags": [],
    }

    while True:
        c = state.consume()

        if c == delim:
            state.start += 1
            state.backup()
            params['search_term'] = state.emit()
            state.consume()
            break

        if c == EOF:
            raise ValueError("bad command: {0}".format(state.source))

    replacement = None
    while True:
        c = state.consume()

        if c == delim:
            state.start += 1
            state.backup()
            params['replacement'] = state.emit()
            state.consume()
            state.ignore()
            break

        if c == EOF:
            raise ValueError("bad command: {0}".format(state.source))

    if state.match(r'\s*[&cegiInp#lr]+'):
        params['flags'] = list(state.emit().strip())
        if '&' in params['flags'] and params['flags'][0] != '&':
            raise ValueError("bad command: {}".format(state.source))

    if state.peek(' '):
        state.skip(' ')
        state.ignore()
        if state.match(r'\d+'):
            params['count'] = int(state.emit())

    state.skip(' ')
    state.ignore()
    state.expect(EOF)
    return None, [TokenCommandSubstitute(params), TokenEof()]
