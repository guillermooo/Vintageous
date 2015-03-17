

class Node(object):
    pass


class RangeNode(Node):
    def __init__(self,
            start=None,
            end=None,
            separator=None,
            start_offset=None,
            end_offset=None):
        self.start =  start or []
        self.end = end or []
        self.start_offset = start_offset or []
        self.end_offset = end_offset or []
        self.separator = separator

    def __repr__(self):
        return ('<{0}(start:{1}, end:{2}, loffset:{3}, roffset:{4}, separator:{5}]>'
            .format(self.__class__.__name__, self.start, self.end,
                self.start_offset, self.end_offset, self.separator))

    def __eq__(self, other):
        if not isinstance(other, RangeNode):
            return False
        return (self.start == other.start and
                self.end == other.end and
                self.separator == other.separator and
                self.start_offset == other.start_offset and
                self.end_offset == other.end_offset)

    def to_json(self):
        return {
            'start': [str(item) for item in self.start],
            'end': [str(item) for item in self.end],
            'separator': str(self.separator) if self.separator else None,
            'start_offset': [int(item) for item in self.start_offset],
            'end_offset': [int(item) for item in self.end_offset],
        }



class CommandLineNode(Node):
    def __init__(self, line_range, command):
        # A RangeNode
        self.line_range = line_range
        # A TokenOfCommand
        self.command = command

    def __str__(self):
        return '{0}, {1}'.format(str(self.line_range), str(self.command))
