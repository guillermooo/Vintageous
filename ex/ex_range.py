"""helpers to manage :ex mode ranges
"""

from collections import namedtuple
import sublime


class VimRange(object):
    """Encapsulates calculation of view regions based on supplied raw range info.
    """
    def __init__(self, view, range_info, default=None):
        self.view = view
        self.default = default
        self.range_info = range_info

    def blocks(self):
        """Returns a list of blocks potentially encompassing multiple lines.
        Returned blocks don't end in a newline char.
        """
        regions, visual_regions = new_calculate_range(self.view, self.range_info)
        blocks = []
        for a, b in regions:
            r = sublime.Region(self.view.text_point(a - 1, 0),
                               self.view.line(self.view.text_point(b - 1, 0)).end())
            if self.view.substr(r) == '':
                pass
            elif self.view.substr(r)[-1] == "\n":
                if r.begin() != r.end():
                    r = sublime.Region(r.begin(), r.end() - 1)
            blocks.append(r)
        return blocks

    def lines(self):
        """Return a list of lines.
        Returned lines don't end in a newline char.
        """
        lines = []
        for block in self.blocks():
            lines.extend(self.view.split_by_newlines(block))
        return lines


EX_RANGE = namedtuple('ex_range', 'left left_offset separator right right_offset')


def calculate_relative_ref(view, where, start_line=None):
    if where == '$':
        return view.rowcol(view.size())[0] + 1
    if where == '.':
        if start_line:
            return view.rowcol(view.text_point(start_line, 0))[0] + 1
        return view.rowcol(view.sel()[0].begin())[0] + 1


def new_calculate_search_offsets(view, searches, start_line):
    last_line = start_line
    for search in searches:
        if search[0] == '/':
            last_line = ex_location.search(view, search[1], start_line=last_line)
        elif search[0] == '?':
            end = view.line(view.text_point(start_line, 0)).end()
            last_line = ex_location.reverse_search(view, search[1], end=end)
        last_line += search[2]
    return last_line


def calculate_address(view, a):
    fake_range = dict(left_ref=a['ref'],
                      left_offset=a['offset'],
                      left_search_offsets=a['search_offsets'],
                      sep=None,
                      right_ref=None,
                      right_offset=None,
                      right_search_offsets=[]
                      # todo: 'text_range' key missing
                    )

    a, _ =  new_calculate_range(view, fake_range)[0][0] or -1
    # FIXME: 0 should be a valid address?
    if not (0 < a <= view.rowcol(view.size())[0] + 1):
        return None
    return a - 1


def new_calculate_range(view, r):
    """Calculates line-based ranges (begin_row, end_row) and returns
    a tuple: a list of ranges and a boolean indicating whether the ranges
    where calculated based on a visual selection.
    """

    # FIXME: make sure this works with whitespace between markers, and doublecheck
    # with Vim to see whether '<;>' is allowed.
    # '<,>' returns all selected line blocks
    if r['left_ref'] == "'<" and r['right_ref'] == "'>":
        all_line_blocks = []
        for sel in view.sel():
            start = view.rowcol(sel.begin())[0] + 1
            end = view.rowcol(sel.end())[0] + 1
            if view.substr(sel.end() - 1) == '\n':
                end -= 1
            all_line_blocks.append((start, end))
        return all_line_blocks, True

    # todo: '< and other marks
    if r['left_ref'] and (r['left_ref'].startswith("'") or (r['right_ref'] and r['right_ref'].startswith("'"))):
        return []

    # todo: don't mess up with the received ranged. Also, % has some strange
    # behaviors that should be easy to replicate.
    if r['left_ref'] == '%' or r['right_ref'] == '%':
        r['left_offset'] = 1
        r['right_ref'] = '$'

    current_line = None
    lr = r['left_ref']
    if lr is not None:
        current_line = calculate_relative_ref(view, lr)
    loffset = r['left_offset']
    if loffset:
        current_line = current_line or 0
        current_line += loffset

    searches = r['left_search_offsets']
    if searches:
        current_line = new_calculate_search_offsets(view, searches, current_line or calculate_relative_ref(view, '.'))
    left = current_line

    current_line = None
    rr = r['right_ref']
    if rr is not None:
        current_line = calculate_relative_ref(view, rr)
    roffset = r['right_offset']
    if roffset:
        current_line = current_line or 0
        current_line += roffset

    searches = r['right_search_offsets']
    if searches:
        current_line = new_calculate_search_offsets(view, searches, current_line or calculate_relative_ref(view, '.'))
    right = current_line

    if not right:
        right = left

    # todo: move this to the parsing phase? Do all vim commands default to '.' as a range?
    if not any([left, right]):
        left = right = calculate_relative_ref(view, '.')

    # todo: reverse range automatically if needed
    return [(left, right)], False

# Avoid circular import.
# from vex import ex_location
