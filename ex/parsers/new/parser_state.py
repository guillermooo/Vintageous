from .scanner import Scanner
from .nodes import CommandLineNode
from .nodes import RangeNode


class ParserState(object):
    def __init__(self, source):
        self.scanner = Scanner(source)
        self.is_range_start_line_parsed = False
        range_node = RangeNode()
        self.command_line = CommandLineNode(None, None)

    def next_token(self):
        return next(self.scanner.scan())