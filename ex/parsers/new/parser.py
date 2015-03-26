from .nodes import CommandLineNode
from .nodes import RangeNode
from .parser_state import ParserState
from .scanner import Scanner
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
from .tokens_base import TokenOfCommand


def parse_ex_command(source):
    state = ParserState(source)
    parse_func = parse_line_ref
    command_line = CommandLineNode(None, None)
    while True:
        parse_func, command_line = parse_func(state, command_line)
        if parse_func is None:
            command_line.validate()
            return command_line


def init_line_range(command_line):
    if command_line.line_range:
        return
    command_line.line_range = RangeNode()


def parse_line_ref(state, command_line):
    token = state.next_token()

    if isinstance(token, TokenEof):
        return None, command_line

    if isinstance(token, TokenDot):
        init_line_range(command_line)
        return parse_line_ref_dot(state, command_line)

    if isinstance(token, TokenOffset):
        init_line_range(command_line)
        return parse_line_ref_offset(token, state, command_line)

    if isinstance(token, TokenSearchForward):
        init_line_range(command_line)
        return parse_line_ref_search_forward(token, state, command_line)

    if isinstance(token, TokenSearchBackward):
        init_line_range(command_line)
        return parse_line_ref_search_backward(token, state, command_line)

    if isinstance(token, TokenComma):
        init_line_range(command_line)
        command_line.line_range.separator = TokenComma()
        state.is_range_start_line_parsed = not state.is_range_start_line_parsed
        return parse_line_ref, command_line

    if isinstance(token, TokenSemicolon):
        init_line_range(command_line)
        command_line.line_range.separator = TokenSemicolon()
        state.is_range_start_line_parsed = True
        return parse_line_ref, command_line

    if isinstance(token, TokenDigits):
        init_line_range(command_line)
        return parse_line_ref_digits(token, state, command_line)

    if isinstance (token, TokenDollar):
        init_line_range(command_line)
        return parse_line_ref_dollar(token, state, command_line)

    if isinstance (token, TokenPercent):
        init_line_range(command_line)
        return parse_line_ref_percent(token, state, command_line)

    if isinstance (token, TokenMark):
        init_line_range(command_line)
        return parse_line_ref_mark(token, state, command_line)

    if isinstance (token, TokenOfCommand):
        init_line_range(command_line)
        command_line.command = token
        return None, command_line

    return None, command_line


def parse_line_ref_mark(token, state, command_line):
    if not state.is_range_start_line_parsed:
        command_line.line_range.start.append(token)
    else:
        command_line.line_range.end.append(token)
    return parse_line_ref, command_line


def parse_line_ref_percent(token, state, command_line):
    if not state.is_range_start_line_parsed:
        if command_line.line_range.start:
            raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        command_line.line_range.start.append(token)
    else:
        if command_line.line_range.end:
            raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        command_line.line_range.end.append(token)
    return parse_line_ref, command_line


def parse_line_ref_dollar(token, state, command_line):
    if not state.is_range_start_line_parsed:
        if command_line.line_range.start:
            raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        command_line.line_range.start.append(token)
    else:
        if command_line.line_range.end:
            raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        command_line.line_range.end.append(token)
    return parse_line_ref, command_line


def parse_line_ref_digits(token, state, command_line):
    if not state.is_range_start_line_parsed:
        if (command_line.line_range.start and
            command_line.line_range.start[-1]) == TokenDot():
            raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        elif (command_line.line_range.start and
            isinstance(command_line.line_range.start[-1], TokenDigits)):
            command_line.line_range.start = [token]
        else:
            command_line.line_range.start.append(token)
    else:
        if (command_line.line_range.end and
            command_line.line_range.end[-1] == TokenDot()):
                raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        elif (command_line.line_range.end and
            isinstance(command_line.line_range.end[-1], TokenDigits)):
            command_line.line_range.end = [token]
        else:
            command_line.line_range.end.append(token)
    return parse_line_ref, command_line


def parse_line_ref_search_forward(token, state, command_line):
    if not state.is_range_start_line_parsed:
        if command_line.line_range.start:
            command_line.line_range.start_offset = []
        command_line.line_range.start.append(token)
    else:
        if command_line.line_range.end:
            command_line.line_range.end_offset = []
        command_line.line_range.end.append(token)
    return parse_line_ref, command_line


def parse_line_ref_search_backward(token, state, command_line):
    if not state.is_range_start_line_parsed:
        if command_line.line_range.start:
            command_line.line_range.start_offset = []
        command_line.line_range.start.append(token)
    else:
        if command_line.line_range.end:
            command_line.line_range.end_offset = []
        command_line.line_range.end.append(token)
    return parse_line_ref, command_line


def parse_line_ref_offset(token, state, command_line):
    if not state.is_range_start_line_parsed:
        if (command_line.line_range.start and
            command_line.line_range.start[-1] == TokenDollar()):
                raise ValueError ('bad command line {}'.format(state.scanner.state.source))
        command_line.line_range.start.append(token)
    else:
        if (command_line.line_range.end and
            command_line.line_range.end[-1] == TokenDollar()):
                raise ValueError ('bad command line {}'.format(state.scanner.state.source))
        command_line.line_range.end.append(token)
    return parse_line_ref, command_line


def parse_line_ref_dot(state, command_line):
        init_line_range(command_line)
        if not state.is_range_start_line_parsed:
            if command_line.line_range.start and isinstance(command_line.line_range.start[-1], TokenOffset):
                raise ValueError('bad range {0}'.format(state.scanner.state.source))
            command_line.line_range.start.append(TokenDot())
        else:
            if command_line.line_range.end and isinstance(command_line.line_range.end[-1], TokenOffset):
                raise ValueError('bad range {0}'.format(state.scanner.source))
            command_line.line_range.end.append(TokenDot())

        return parse_line_ref, command_line
