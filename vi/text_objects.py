import re

import sublime
from sublime import CLASS_WORD_START
from sublime import CLASS_WORD_END
from sublime import CLASS_PUNCTUATION_START
from sublime import CLASS_PUNCTUATION_END
from sublime import CLASS_LINE_END
from sublime import CLASS_LINE_START
from sublime import CLASS_EMPTY_LINE

from Vintageous.vi import search
from Vintageous.vi import units
from Vintageous.vi import utils
from Vintageous.vi.search import find_in_range
from Vintageous.vi.search import reverse_search_by_pt
from Vintageous.vi.utils import resolve_insertion_point_at_b


RX_ANY_TAG = r'</?([0-9A-Za-z-]+).*?>'
RX_ANY_TAG_NAMED_TPL = r'</?({0}) *?.*?>'
RXC_ANY_TAG = re.compile(r'</?([0-9A-Za-z]+).*?>')
# According to the HTML 5 editor's draft, only 0-9A-Za-z characters can be
# used in tag names. TODO: This won't be enough in Dart Polymer projects,
# for example.
RX_ANY_START_TAG = r'<([0-9A-Za-z]+)(.*?)>'
RX_ANY_END_TAG = r'</([0-9A-Za-z-]+).*?>'


ANCHOR_NEXT_WORD_BOUNDARY = CLASS_WORD_START | CLASS_PUNCTUATION_START | \
                            CLASS_LINE_END
ANCHOR_PREVIOUS_WORD_BOUNDARY = CLASS_WORD_END | CLASS_PUNCTUATION_END | \
                                CLASS_LINE_START

WORD_REVERSE_STOPS = CLASS_WORD_START | CLASS_EMPTY_LINE | \
                         CLASS_PUNCTUATION_START
WORD_END_REVERSE_STOPS = CLASS_WORD_END | CLASS_EMPTY_LINE | \
                         CLASS_PUNCTUATION_END



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
    'b': (('\\(', '\\)'), BRACKET),
    'B': (('\\{', '\\}'), BRACKET),
    'p': (None, PARAGRAPH),
    's': (None, SENTENCE),
    't': (None, TAG),
    'W': (None, BIG_WORD),
    'w': (None, WORD),
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
        begin_tag, end_tag, _ = find_containing_tag(view, s.b)
        if inclusive:
            return sublime.Region(begin_tag.a, end_tag.b)
        else:
            return sublime.Region(begin_tag.b, end_tag.a)

    if type_ == PARAGRAPH:
        return find_paragraph_text_object(view, s, inclusive=inclusive, count=count)

    if type_ == BRACKET:
        b = resolve_insertion_point_at_b(s)
        opening = find_prev_lone_bracket(view, b, delims)
        closing = find_next_lone_bracket(view, b, delims)

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

        while view.substr(next_closing_bracket.begin() - 1) == '\\':
            next_closing_bracket = find_in_range(view, items[1],
                                                 start=next_closing_bracket.end(),
                                                 end=view.size(),
                                                 flags=sublime.IGNORECASE)
            if next_closing_bracket is None:
                return

        new_start = next_closing_bracket.end()

    if view.substr(start) == items[0][-1]:
        start += 1

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

    # XXX: refactor this
    if view.substr(start) == tags[0][1] if len(tags[0]) > 1 else tags[0]:
        if not unbalanced and view.substr(start - 1) != '\\':
            return sublime.Region(start, start + 1)

    new_start = start
    for i in range(unbalanced or 1):
        prev_opening_bracket = reverse_search_by_pt(view, tags[0],
                                                  start=0,
                                                  end=new_start,
                                                  flags=sublime.IGNORECASE)

        if prev_opening_bracket is None:
            # Check whether the caret is exactly at a bracket.
            # Tag names may be escaped, so slice them.
            if (i == 0 and view.substr(start) == tags[0][-1] and
               view.substr(start - 1) != '\\'):
                    return sublime.Region(start, start + 1)
            # Unbalanced tags; nothing we can do.
            return

        while view.substr(prev_opening_bracket.begin() - 1) == '\\':
            prev_opening_bracket = reverse_search_by_pt(
                                          view, tags[0],
                                          start=0,
                                          end=prev_opening_bracket.begin(),
                                          flags=sublime.IGNORECASE)
            if prev_opening_bracket is None:
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

def find_paragraph_text_object(view, s, inclusive=True, count=1):
    # In Vim, `vip` will select an inner paragraph -- all the lines having the
    # same whitespace status of the current location. And a `vap` will select
    # both the current inner paragraph (either whitespace or not) and the next
    # inner paragraph (the opposite).
    begin = None
    end   = s.a
    for _ in range(count):
        b1, e1  = find_inner_paragraph(view, end)
        b2, end = find_inner_paragraph(view, e1) if inclusive else (b1, e1)
        if begin is None:
            begin = b1
    return sublime.Region(begin, end)

