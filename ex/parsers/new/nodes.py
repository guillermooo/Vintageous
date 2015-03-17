from Vintageous.vi.utils import R
from Vintageous.vi.utils import first_sel
from Vintageous.vi.utils import row_at
from Vintageous.ex.parsers.new.tokens import TokenDot
from Vintageous.ex.parsers.new.tokens import TokenDigits
from Vintageous.ex.parsers.new.tokens import TokenPercent
from Vintageous.ex.parsers.new.tokens import TokenSearchForward
from Vintageous.ex.parsers.new.tokens import TokenOfSearch


class Node(object):
    pass


class RangeNode(Node):
    '''
    Represents a Vim line range.
    '''

    def __init__(self, start=None, end=None, separator=None, start_offset=None,
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

    @property
    def has_offsets(self):
        return bool(self.start_offset or self.end_offset)

    @property
    def is_empty(self):
        '''
        Indicates whether this range has ever been defined. For example, in
        interactive mode, if `true`, it means that the user hasn't provided
        any line range on the command line.
        '''
        return not any((self.start, self.end, self.has_offsets, self.separator))

    def resolve_notation(self, view, token, current=0):
        '''
        Returns a line number.
        '''
        if isinstance(token, TokenDot):
            sel = first_sel(view)
            return row_at(view, sel.b)

        if isinstance(token, TokenDigits):
            return max(int(str(token)) - 1, 0)

        if isinstance(token, TokenPercent):
            return row_at(view, view.size())

        if isinstance(token, TokenSearchForward):
            start_pt = view.text_point(current, 0)
            match = view.find(str(token), start_pt)
            if not match:
                # TODO: Convert this to a VimError or something like that.
                raise ValueError('pattern not found')
            return row_at(view, match.a)

        raise NotImplementedError()

    def resolve_line_reference(self, view, line_reference, current=0):
        '''
        Calculates the line offset determined by @line_reference.

        @view
          The view where the calculation is made.
        @line_reference
          The sequence of tokens defining the line range to be calculated.
        @current
          Line number where we are now.
        '''
        last = None
        for token in line_reference:
            # Make sure a search forward doesn't overlap with a match obtained
            # right before this search.
            if isinstance(last, TokenOfSearch) and isinstance(token, TokenOfSearch):
                if isinstance(token, TokenSearchForward):
                    current += 1

            current = self.resolve_notation(view, token, current)

            last = token

        return current

    def resolve(self, view):
        '''
        Returns a Sublime Text range representing the Vim line range that the
        ex command should operate on.
        '''
        start = self.resolve_line_reference(view, self.start or [TokenDot()])
        start += sum(self.start_offset)

        if not self.separator:
            if len(self.start) == 1 and isinstance(self.start[0], TokenPercent):
                return R(0, view.size())

            return view.full_line(view.text_point(start, 0))

        start = start if self.separator == ';' else 0
        end = self.resolve_line_reference(view, self.end or [TokenDot()], current=start)
        end += sum(self.end_offset)

        return R(start.begin(), end.end())


class CommandLineNode(Node):
    def __init__(self, line_range, command):
        # A RangeNode
        self.line_range = line_range
        # A TokenOfCommand
        self.command = command

    def __str__(self):
        return '{0}, {1}'.format(str(self.line_range), str(self.command))
