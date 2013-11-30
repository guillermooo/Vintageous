import sublime

from sublime import CLASS_WORD_START
from sublime import CLASS_WORD_END
from sublime import CLASS_PUNCTUATION_START
from sublime import CLASS_PUNCTUATION_END
from sublime import CLASS_LINE_END
from sublime import CLASS_LINE_START
from sublime import CLASS_EMPTY_LINE

from Vintageous.vi.search import reverse_search_by_pt
from Vintageous.vi.search import find_in_range
from Vintageous.vi import units
from Vintageous.vi import utils
from Vintageous.vi import search

import re


RX_ANY_TAG = r'</?([0-9A-Za-z]+).*?>'
RXC_ANY_TAG = re.compile(r'</?([0-9A-Za-z]+).*?>')
# According to the HTML 5 editor's draft, only 0-9A-Za-z characters can be
# used in tag names. TODO: This won't be enough in Dart Polymer projects,
# for example.
RX_ANY_START_TAG = r'<([0-9A-Za-z]+)(.*?)>'
RX_ANY_END_TAG = r'</.*?>'


ANCHOR_NEXT_WORD_BOUNDARY = CLASS_WORD_START | CLASS_PUNCTUATION_START | \
                            CLASS_LINE_END
ANCHOR_PREVIOUS_WORD_BOUNDARY = CLASS_WORD_END | CLASS_PUNCTUATION_END | \
                                CLASS_LINE_START


BRACKET = 1
QUOTE = 2
SENTENCE = 3
TAG = 4
WORD = 5
BIG_WORD = 6
PARAGRAPH = 7


PAIRS = {
    '"': (('"', '"'), QUOTE),
    "'": (("'", "'"), QUOTE),
    '`': (('`', '`'), QUOTE),
    '(': (('\\(', '\\)'), BRACKET),
    ')': (('\\(', '\\)'), BRACKET),
    '[': (('\\[', '\\]'), BRACKET),
    ']': (('\\[', '\\]'), BRACKET),
    '{': (('\\{', '\\}'), BRACKET),
    '}': (('\\{', '\\}'), BRACKET),
    '<': (('<', '>'), BRACKET),
    '>': (('<', '>'), BRACKET),
    't': (None, TAG),
    'w': (None, WORD),
    'W': (None, BIG_WORD),
    's': (None, SENTENCE),
    'p': (None, PARAGRAPH),
}


def is_at_punctuation(view, pt):
    next_char = view.substr(pt)
    # FIXME: Wrong if pt is at '\t'.
    return (not (is_at_word(view, pt) or
                 next_char.isspace() or
                 next_char == '\n')
            and next_char.isprintable())


def is_at_word(view, pt):
    next_char = view.substr(pt)
    return (next_char.isalnum() or next_char == '_')


def is_at_space(view, pt):
    return view.substr(pt).isspace()


def get_punctuation_region(view, pt):
   start = view.find_by_class(pt + 1, forward=False,
                              classes=CLASS_PUNCTUATION_START)
   end = view.find_by_class(pt, forward=True,
                            classes=CLASS_PUNCTUATION_END)
   return sublime.Region(start, end)


def get_space_region(view, pt):
    end = view.find_by_class(pt, forward=True,
                             classes=ANCHOR_NEXT_WORD_BOUNDARY)
    return sublime.Region(previous_word_end(view, pt + 1), end)


def previous_word_end(view, pt):
    return view.find_by_class(pt, forward=False,
                              classes=ANCHOR_PREVIOUS_WORD_BOUNDARY)


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
                                     classes=CLASS_WORD_END |
                                             CLASS_PUNCTUATION_END |
                                             CLASS_LINE_END)
            return end

    # Skip the word under the caret and any trailing spaces.
    return view.find_by_class(pt, forward=True,
                              classes=ANCHOR_NEXT_WORD_BOUNDARY)


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