def find_inner_paragraph(view, initial_loc):
    '''Takes a location, as an integer. Returns a (begin, end) tuple of ints for
    the Vim inner paragraph corresponding to that location. An inner paragraph
    consists of a set of contiguous lines all having the same whitespace status
    (a line either consists entirely of whitespace characters or it does not).'''
    # Determine whether the initial point lies in an all-whitespace line.
    is_whitespace = lambda region: len(view.substr(region).strip()) == 0
    iws = is_whitespace(view.line(initial_loc))

    # Search backward finding all lines with similar whitespace status.
    # This will give use the value for begin.
    p = initial_loc
    while True:
        line = view.line(p)
        if is_whitespace(line) != iws:
            break
        elif line.begin() == 0:
            p = 0
            break
        p = line.begin() - 1
    begin = p + 1 if p > 0 else p

    # To get the value for end, we do the same thing, this time searching forward.
    p = initial_loc
    while True:
        line = view.line(p)
        if is_whitespace(line) != iws:
            break
        p = line.end() + 1
        if p >= view.size():
            break
    end = p

    return (begin, end)

# TODO: Move this to units.py.
def word_reverse(view, pt, count=1, big=False):
    t = pt
    for _ in range(count):
        t = view.find_by_class(t, forward=False, classes=WORD_REVERSE_STOPS)
        if t == 0:
            break

        if big:
            # Skip over punctuation characters.
            while not ((view.substr(t - 1) in '\n\t ') or (t <= 0)):
                t -= 1
    return t


# TODO: Move this to units.py.
def word_end_reverse(view, pt, count=1, big=False):
    t = pt
    for i in range(count):
        if big:
            # Skip over punctuation characters.
            while not ((view.substr(t - 1) in '\n\t ') or (t <= 0)):
                t -= 1

        # `ge` should stop at the previous word end if starting at a space
        # immediately after a word.
        if (i == 0 and
            view.substr(t).isspace() and
            not view.substr(t - 1).isspace()):
                continue

        if (not view.substr(t).isalnum() and
            not view.substr(t).isspace() and
            view.substr(t - 1).isalnum() and
            t > 0):
                pass
        else:
            t = view.find_by_class(t, forward=False, classes=WORD_END_REVERSE_STOPS)
        if t == 0:
            break

    return max(t - 1, 0)


def next_end_tag(view, pattern=RX_ANY_TAG, start=0, end=-1):
    region = view.find(pattern, start, sublime.IGNORECASE)
    if region.a == -1:
        return None, None, None
    match = re.search(pattern, view.substr(region))
    return (region, match.group(1), match.group(0).startswith('</'))


def previous_begin_tag(view, pattern, start=0, end=0):
    assert pattern, 'bad call'
    region = reverse_search_by_pt(view, RX_ANY_TAG, start, end,
                                  sublime.IGNORECASE)
    if not region:
        return None, None, None
    match = re.search(RX_ANY_TAG, view.substr(region))
    return (region, match.group(1), match.group(0)[1] != '/')


def get_region_end(r):
    return {'start': r.end()}


def get_region_begin(r):
    return {'start': 0, 'end': r.begin()}


def get_closest_tag(view, pt):
    while pt > 0 and view.substr(pt) != '<':
        pt -= 1

    if view.substr(pt) != '<':
        return None

    next_tag = view.find(RX_ANY_TAG, pt)
    if next_tag.a != pt:
        return None

    return pt, next_tag


def find_containing_tag(view, start):
    # BUG: fails if start < first begin tag
    # TODO: Should not select tags in PCDATA sections.
    _, closest_tag = get_closest_tag(view, start)
    if not closest_tag:
        return None, None, None

    start = closest_tag.a if ((closest_tag.contains(start)) and
                              (view.substr(closest_tag)[1] == '/')) else start

    search_forward_args = {
        'pattern': RX_ANY_TAG,
        'start': start,
    }
    end_region, tag_name = next_unbalanced_tag(view,
                                 search=next_end_tag,
                                 search_args=search_forward_args,
                                 restart_at=get_region_end)

    if not end_region:
        return None, None, None

    search_backward_args = {
        'pattern': RX_ANY_TAG_NAMED_TPL.format(tag_name),
        'start': 0,
        'end': end_region.a
    }
    begin_region, _ = next_unbalanced_tag(view,
                                 search=previous_begin_tag,
                                 search_args=search_backward_args,
                                 restart_at=get_region_begin)

    if not end_region:
        return None, None, None

    return begin_region, end_region, tag_name


def next_unbalanced_tag(view,
                        search=None,
                        search_args={},
                        restart_at=None,
                        tags=[]):
    assert search and restart_at, 'wrong call'

    region, tag, is_end_tag = search(view, **search_args)

    if not region:
        return None, None

    if not is_end_tag:
        tags.append(tag)
        search_args.update(restart_at(region))
        return next_unbalanced_tag(view,
                                   search,
                                   search_args,
                                   restart_at,
                                   tags)

    if not tags or (tag not in tags):
        return region, tag

    while tag != tags.pop():
        continue

    search_args.update(restart_at(region))
    return next_unbalanced_tag(view,
                               search,
                               search_args,
                               restart_at,
                               tags)
