import sublime

from sublime import CLASS_WORD_START
from sublime import CLASS_WORD_END
from sublime import CLASS_PUNCTUATION_START
from sublime import CLASS_PUNCTUATION_END
from sublime import CLASS_LINE_END
from sublime import CLASS_LINE_START

from Vintageous.vi.search import reverse_search_by_pt
from Vintageous.vi.search import find_in_range
from Vintageous.vi import units


ANCHOR_NEXT_WORD_BOUNDARY = CLASS_WORD_START | CLASS_PUNCTUATION_START | CLASS_LINE_END
ANCHOR_PREVIOUS_WORD_BOUNDARY = CLASS_WORD_END | CLASS_PUNCTUATION_END | CLASS_LINE_START


BRACKET = 1
QUOTE = 2
SENTENCE = 3
TAG = 4
WORD = 5
BIG_WORD = 6


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
    'W': (None, BIG_WORD),
    's': (None, SENTENCE),
    # TODO: Implement this.
    # 'p': (None, PARAGRAPH),
}


def is_at_punctuation(view, pt):
    next_char = view.substr(pt)
    return (not (next_char.isalnum() or
                 next_char.isspace() or
                 next_char == '\n')
            and next_char.isprintable())


def is_at_word(view, pt):
    next_char = view.substr(pt)
    return next_char.isalnum()


def is_at_space(view, pt):
    return view.substr(pt).isspace()


def get_punctuation_region(view, pt):
   start = view.find_by_class(pt + 1, forward=False, classes=CLASS_PUNCTUATION_START)
   end = view.find_by_class(pt, forward=True, classes=CLASS_PUNCTUATION_END)
   return sublime.Region(start, end)


def get_space_region(view, pt):
    end = view.find_by_class(pt, forward=True, classes=ANCHOR_NEXT_WORD_BOUNDARY)
    return sublime.Region(previous_word_end(view, pt + 1), end)


def previous_word_end(view, pt):
    return view.find_by_class(pt, forward=False, classes=ANCHOR_PREVIOUS_WORD_BOUNDARY)


def next_word_start(view, pt):
    if is_at_punctuation(view, pt):
        # Skip all punctuation surrounding the caret and any trailing spaces.
        end = get_punctuation_region(view, pt).b
        if view.substr(end) in (' ', '\n'):
            end = view.find_by_class(end, forward=True,
                                     classes=ANCHOR_NEXT_WORD_BOUNDARY)
            return end
    elif is_at_space(view, pt):
        # Skip all spaces surrounding the cursor and the text word.
        end = get_space_region(view, pt).b
        if is_at_word(view, end) or is_at_punctuation(view, end):
            end = view.find_by_class(end, forward=True,
                                     classes=CLASS_WORD_END | CLASS_PUNCTUATION_END | CLASS_LINE_END)
            return end

    # Skip the word under the caret and any trailing spaces.
    return view.find_by_class(pt, forward=True, classes=ANCHOR_NEXT_WORD_BOUNDARY)


def current_word_start(view, pt):
    if is_at_punctuation(view, pt):
        return get_punctuation_region(view, pt).a
    elif is_at_space(view, pt):
        return get_space_region(view, pt).a
    return view.word(pt).a


def current_word_end(view, pt):
    if is_at_punctuation(view, pt):
        return get_punctuation_region(view, pt).b
    elif is_at_space(view, pt):
        return get_space_region(view, pt).b
    return view.word(pt).b


def a_word(view, pt, inclusive=True, count=1):
    assert count > 0
    start = current_word_start(view, pt)
    end = pt
    if inclusive:
        end = units.word_starts(view, start, count=count, internal=True)
        # Vim does some inconsistent stuff here...
        if count > 1 and view.substr(end) == '\n':
            end += 1
        return sublime.Region(start, end)

    for x in range(count):
        end = current_word_end(view, end)

    return sublime.Region(start, end)


def big_word_end(view, pt):
    while True:
        if is_at_punctuation(view, pt):
            pt = get_punctuation_region(view, pt).b
        elif is_at_word(view, pt):
            pt = current_word_end(view, pt)
        else:
            break
    return pt


def big_word_start(view, pt):
    while True:
        if is_at_punctuation(view, pt):
            pt = get_punctuation_region(view, pt).a - 1
        elif is_at_word(view, pt):
            pt = current_word_start(view, pt) - 1
        else:
            break
    return pt + 1


def a_big_word(view, pt, inclusive=True, count=1):
    start, end = None, pt
    for x in range(count):
        if is_at_space(view, end):
            if start is None:
                start = get_space_region(view, pt)
            if not inclusive:
                end = get_space_region(view, end).b
            else:
                end = big_word_end(view, get_space_region(view, end).b)

        if is_at_punctuation(view, end):
            if start is None:
                start = big_word_start(view, end)
            end = big_word_end(view, end)
            if inclusive and is_at_space(view, end):
                end = get_space_region(view, end).b

        else:
            if start is None:
                start = big_word_start(view, end)
            end = big_word_end(view, end)
            if inclusive and is_at_space(view, end):
                end = get_space_region(view, end).b

    return sublime.Region(start, end)


def get_text_object_region(view, s, text_object, inclusive=False, count=1):
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
        # Vim only operates on the current line.
        line = view.line(s)
        # FIXME: Escape sequences like \" are probably syntax-dependant.
        prev_quote = reverse_search_by_pt(view, '(?<!\\\\)' + delims[0],
                                          start=line.a, end=s.b)

        next_quote = find_in_range(view, '(?<!\\\\)' + delims[0],
                                   start=s.b, end=line.b)

        if next_quote and not prev_quote:
            prev_quote = next_quote
            next_quote = find_in_range(view, '(?<!\\\\)' + delims[0],
                                       start=prev_quote.b, end=line.b)

        if not (prev_quote and next_quote):
            return s

        if inclusive:
            return sublime.Region(prev_quote.a, next_quote.b)
        return sublime.Region(prev_quote.a + 1, next_quote.b - 1)

    if type_ == WORD:
        w = a_word(view, s.b, inclusive=inclusive, count=count)
        if not w:
            return s
        return w

    if type_ == BIG_WORD:
        w = a_big_word(view, s.b, inclusive=inclusive, count=count)
        if not w:
            return s
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
