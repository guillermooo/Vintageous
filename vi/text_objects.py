import sublime

from Vintageous.vi.search import reverse_search_by_pt
from Vintageous.vi.search import find_in_range


BRACKET = 1
QUOTE = 2
SENTENCE = 3
TAG = 4
WORD = 5


PAIRS = {
    # FIXME: Treat quotation marks differently. We cannot distinguish between opening and closing
    # in this case.
    '"': (('"', '"'), QUOTE),
    "'": (("'", "'"), QUOTE),
    '`': (('`', '`'), QUOTE),
    '(': (('\\(', '\\)'), BRACKET),
    ')': (('\\(', '\\)'), BRACKET),
    '[': (('\\[', '\\]'), BRACKET),
    ']': (('\\[', '\\]'), BRACKET),
    '{': (('\\{', '\\}'), BRACKET),
    '}': (('\\{', '\\}'), BRACKET),
    't': (None, TAG),
    'w': (None, WORD),
    's': (None, SENTENCE),
    # TODO: Implement this.
    # 'p': (None, PARAGRAPH),
}


def get_text_object_region(view, s, text_object, inclusive=False):
    try:
        delims, type_ = PAIRS[text_object]
    except KeyError:
        return s

    if type_ == TAG:
        return find_tag_text_object(view, s, inclusive)

    if type_ == BRACKET:
        opening = find_prev_lone_bracket(view, s.b, delims)
        closing = find_next_lone_bracket(view, s.b, delims)

        if not (opening and closing):
            return s

        if inclusive:
            return sublime.Region(opening.a, closing.b)
        return sublime.Region(opening.a + 1, closing.b - 1)

    if type_ == QUOTE:
        prev_quote = reverse_search_by_pt(view, delims[0],
                                                start=0,
                                                end=s.b,
                                                flags=sublime.IGNORECASE)

        next_quote = find_in_range(view, delims[0],
                                         start=s.b,
                                         end=view.size(),
                                         flags=sublime.IGNORECASE)

        if not (prev_quote and next_quote):
            return s

        if inclusive:
            return sublime.Region(prev_quote.a, next_quote.b)
        return sublime.Region(prev_quote.a + 1, next_quote.b - 1)

    if type_ == WORD:
        # TODO: Improve this -- specify word separators.
        word_start = view.find_by_class(s.b,
                                        forward=True,
                                        classes=sublime.CLASS_WORD_START |
                                                sublime.CLASS_PUNCTUATION_START)
        w = view.word(s.b)

        # XXX: I don't think this is necessary?
        if not w:
            return s

        if inclusive:
            return sublime.Region(w.a, word_start)
        else:
            return w

    if type_ == SENTENCE:
        # FIXME: This doesn't work well.
        # TODO: Improve this.
        sentence_start = view.find_by_class(s.b,
                                            forward=False,
                                            classes=sublime.CLASS_EMPTY_LINE)
        sentence_start_2 = reverse_search_by_pt(view, "[.?!:]\s+|[.?!:]$",
                                              start=0,
                                              end=s.b)
        if sentence_start_2:
            sentence_start = sentence_start + 1 if sentence_start > sentence_start_2.b else sentence_start_2.b
        else:
            sentence_start = sentence_start + 1
        sentence_end = find_in_range(view, "[.?!:)](?=\s)|[.?!:)]$",
                                     start=s.b,
                                     end=view.size())

        if not (sentence_end):
            return s

        if inclusive:
            return sublime.Region(sentence_start, sentence_end.b)
        else:
            return sublime.Region(sentence_start, sentence_end.b)


    return s


def find_tag_text_object(view, s, inclusive=False):

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

    begin_tag = find_prev_lone_bracket(view, closing_tag.a, (begin_tag_patt, view.substr(closing_tag)))

    if not begin_tag:
        return s

    if not inclusive:
        return sublime.Region(begin_tag.b, closing_tag.a)
    return sublime.Region(begin_tag.a, closing_tag.b)


def find_next_lone_bracket(view, start, items, unbalanced=0):
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
        return find_next_lone_bracket(view, next_closing_bracket.end(),
                                                  items,
                                                  nested)
    else:
        return next_closing_bracket


def find_prev_lone_bracket(view, start, tags, unbalanced=0):
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
        return find_prev_lone_bracket(view, prev_opening_bracket.begin(),
                                                  tags,
                                                  nested)
    else:
        return prev_opening_bracket