# See vim :help word for a definition of word.
def a_word(view, pt, inclusive=True, count=1):
    assert count > 0
    start = current_word_start(view, pt)
    end = pt
    if inclusive:
        end = units.word_starts(view, start, count=count, internal=True)

        # If there is no space at the end of our word text object, include any
        # preceding spaces. (Follows Vim behavior.)
        if (not view.substr(end - 1).isspace() and
            view.substr(start - 1).isspace()):
                start = utils.previous_non_white_space_char(
                                                    view, start - 1,
                                                    white_space=' \t') + 1

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

    if type_ == PARAGRAPH:
        return find_paragraph_text_object(view, s, inclusive)

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
        prev_quote = reverse_search_by_pt(view, r'(?<!\\\\)' + delims[0],
                                          start=line.a, end=s.b)

        next_quote = find_in_range(view, r'(?<!\\\\)' + delims[0],
                                   start=s.b, end=line.b)

        if next_quote and not prev_quote:
            prev_quote = next_quote
            next_quote = find_in_range(view, r'(?<!\\\\)' + delims[0],
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
        if s.size() <= 1:
            return w
        return sublime.Region(s.a, w.b)

    if type_ == BIG_WORD:
        w = a_big_word(view, s.b, inclusive=inclusive, count=count)
        if not w:
            return s
        if s.size() <= 1:
            return w
        return sublime.Region(s.a, w.b)

    if type_ == SENTENCE:
        # FIXME: This doesn't work well.
        # TODO: Improve this.
        sentence_start = view.find_by_class(s.b,
                                            forward=False,
                                            classes=sublime.CLASS_EMPTY_LINE)
        sentence_start_2 = reverse_search_by_pt(view, r'[.?!:]\s+|[.?!:]$',
                                                start=0,
                                                end=s.b)
        if sentence_start_2:
            sentence_start = (sentence_start + 1 if (sentence_start >
                                                     sentence_start_2.b)
                                                 else sentence_start_2.b)
        else:
            sentence_start = sentence_start + 1
        sentence_end = find_in_range(view, r'([.?!:)](?=\s))|([.?!:)]$)',
                                     start=s.b,
                                     end=view.size())

        if not (sentence_end):
            return s

        if inclusive:
            return sublime.Region(sentence_start, sentence_end.b)
        else:
            return sublime.Region(sentence_start, sentence_end.b)


    return s


def get_tag_name(tag):
    return re.match(RXC_ANY_TAG, tag).groups()[0]


def find_tag_text_object(view, s, inclusive=False):

    if (view.score_selector(s.b, 'text.html') == 0 and
        view.score_selector(s.b, 'text.xml') == 0):
            # TODO: What happens with other xml formats?
            return s

    # TODO: Receive the actual mode in the parameter list?
    current_pt = (s.b - 1) if view.has_non_empty_selection_region() else s.b
    start_pt = utils.previous_white_space_char(view, current_pt,
                                               white_space=' \t\n') + 1

    if view.substr(sublime.Region(start_pt, start_pt + 2)) == '</':
        closing_tag = view.find(RX_ANY_END_TAG, start_pt, sublime.IGNORECASE)
        name = get_tag_name(view.substr(closing_tag))
        start_tag_pattern = r'<({0}).*?>'.format(name)
        start_tag = search.reverse_search_by_pt(view, start_tag_pattern, 0,
                                                start_pt)
    elif view.substr(start_pt) == '<':
        start_tag = view.find(RX_ANY_START_TAG, start_pt, sublime.IGNORECASE)
        if start_tag.a != start_pt:
            return s
    else:
        start_tag = search.reverse_search_by_pt(view, RX_ANY_START_TAG, 0,
                                                start_pt)

    if not start_tag:
        return s

    tag_name = get_tag_name(view.substr(start_tag))

    literal_end_tag = r'</{0}>'.format(tag_name)
    end_tag = None
    current_pt = start_tag.b
    while True:
        temp_end_tag = view.find(literal_end_tag, current_pt,
                                 sublime.IGNORECASE)
        if not end_tag and not temp_end_tag:
            return s
        elif not temp_end_tag:
            break

        end_tag = temp_end_tag
        current_pt = end_tag.b

        where = view.substr(sublime.Region(start_pt, end_tag.end()))
        opening_tags = re.findall(r'<{0}.*?>'.format(tag_name), where,
                                  re.IGNORECASE)
        closing_tags = re.findall(literal_end_tag, where, sublime.IGNORECASE)

        if len(opening_tags) == len(closing_tags):
            break

    if not end_tag:
        return s

    # Perhaps this should be handled further up by the command itself?
    was_visual = view.has_non_empty_selection_region()
    if not inclusive:
        if not was_visual:
            return sublime.Region(start_tag.b, end_tag.a)
        else:
            if start_tag.b == end_tag.a:
                return sublime.Region(start_tag.b, start_tag.b + 1)
            else:
                return sublime.Region(start_tag.b, end_tag.a)

    if not was_visual:
        return sublime.Region(start_tag.a, end_tag.b)
    else:
        if start_tag.a == end_tag.b:
            return sublime.Region(start_tag.a, start_tag.a + 1)
        else:
            return sublime.Region(start_tag.a, end_tag.b)


def find_next_lone_bracket(view, start, items, unbalanced=0):
    # TODO: Extract common functionality from here and the % motion instead of
    # duplicating code.
    new_start = start
    for i in range(unbalanced or 1):
        next_closing_bracket = find_in_range(view, items[1],
                                                  start=new_start,
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
    # TODO: Extract common functionality from here and the % motion instead of
    # duplicating code.
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


def find_paragraph_text_object(view, s, inclusive=True):
    # TODO: Implement counts.
    begin = view.find_by_class(s.a, forward=False, classes=CLASS_EMPTY_LINE)
    end = view.find_by_class(s.b, forward=True, classes=CLASS_EMPTY_LINE)
    if not inclusive:
        if begin > 0:
            begin += 1
    return sublime.Region(begin, end)
