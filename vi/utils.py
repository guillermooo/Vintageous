import sublime

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL, MODE_NORMAL, MODE_VISUAL


def is_at_eol(view, reg):
    return view.line(reg.b).b == reg.b


def _is_on_eol(view, reg, mode):
    if mode in (_MODE_INTERNAL_NORMAL, MODE_NORMAL):
            return view.line(reg.b).b == reg.b
    elif mode == MODE_VISUAL:
        return view.full_line(reg.b - 1).b == reg.b


def is_at_hard_eol(view, reg):
    return view.full_line(reg.b - 1).b == reg.b


def is_at_bol(view, reg):
    return view.line(reg.b).a == reg.b


def back_one_char(reg):
    return sublime.Region(reg.a - 1, reg.b - 1)


def back_end_one_char(reg):
    return sublime.Region(reg.a, reg.b - 1)


def forward_one_char(reg):
    return sublime.Region(reg.a + 1, reg.b + 1)


def forward_end_one_char(reg):
    return sublime.Region(reg.a, reg.b + 1)


def is_line_empty(view, pt):
    return view.line(pt).empty()


def is_on_empty_line(view, s):
    if is_line_empty(view, s.a):
        return True

def visual_is_on_empty_line_forward(view, s):
    if is_line_empty(view, s.b - 1):
        return True

def visual_is_end_at_bol(view, s):
    bol = view.line(s.b).a
    return s.b - 1 == bol


def visual_is_end_at_eol(view, reg):
    return view.line(reg.b - 1).b == reg.b


def visual_is_end_at_hard_eol(view, s):
    heol = view.full_line(s.b - 1).b
    return s.b == heol


def visual_forward_is_current_line_empty(view, r):
    return view.line(r.b - 1).empty()


def visual_forward_is_previous_line_empty(view, r):
    return view.line(r.b - 2).empty()


def visual_forward_is_caret_on_eol(view, r):
    return view.full_line(r.b - 1).b == r.b


def visual_forward_is_caret_at_eol(view, r):
    return view.line(r.b - 1).b == r.b


def is_region_reversed(view, r):
    return r.a > r.b


def reverse_region(r):
    return sublime.Region(r.b, r.a)


def orient_region_right(r):
    return sublime.Region(r.begin(), r.end())


def orient_region_left(r):
    return sublime.Region(r.end(), r.begin())


def next_non_white_space_char(view, pt, white_space='\t '):
    while (view.substr(pt) in white_space) and (pt <= view.size()):
        pt += 1
    return pt


def previous_non_white_space_char(view, pt, white_space='\t \n'):
    while view.substr(pt) in white_space and pt > 0:
        pt -= 1
    return pt


def previous_white_space_char(view, pt):
    while view.substr(pt) not in '\t ':
        pt -= 1
    return pt


def next_white_space_char(view, pt, white_space='\t \n'):
    while view.substr(pt) not in white_space:
        pt += 1
    return pt


def visual_back_one_word(view, pt):
    word_end = pt
    if view.substr(pt - 1) in '\t ':
        word_end = previous_non_white_space_char(view, pt - 1)
    return previous_white_space_char(view, word_end)

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
