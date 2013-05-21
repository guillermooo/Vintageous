import sublime

from Vintageous.vi.search import reverse_search_by_pt


def tag_text_object(view, s, inclusive=False):

    if (view.score_selector(s.b, 'text.html') == 0 and
        view.score_selector(s.b, 'text.xml') == 0):
            # TODO: What happens with other xml formats?
            return None

    end_tag_patt = "</(.+?)>"
    begin_tag_patt = "<{0}(\s+.*?)?>"

    closing_tag = view.find(end_tag_patt, s.b, sublime.IGNORECASE)

    if not closing_tag:
        return None

    begin_tag_patt = begin_tag_patt.format(view.substr(closing_tag)[2:-1])

    begin_tag = find_balanced_opening_tag(view, closing_tag.a, (begin_tag_patt, view.substr(closing_tag)))

    if not begin_tag:
        return None

    if not inclusive:
        return sublime.Region(begin_tag.b, closing_tag.a)
    return sublime.Region(begin_tag.a, closing_tag.b)


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
        return find_balanced_opening_bracket(prev_opening_bracket.begin(),
                                                  tags,
                                                  nested)
    else:
        return prev_opening_bracket