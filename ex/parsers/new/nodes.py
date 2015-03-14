

class Node(object):
    pass


class RangeNode(Node):
    def __init__(self,
            start_line=None,
            end_line=None,
            must_recompute_start_line=False):
        self.start_line =  start_line or []
        self.end_line = end_line or []
        self.must_recompute_start_line = must_recompute_start_line
        self.start_offset = []
        self.end_offset = []
        self.separator = None

    def __repr__(self):
        return ('<{0}(start:{1}, end:{2}, loffset:{3}, roffset:{4}, semicolon:{5}]>'
            .format(self.__class__.__name__, self.start_line, self.end_line,
                self.start_offset, self.end_offset, self.must_recompute_start_line))

    def __eq__(self, other):
        if not isinstance(other, RangeNode):
            return False
        return (self.start_line == other.start_line and
                self.end_line == other.end_line and
                self.separator == other.separator and
                self.start_offset == other.start_offset and
                self.end_offset == other.end_offset)


# TODO: remove this
class CommandNode(Node):
    def __init__(self, command_token):
        self.name = command_token.content
        self.arguments = command_token.params
        self.flags = command_token.params.get('flags', [])
        self.count = command_token.params.get('count', 1)


class CommandLineNode(Node):
    def __init__(self, line_range, command):
        # A RangeNode
        self.line_range = line_range
        # A TokenOfCommand
        self.command = command

    def __str__(self):
        return '{0}, {1}'.format(str(self.line_range), str(self.command))
