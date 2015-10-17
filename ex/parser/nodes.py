from Vintageous.ex.ex_error import ERR_NO_RANGE_ALLOWED
from Vintageous.ex.ex_error import VimError
from Vintageous.ex.parser.tokens import TokenDigits
from Vintageous.ex.parser.tokens import TokenDollar
from Vintageous.ex.parser.tokens import TokenDot
from Vintageous.ex.parser.tokens import TokenMark
from Vintageous.ex.parser.tokens import TokenOffset
from Vintageous.ex.parser.tokens import TokenOfSearch
from Vintageous.ex.parser.tokens import TokenPercent
from Vintageous.ex.parser.tokens import TokenSearchBackward
from Vintageous.ex.parser.tokens import TokenSearchForward
from Vintageous.vi.search import reverse_search_by_pt
from Vintageous.vi.utils import first_sel
from Vintageous.vi.utils import R
from Vintageous.vi.utils import row_at


class Node(object):
    pass


class RangeNode(Node):
    '''
    Represents a Vim line range.
    '''

    def __init__(self, start=None, end=None, separator=None):
        self.start =  start or []
        self.end = end or []
        self.separator = separator

    def __str__(self):
        return '{0}{1}{2}'.format(
            ''.join(str(x) for x in self.start),
            str(self.separator) if self.separator else '',
            ''.join(str(x) for x in self.end),
            )

    def __rpr__(self):
        return ('RangeNode<{0}(start:{1}, end:{2}, separator:{3}]>'
            .format(self.__class__.__name__, self.start, self.end, self.separator))

    def __eq__(self, other):
        if not isinstance(other, RangeNode):
            return False
        return (self.start == other.start and
                self.end == other.end and
                self.separator == other.separator)

    @property
    def is_empty(self):
        '''
        Indicates whether this range has ever been defined. For example, in
        interactive mode, if `true`, it means that the user hasn't provided
        any line range on the command line.
        '''
        return not any((self.start, self.end, self.separator))

    def resolve_notation(self, view, token, current):
        '''
        Returns a line number.
        '''
        if isinstance(token, TokenDot):
            pt = view.text_point(current, 0)
            return row_at(view, pt)

        if isinstance(token, TokenDigits):
            return max(int(str(token)) - 1, -1)

        if isinstance(token, TokenPercent):
            return row_at(view, view.size())

        if isinstance(token, TokenDollar):
            return row_at(view, view.size())

        if isinstance(token, TokenOffset):
            return current + sum(token.content)

        if isinstance(token, TokenSearchForward):
            start_pt = view.text_point(current, 0)
            match = view.find(str(token)[1:-1], start_pt)
            if not match:
                # TODO: Convert this to a VimError or something like that.
                raise ValueError('pattern not found')
            return row_at(view, match.a)

        if isinstance(token, TokenSearchBackward):
            start_pt = view.text_point(current, 0)
            match = reverse_search_by_pt(view, str(token)[1:-1], 0, start_pt)
            if not match:
                # TODO: Convert this to a VimError or something like that.
                raise ValueError('pattern not found')
            return row_at(view, match.a)

        if isinstance(token, TokenMark):
            return self.resolve_mark(view, token)

        raise NotImplementedError()

    def resolve_mark(self, view, token):
        if token.content == '<':
            sel = list(view.sel())[0]
            view.sel().clear()
            view.sel().add(sel)
            if sel.a < sel.b:
                return row_at(view, sel.a)
            else:
                return row_at(view, sel.a - 1)

        if token.content == '>':
            sel = list(view.sel())[0]
            view.sel().clear()
            view.sel().add(sel)
            if sel.a < sel.b:
                return row_at(view, sel.b - 1)
            else:
                return row_at(view, sel.b)

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
        last_token = None
        # XXX: what happens if there is no selection in the view?
        current = row_at(view, first_sel(view).b)
        for token in line_reference:
            # Make sure a search forward doesn't overlap with a match obtained
            # right before this search.
            if isinstance(last_token, TokenOfSearch) and isinstance(token, TokenOfSearch):
                if isinstance(token, TokenSearchForward):
                    current += 1

            current = self.resolve_notation(view, token, current)

            last_token = token

        return current

    def resolve(self, view):
        '''
        Returns a Sublime Text range representing the Vim line range that the
        ex command should operate on.
        '''
        start = self.resolve_line_reference(view, self.start or [TokenDot()])

        if not self.separator:
            if start == -1:
                return R(-1, -1)

            if len(self.start) == 1 and isinstance(self.start[0], TokenPercent):
                return R(0, view.size())

            return view.full_line(view.text_point(start, 0))

        new_start = start if self.separator == ';' else 0
        end = self.resolve_line_reference(view, self.end or [TokenDot()], current=new_start)

        return view.full_line(R(view.text_point(start, 0), view.text_point(end, 0)))


class CommandLineNode(Node):
    def __init__(self, line_range, command):
        # A RangeNode
        self.line_range = line_range
        # A TokenOfCommand
        self.command = command

    def __str__(self):
        return '{0}, {1}'.format(str(self.line_range), str(self.command))

    def validate(self):
        '''
        Raises an error for known conditions.
        '''
        if not (self.command and self.line_range):
            return

        if not self.command.addressable and not self.line_range.is_empty:
            raise VimError(ERR_NO_RANGE_ALLOWED)
