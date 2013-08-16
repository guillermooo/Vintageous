from sublime import CLASS_WORD_START
from sublime import CLASS_WORD_END
from sublime import CLASS_PUNCTUATION_START
from sublime import CLASS_PUNCTUATION_END
from sublime import CLASS_EMPTY_LINE
from sublime import CLASS_LINE_END
from sublime import CLASS_LINE_START


from Vintageous.vi.utils import next_non_white_space_char

import re


word_pattern = re.compile('\w')

# Places at which regular words start (for Vim).
CLASS_VI_WORD_START = CLASS_WORD_START | CLASS_PUNCTUATION_START | CLASS_LINE_START
# Places at which *sometimes* words start. Called 'internal' because it's a notion Vim has; not
# obvious.
CLASS_VI_INTERNAL_WORD_START = CLASS_WORD_START | CLASS_PUNCTUATION_START | CLASS_LINE_END
CLASS_VI_WORD_END = CLASS_WORD_END | CLASS_PUNCTUATION_END
CLASS_VI_INTERNAL_WORD_END = CLASS_WORD_END | CLASS_PUNCTUATION_END


def at_eol(view, pt):
    return (view.classify(pt) & CLASS_LINE_END) == CLASS_LINE_END


def at_punctuation(view, pt):
    # FIXME: Not very reliable?
    is_at_eol = at_eol(view, pt)
    is_at_word = at_word(view, pt)
    is_white_space = view.substr(pt).isspace()
    is_at_eof = pt == view.size()
    return not any((is_at_eol, is_at_word, is_white_space, is_at_eof))


def at_word_start(view, pt):
    return (view.classify(pt) & CLASS_WORD_START) == CLASS_WORD_START


def at_word_end(view, pt):
    return (view.classify(pt) & CLASS_WORD_END) == CLASS_WORD_END


def at_punctuation_end(view, pt):
    return (view.classify(pt) & CLASS_PUNCTUATION_END) == CLASS_PUNCTUATION_END


def at_word(view, pt):
    return at_word_start(view, pt) or word_pattern.match(view.substr(pt))


def skip_word(view, pt):
    while True:
        if at_punctuation(view, pt):
            pt = view.find_by_class(pt, forward=True, classes=CLASS_PUNCTUATION_END)
        elif at_word(view, pt):
            pt = view.find_by_class(pt, forward=True, classes=CLASS_WORD_END)
        else:
            break
    return pt


def next_word_start(view, start, internal=False):
    classes = CLASS_VI_WORD_START if not internal else CLASS_VI_INTERNAL_WORD_START
    pt = view.find_by_class(start, forward=True, classes=classes)
    if internal and at_eol(view, pt):
        # Unreachable?
        return pt
    return pt


def next_big_word_start(view, start, internal=False):
    classes = CLASS_VI_WORD_START if not internal else CLASS_VI_INTERNAL_WORD_START
    pt = skip_word(view, start)
    seps = ''
    if internal and at_eol(view, pt):
        return pt
    pt = view.find_by_class(pt, forward=True, classes=classes, separators=seps)
    return pt


def next_word_end(view, start, internal=False):
    classes = CLASS_VI_WORD_END if not internal else CLASS_VI_INTERNAL_WORD_END
    pt = view.find_by_class(start, forward=True, classes=classes)
    if internal and at_eol(view, pt):
        # Unreachable?
        return pt
    return pt


def word_starts(view, start, count=1, internal=False):
    assert start >= 0
    assert count > 0

    pt = start
    for i in range(count):
        # On the last motion iteration, we must do some special stuff if we are still on the
        # starting line of the motion.
        if (internal and (i == count - 1) and
            (view.line(start) == view.line(pt))):
                if view.substr(pt) == '\n':
                    return pt + 1
                return next_word_start(view, pt, internal=True)

        pt = next_word_start(view, pt)
        if not internal or (i != count - 1):
            pt = next_non_white_space_char(view, pt, white_space=' \t')
            while not (view.size() == pt or
                       view.line(pt).empty() or
                       view.substr(view.line(pt)).strip()):
                pt = next_word_start(view, pt)
                pt = next_non_white_space_char(view, pt, white_space=' \t')

    if (internal and (view.line(start) != view.line(pt)) and
       (start != view.line(start).a and not view.substr(view.line(pt - 1)).isspace()) and
         at_eol(view, pt - 1)):
            pt -= 1

    return pt


def big_word_starts(view, start, count=1, internal=False):
    assert start >= 0
    assert count > 0

    pt = start
    for i in range(count):
        if internal and i == count - 1 and view.line(start) == view.line(pt):
            if view.substr(pt) == '\n':
                return pt + 1
            return next_big_word_start(view, pt, internal=True)

        pt = next_big_word_start(view, pt)
        if not internal or i != count - 1:
            pt = next_non_white_space_char(view, pt, white_space=' \t')
            while not (view.size() == pt or
                       view.line(pt).empty() or
                       view.substr(view.line(pt)).strip()):
                pt = next_big_word_start(view, pt)
                pt = next_non_white_space_char(view, pt, white_space=' \t')

    if (internal and (view.line(start) != view.line(pt)) and
       (start != view.line(start).a and not view.substr(view.line(pt - 1)).isspace()) and
         at_eol(view, pt - 1)):
            pt -= 1

    return pt


def word_ends(view, start, count=1, internal=False):
    assert start >= 0
    assert count > 0

    pt = start

    for i in range(count):
        # TODO: In Vim, cw on the last word char deletes up to the current word's end or eol
        # (exclusive). However, ce at the same position deletes up to the next word's end. Remember
        # that normally cw is translated to ce. In order to be 100% Vim-compatible, we need to know
        # that the translation has taken place. For the moment, just unify 'e' and 'w' behavior at
        # the word's last char. Also, it seems that 'ce' translates to a especial motion, not
        # simply 'cw'. That should be easier to implement.
        offset = 1
        if internal:
            offset = 1 if not (at_word_end(view, pt + 1) or
                               at_punctuation_end(view, pt + 1)) else 0
        pt = next_word_end(view, pt + offset)

    # FIXME: We should return the actual word end and not pt - 1 ??
    return pt - 1
