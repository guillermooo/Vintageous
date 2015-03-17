

class Node(object):
    pass


class RangeNode(Node):
    def __init__(self,
            start_line=None,
            end_line=None,
            separator=None):
        self.start_line =  start_line or []
        self.end_line = end_line or []
        self.start_offset = []
        self.end_offset = []
        self.separator = separator

    def __repr__(self):
        return ('<{0}(start:{1}, end:{2}, loffset:{3}, roffset:{4}, separator:{5}]>'
            .format(self.__class__.__name__, self.start_line, self.end_line,
                self.start_offset, self.end_offset, self.separator))

    def __eq__(self, other):
        if not isinstance(other, RangeNode):
            return False
        return (self.start_line == other.start_line and
                self.end_line == other.end_line and
                self.separator == other.separator and
                self.start_offset == other.start_offset and
                self.end_offset == other.end_offset)


class CommandLineNode(Node):
    def __init__(self, line_range, command):
        # A RangeNode
        self.line_range = line_range
        # A TokenOfCommand
        self.command = command

    def __str__(self):
        return '{0}, {1}'.format(str(self.line_range), str(self.command))
