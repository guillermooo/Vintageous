from sublime import CLASS_WORD_START
from sublime import CLASS_WORD_END
from sublime import CLASS_PUNCTUATION_START
from sublime import CLASS_PUNCTUATION_END
from sublime import CLASS_EMPTY_LINE
from sublime import CLASS_LINE_END

from Vintageous.vi.utils import next_non_white_space_char

import re

word_pattern = re.compile('\w')


CLASS_VI_WORD_START = (CLASS_WORD_START | CLASS_PUNCTUATION_START |
                       CLASS_EMPTY_LINE)
CLASS_VI_INTERNAL_WORD_START = (CLASS_WORD_START | CLASS_PUNCTUATION_START |
                                CLASS_LINE_END)
CLASS_VI_BIG_WORD_START = (CLASS_WORD_START | CLASS_EMPTY_LINE |
                           CLASS_PUNCTUATION_START)
CLASS_VI_INTERNAL_BIG_WORD_START = (CLASS_WORD_START | CLASS_LINE_END |
                                    CLASS_PUNCTUATION_START)


def at_eol(view, pt):
    return view.classify(pt) & CLASS_LINE_END == CLASS_LINE_END

def at_punctuation(view, pt):
    # FIXME: Not very reliable?
    is_at_eol = at_eol(view, pt)
    is_at_word = at_word(view, pt)
    is_white_space = view.substr(pt).isspace()
    is_at_eof = pt == view.size()
    return not any((is_at_eol, is_at_word, is_white_space, is_at_eof))

def at_punctuation_end(view, pt):
    return view.classify(pt) & CLASS_PUNCTUATION_END == CLASS_PUNCTUATION_END

def at_punctuation_start(view, pt):
    return view.classify(pt) & CLASS_PUNCTUATION_START == CLASS_PUNCTUATION_START

def at_word_start(view, pt):
    return view.classify(pt) & CLASS_WORD_START == CLASS_WORD_START

def at_word(view, pt):
    return at_word_start(view, pt) or word_pattern.match(view.substr(pt))


def skip_whitespace_lines(view, pt):
    while pt < view.size() and view.substr(view.line(pt)).isspace():
        pt = view.full_line(pt).b
    return pt


def skip_word(view, pt):
    while True:
        if at_punctuation(view, pt):
            pt = view.find_by_class(pt, forward=True, classes=CLASS_PUNCTUATION_END)
        elif at_word(view, pt):
            pt = view.find_by_class(pt, forward=True, classes=CLASS_WORD_END)
        else:
            break
    return pt


def next_word_start(view, start, classes=CLASS_VI_WORD_START):
    pt = view.find_by_class(start, forward=True, classes=classes)
    if classes != CLASS_VI_INTERNAL_WORD_START:
        while not (view.size() == pt or
                   view.line(pt).empty() or
                   view.substr(view.line(pt)).strip()):
            pt = next_word_start(view, pt, classes=classes)
    return pt


def prev_punctuation_start(view, start):
    pt = view.find_by_class(start, forward=False, classes=CLASS_PUNCTUATION_START)
    return pt


def next_big_word_start(view, start, classes=CLASS_VI_BIG_WORD_START):
    pt = skip_word(view, start)
    seps = ''
    pt = view.find_by_class(pt, forward=True, classes=classes,
                            separators=seps)

    if classes != CLASS_VI_INTERNAL_BIG_WORD_START:
        while not (view.line(pt).empty() or
                   view.substr(view.line(pt)).strip()):
            pt = next_word_start(view, pt, classes=classes, separators=seps)
    return pt


def word_starts(view, start, count=1, internal=False):
    assert start >= 0
    assert count > 0

    classes = (CLASS_VI_WORD_START if not internal
                                   else CLASS_VI_INTERNAL_WORD_START)

    pt = start
    for i in range(count):
        # Special case. Don't eat up next leading white space if moving from empty line in
        # internal mode.
        # For example, dw (starting in line 1):
        #
        #   1|
        #   2|  foo bar
        #
        if (internal and (i == count - 1) and view.line(pt).empty() and
            (pt < view.size())):
                pt += 1
                continue

        pt = next_word_start(view, pt, classes=classes)

        if internal:
            if ((i != count -1) and at_eol(view, pt) and
                pt + 1 < view.size() and view.line(pt+1).empty()):
                    pass
            elif ((i != count -1) and at_eol(view, pt) and
                  pt + 1 < view.size() and view.substr(view.line(pt+1)).isspace()):
                    pt = skip_whitespace_lines(view, pt + 1)
                    pt = next_non_white_space_char(view, pt, white_space=' \t')
            elif ((i != count - 1) and at_eol(view, pt) and
                  not view.line(pt).empty()):
                    pt = next_non_white_space_char(view, pt + 1,
                                                   white_space=' \t')

    if (internal and (view.line(start) != view.line(pt)) and
       (start == view.line(start).a or view.substr(view.line(start)).isspace()) and
         at_eol(view, pt)):
            pt += 1

    return pt


def big_words(view, start, count=1, internal=False):
    assert start >= 0
    assert count > 0

    classes = (CLASS_VI_BIG_WORD_START if not internal
                                   else CLASS_VI_INTERNAL_BIG_WORD_START)

    pt = start
    for i in range(count):
        # Special case. Don't eat up next leading white space if moving from empty line in
        # internal mode.
        # For example, dw (starting in line 1):
        #
        #   1|
        #   2|  foo bar
        #
        if (internal and (i == count - 1) and view.line(pt).empty() and
            (pt < view.size())):
                pt += 1
                continue

        pt = next_big_word_start(view, pt, classes=classes)
        if internal:
            if (i != count - 1):
                if (not view.line(pt).empty()) and at_eol(view, pt):
                    pt += 1
                    pt = next_non_white_space_char(view, pt, white_space=' \t')

    if (internal and (view.line(start) != view.line(pt)) and
        (not view.line(pt).empty()) and at_eol(view, pt)):
            pt += 1


    return pt
