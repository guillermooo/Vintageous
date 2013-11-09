import sublime

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL, MODE_NORMAL, MODE_VISUAL


# deprecated
def is_at_eol(view, reg):
    return view.line(reg.b).b == reg.b


# deprecated
def _is_on_eol(view, reg, mode):
    if mode in (_MODE_INTERNAL_NORMAL, MODE_NORMAL):
            return view.line(reg.b).b == reg.b
    elif mode == MODE_VISUAL:
        return view.full_line(reg.b - 1).b == reg.b


# deprecated
def is_at_bol(view, reg):
    return view.line(reg.b).a == reg.b


# deprecated
def back_one_char(reg):
    return sublime.Region(reg.a - 1, reg.b - 1)


# deprecated
def is_line_empty(view, pt):
    return view.line(pt).empty()


# deprecated
def is_on_empty_line(view, s):
    if is_line_empty(view, s.a):
        return True


# deprecated
def is_region_reversed(view, r):
    return r.a > r.b


# deprecated
def reverse_region(r):
    return sublime.Region(r.b, r.a)


def next_non_white_space_char(view, pt, white_space='\t '):
    while (view.substr(pt) in white_space) and (pt <= view.size()):
        pt += 1
    return pt


def previous_non_white_space_char(view, pt, white_space='\t \n'):
    while view.substr(pt) in white_space and pt > 0:
        pt -= 1
    return pt


# deprecated
def previous_white_space_char(view, pt, white_space='\t '):
    while pt >= 0 and view.substr(pt) not in white_space:
        pt -= 1
    return pt


def is_same_line(view, pt1, pt2):
    # XXX: Use built-in region comparison when's available.
    line_a, line_b = view.line(pt1), view.line(pt2)
    return (line_a.a == line_b.a) and (line_a.b == line_b.b)


def blink(times=4, delay=55):
    v = sublime.active_window().active_view()
    settings = v.settings()
    # Ensure we leave the setting as we found it.
    times = times if (times % 2) == 0 else times + 1

    def do_blink():
        nonlocal times
        if times > 0:
            settings.set('highlight_line', not settings.get('highlight_line'))
            times -= 1
            sublime.set_timeout(do_blink, delay)

    do_blink()


def has_empty_selection(view):
    return any(s.empty() for s in view.sel())
