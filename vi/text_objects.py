import sublime

from Vintageous.vi.search import reverse_search_by_pt
from Vintageous.vi.search import find_in_range


PAIRS = {
    # FIXME: Treat quotation marks differently. We cannot distinguish between opening and closing
    # in this case.
    '"': ('"', '"'),
    "'": ("'", "'"),
    "`": ("`", "`"),
    "(": ("\\(", "\\)"),
    ")": ("\\(", "\\)"),
    # XXX: Does Vim really allow this one?
    "[": ("\\[", "\\]"),
    "]": ("\\[", "\\]"),
    "{": ("\\{", "\\}"),
    "}": ("\\{", "\\}"),
    # TODO: Get rid of this sloppiness.
    "t": lambda x: x,
}


def find_next(view, start, what):
    limit = view.line(start).b
    pt = start
    while True:
        if pt > limit:
            return start

        if view.substr(pt) == what:
            return pt

        pt += 1

    return start


def get_text_object_region(view, s, text_object, inclusive=False):
    if text_object in PAIRS:
        actual_text_object = PAIRS[text_object]

        if callable(actual_text_object):
            return tag_text_object(view, s, inclusive)
        else:
            a, b = actual_text_object
            start = find_balanced_opening_tag(view, s.b, (a, b))
            end = find_balanced_closing_item(view, s.b, (a, b))
            if not (start and end):
                return s
            if inclusive:
                return sublime.Region(start.a, end.b)
            else:
                return sublime.Region(start.a + 1, end.b - 1)
    return s


def tag_text_object(view, s, inclusive=False):

    if (view.score_selector(s.b, 'text.html') == 0 and
        view.score_selector(s.b, 'text.xml') == 0):
            # TODO: What happens with other xml formats?
            return s

    end_tag_patt = "</(.+?)>"
    begin_tag_patt = "<{0}(\s+.*?)?>"

    closing_tag = view.find(end_tag_patt, s.b, sublime.IGNORECASE)

    if not closing_tag:
        return s

    begin_tag_patt = begin_tag_patt.format(view.substr(closing_tag)[2:-1])

    begin_tag = find_balanced_opening_tag(view, closing_tag.a, (begin_tag_patt, view.substr(closing_tag)))

    if not begin_tag:
        return s

    if not inclusive:
        return sublime.Region(begin_tag.b, closing_tag.a)
    return sublime.Region(begin_tag.a, closing_tag.b)


def find_balanced_closing_item(view, start, items, unbalanced=0):
    # TODO: Extract common functionality from here and the % motion instead of duplicating code.
    new_start = start
    for i in range(unbalanced or 1):
        next_closing_bracket = find_in_range(view, items[1],
                                                  start=start,
                                                  end=view.size(),
                                                  flags=sublime.IGNORECASE)
        if next_closing_bracket is None:
            # Unbalanced items; nothing we can do.
            return
        new_start = next_closing_bracket.end()

    nested = 0
    while True:
        next_opening_bracket = find_in_range(view, items[0],
                                              start=start,
                                              end=next_closing_bracket.b,
                                              flags=sublime.IGNORECASE)
        if not next_opening_bracket:
            break
        nested += 1
        start = next_opening_bracket.end()

    if nested > 0:
        return find_balanced_closing_item(view, next_closing_bracket.end(),
                                                  items,
                                                  nested)
    else:
        return next_closing_bracket


def find_balanced_opening_tag(view, start, tags, unbalanced=0):
    # TODO: Extract common functionality from here and the % motion instead of duplicating code.
    new_start = start
    for i in range(unbalanced or 1):
        prev_opening_bracket = reverse_search_by_pt(view, tags[0],
                                                  start=0,
                                                  end=new_start,
                                                  flags=sublime.IGNORECASE)
        if prev_opening_bracket is None:
            # Unbalanced tags; nothing we can do.
            return
        new_start = prev_opening_bracket.begin()

    nested = 0
    while True:
        next_closing_bracket = reverse_search_by_pt(view, tags[1],
                                              start=prev_opening_bracket.a,
                                              end=start,
                                              flags=sublime.IGNORECASE)
        if not next_closing_bracket:
            break
        nested += 1
        start = next_closing_bracket.begin()

    if nested > 0:
        return find_balanced_opening_tag(view, prev_opening_bracket.begin(),
                                                  tags,
                                                  nested)
    else:
        return prev_opening_bracket