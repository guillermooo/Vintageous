from sublime import CLASS_WORD_START
from sublime import CLASS_PUNCTUATION_START
from sublime import CLASS_EMPTY_LINE
from sublime import CLASS_LINE_END

from Vintageous.vi.utils import next_non_white_space_char


CLASS_VI_WORD_START = (CLASS_WORD_START | CLASS_PUNCTUATION_START |
                       CLASS_EMPTY_LINE)
CLASS_VI_INTERNAL_WORD_START = (CLASS_WORD_START | CLASS_PUNCTUATION_START |
                                CLASS_LINE_END)


def next_word_start(view, start, classes=CLASS_VI_WORD_START):
    pt = view.find_by_class(start, forward=True, classes=classes)
    if classes != CLASS_VI_INTERNAL_WORD_START:
        while not (view.line(pt).empty() or
                   view.substr(view.line(pt)).strip()):
            pt = next_word_start(view, pt)
    return pt


def words(view, start, count=1, internal=False):
    assert start >= 0
    assert count > 0

    classes = (CLASS_VI_WORD_START if not internal
                                   else CLASS_VI_INTERNAL_WORD_START)

    pt = start
    for i in range(count):
        pt = next_word_start(view, pt, classes=classes)
        if internal:
            if (i != count - 1):
                if not view.line(pt).empty() and view.classify(pt) & CLASS_LINE_END == CLASS_LINE_END:
                    pt += 1
                    pt = next_non_white_space_char(view, pt, white_space=' \t')

    if internal and view.line(start) != view.line(pt) and not view.line(pt).empty() and view.classify(pt) & CLASS_LINE_END == CLASS_LINE_END:
        pt += 1


    return pt
