import sublime


def select_point(view, left_end, right_end=None):
    if right_end is None:
        right_end = left_end 

    view.sel().clear()
    view.sel().add(sublime.Region(left_end, right_end))


def select_eof(view):
    select_point(view, view.size(), view.size())


def select_line(view, line_nr):
    pt = view.text_point(line_nr - 1, 0)
    select_point(view, pt)


def select_bof(view):
    select_point(view, 0, 0)
