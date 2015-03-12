from .nodes import CommandLineNode
from .nodes import CommandNode
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
from .tokens_commands import TokenOfCommand


def start_parsing(source):
    state = ParserState(source)
    parse_func = parse_line_ref
    command_line = CommandLineNode(None, None)
    while True:
        parse_func, command_line = parse_func(state, command_line)
        if parse_func is None:
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
        command_line.line_range.right_hand_side = not command_line.line_range.right_hand_side
        return parse_line_ref, command_line

    if isinstance(token, TokenSemicolon):
        init_line_range(command_line)
        command_line.line_range.right_hand_side = True
        command_line.line_range.must_recompute_start_line = True
        return parse_line_ref, command_line

    if isinstance(token, TokenDigits):
        init_line_range(command_line)
        return parse_line_ref_digits(token, state, command_line)

    if isinstance (token, TokenDollar):
        init_line_range(command_line)
        return parse_line_ref_dollar(token, state, command_line)

    if isinstance (token, TokenMark):
        init_line_range(command_line)
        return parse_line_ref_mark(token, state, command_line)

    if isinstance (token, TokenOfCommand):
        init_line_range(command_line)
        command_line.command = token
        return None, command_line

    return None, command_line


def parse_line_ref_mark(token, state, command_line):
    if not command_line.line_range.right_hand_side:
        command_line.line_range.start_line.append(token)
    else:
        command_line.line_range.end_line.append(token)
    return parse_line_ref, command_line


def parse_line_ref_dollar(token, state, command_line):
    if not command_line.line_range.right_hand_side:
        if command_line.line_range.start_line:
            raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        command_line.line_range.start_line.append(token)
    else:
        if command_line.line_range.end_line:
            raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        command_line.line_range.end_line.append(token)
    return parse_line_ref, command_line


def parse_line_ref_digits(token, state, command_line):
    if not command_line.line_range.right_hand_side:
        if (command_line.line_range.start_line and
            command_line.line_range.start_line[-1]) == TokenDot():
            raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        elif (command_line.line_range.start_line and
            isinstance(command_line.line_range.start_line[-1], TokenDigits)):
            command_line.line_range.start_line = [token]
        else:
            command_line.line_range.start_line.append(token)
    else:
        if (command_line.line_range.end_line and
            command_line.line_range.end_line[-1] == TokenDot()):
                raise ValueError('bad range: {0}'.format(state.scanner.state.source))
        elif (command_line.line_range.end_line and
            isinstance(command_line.line_range.end_line[-1], TokenDigits)):
            command_line.line_range.end_line = [token]
        else:
            command_line.line_range.end_line.append(token)
    return parse_line_ref, command_line


def parse_line_ref_search_forward(token, state, command_line):
    if not command_line.line_range.right_hand_side:
        if command_line.line_range.start_line:
            command_line.line_range.start_offset = []
        command_line.line_range.start_line.append(token)
    else:
        if command_line.line_range.end_line:
            command_line.line_range.end_offset = []
        command_line.line_range.end_line.append(token)
    return parse_line_ref, command_line


def parse_line_ref_search_backward(token, state, command_line):
    if not command_line.line_range.right_hand_side:
        if command_line.line_range.start_line:
            command_line.line_range.start_offset = []
        command_line.line_range.start_line.append(token)
    else:
        if command_line.line_range.end_line:
            command_line.line_range.end_offset = []
        command_line.line_range.end_line.append(token)
    return parse_line_ref, command_line


def parse_line_ref_offset(token, state, command_line):
    if not command_line.line_range.right_hand_side:
        if (command_line.line_range.start_line and
            command_line.line_range.start_line[-1] == TokenDollar()):
                raise ValueError ('bad command line {}'.format (state.scanner.state.source))
        command_line.line_range.start_offset.extend(token.content)
    else:
        if (command_line.line_range.end_line and
            command_line.line_range.end_line[-1] == TokenDollar()):
                raise ValueError ('bad command line {}'.format (state.scanner.state.source))
        command_line.line_range.end_offset.extend(token.content)
    return parse_line_ref, command_line


def parse_line_ref_dot(state, command_line):
        init_line_range(command_line)
        if not command_line.line_range.right_hand_side:
            if command_line.line_range.start_offset:
                raise ValueError('bad range {0}'.format(state.scanner.state.source))
            command_line.line_range.start_line.append(TokenDot())
        else:
            if command_line.line_range.end_offset:
                raise ValueError('bad range {0}'.format(state.scanner.source))
            command_line.line_range.end_line.append(TokenDot())

        return parse_line_ref, command_line
