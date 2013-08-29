import unittest

# from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
# from Vintageous.vi.constants import MODE_VISUAL
# from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests import BufferTest
from Vintageous.tests import set_text
from Vintageous.tests import add_sel

from Vintageous.vi.units import next_word_end
from Vintageous.vi.units import word_ends
from Vintageous.vi.units import CLASS_VI_INTERNAL_WORD_START


class Test_next_word_end_InNormalMode_FromWhitespace(BufferTest):
    def testToWordStart(self):
        set_text(self.view, '  foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 5)

    def testToPunctuationStart(self):
        set_text(self.view, '  (foo)\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEmptyLine(self):
        set_text(self.view, '  \n\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 5)

    def testToWhitespaceLine(self):
        set_text(self.view, '  \n  \n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 7)

    def testToEofWithNewline(self):
        set_text(self.view, '  \n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEof(self):
        set_text(self.view, '   ')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneWordLine(self):
        set_text(self.view, '   \nfoo\nbar')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 7)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, '   \n foo\nbar')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 8)

    def testToOneCharWord(self):
        set_text(self.view, '  a foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharLine(self):
        set_text(self.view, '  \na\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, '  \n a\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 5)


class Test_next_word_end_InNormalMode_FromWordStart(BufferTest):
    def testToWordStart(self):
        set_text(self.view, 'foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToPunctuationStart(self):
        set_text(self.view, 'foo (bar)\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEmptyLine(self):
        set_text(self.view, 'foo\n\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToWhitespaceLine(self):
        set_text(self.view, 'foo\n  \n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEofWithNewline(self):
        set_text(self.view, 'foo\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEof(self):
        set_text(self.view, 'foo')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneWordLine(self):
        set_text(self.view, 'foo\nbar\nbaz')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n bar\nbaz')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharWord(self):
        set_text(self.view, 'foo a bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharLine(self):
        set_text(self.view, 'foo\na\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n a\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)


class Test_next_word_end_InNormalMode_FromWord(BufferTest):
    def testToWordStart(self):
        set_text(self.view, 'foo bar\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToPunctuationStart(self):
        set_text(self.view, 'foo (bar)\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEmptyLine(self):
        set_text(self.view, 'foo\n\n\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToWhitespaceLine(self):
        set_text(self.view, 'foo\n  \n\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEofWithNewline(self):
        set_text(self.view, 'foo\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEof(self):
        set_text(self.view, 'foo')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneWordLine(self):
        set_text(self.view, 'foo\nbar\nbaz')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n bar\nbaz')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharWord(self):
        set_text(self.view, 'foo a bar\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharLine(self):
        set_text(self.view, 'foo\na\n\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n a\n\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)


class Test_next_word_end_InNormalMode_FromPunctuationStart(BufferTest):
    def testToWordStart(self):
        set_text(self.view, ':foo\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToPunctuationStart(self):
        set_text(self.view, ': (foo)\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToEmptyLine(self):
        set_text(self.view, ':\n\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToWhitespaceLine(self):
        set_text(self.view, ':\n  \n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToEofWithNewline(self):
        set_text(self.view, ':\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToEof(self):
        set_text(self.view, ':')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToOneWordLine(self):
        set_text(self.view, ':\nbar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, ':\n bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToOneCharWord(self):
        set_text(self.view, ':a bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToOneCharLine(self):
        set_text(self.view, ':\na\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, ':\n a\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)


class Test_next_word_end_InNormalMode_FromEmptyLine(BufferTest):
    def testToWordStart(self):
        set_text(self.view, '\nfoo\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToPunctuationStart(self):
        set_text(self.view, '\n (foo)\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEmptyLine(self):
        set_text(self.view, '\n\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToWhitespaceLine(self):
        set_text(self.view, '\n  \n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 5)

    def testToEofWithNewline(self):
        set_text(self.view, '\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToEof(self):
        set_text(self.view, '')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 0)

    def testToOneWordLine(self):
        set_text(self.view, '\nbar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, '\n bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 5)

    def testToOneCharWord(self):
        set_text(self.view, '\na bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneCharLine(self):
        set_text(self.view, '\na\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, '\n a\n\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 3)


class Test_next_word_end_InNormalMode_FromPunctuation(BufferTest):
    def testToWordStart(self):
        set_text(self.view, '::foo\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToPunctuationStart(self):
        set_text(self.view, ':: (foo)\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToEmptyLine(self):
        set_text(self.view, '::\n\n\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToWhitespaceLine(self):
        set_text(self.view, '::\n  \n\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToEofWithNewline(self):
        set_text(self.view, '::\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToEof(self):
        set_text(self.view, '::')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneWordLine(self):
        set_text(self.view, '::\nbar\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, '::\n bar\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneCharWord(self):
        set_text(self.view, '::a bar\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneCharLine(self):
        set_text(self.view, '::\na\n\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, '::\n a\n\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b)
        self.assertEqual(pt, 2)


class Test_next_word_end_InInternalNormalMode_FromWhitespace(BufferTest):
    def testToWhitespaceLine(self):
        set_text(self.view, '  \n  ')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 5)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, '  \n foo')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 7)


class Test_next_word_end_InInternalNormalMode_FromWordStart(BufferTest):
    def testToWhitespaceLine(self):
        set_text(self.view, 'foo\n  ')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 3)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n bar')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 3)


class Test_next_word_end_InInternalNormalMode_FromWord(BufferTest):
    def testToWhitespaceLine(self):
        set_text(self.view, 'foo\n  ')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 3)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n bar')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 3)


class Test_next_word_end_InInternalNormalMode_FromPunctuationStart(BufferTest):
    def testToWhitespaceLine(self):
        set_text(self.view, '.\n  ')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 1)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, '.\n bar')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 1)


class Test_next_word_end_InInternalNormalMode_FromPunctuation(BufferTest):
    def testToWhitespaceLine(self):
        set_text(self.view, '::\n  ')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 2)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, '::\n bar')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 2)


class Test_next_word_end_InInternalNormalMode_FromEmptyLine(BufferTest):
    def testToWhitespaceLine(self):
        set_text(self.view, '\n  ')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 3)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, '\n bar')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = next_word_end(self.view, r.b, internal=True)
        self.assertEqual(pt, 5)


class Test_words_InNormalMode(BufferTest):
    def testMove1(self):
        set_text(self.view, 'foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b)
        self.assertEqual(pt, 2)

    def testMove2(self):
        set_text(self.view, 'foo bar fizz\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, count=2)
        self.assertEqual(pt, 6)

    def testMove10(self):
        set_text(self.view, ''.join(('foo bar\n',) * 5))
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, count=9)
        self.assertEqual(pt, 34)


class Test_words_InInternalNormalMode_FromEmptyLine(BufferTest):
    # We can assume the stuff tested for normal mode applies to internal normal mode, so we
    # don't bother with that. Instead, we only test the differing behavior when advancing by
    # word starts in internal normal.
    def testMove1ToLineWithLeadingWhiteSpace(self):
        set_text(self.view, '\n bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True)
        self.assertEqual(pt, 4)

    def testMove2ToLineWithLeadingWhiteSpace(self):
        set_text(self.view, '\n bar')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, count=2, internal=True)
        self.assertEqual(pt, 6)

    def testMove1ToWhitespaceLine(self):
        set_text(self.view, '\n  \n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, count=1, internal=True)
        self.assertEqual(pt, 3)

    def testMove2ToOneWordLine(self):
        set_text(self.view, '\nfoo\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 4)

    def testMove3AndSwallowLastNewlineChar(self):
        set_text(self.view, '\nfoo\n bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=3)
        self.assertEqual(pt, 9)

    def testMove2ToLineWithLeadingWhiteSpace(self):
        set_text(self.view, '\nfoo\n  \n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 7)


class Test_words_InInternalNormalMode_FromOneWordLine(BufferTest):
    # We can assume the stuff tested for normal mode applies to internal normal mode, so we
    # don't bother with that. Instead, we only test the differing behavior when advancing by
    # word starts in internal normal.
    def testMove1ToEol(self):
        set_text(self.view, 'foo\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=1)
        self.assertEqual(pt, 2)

    def testMove2ToLineWithLeadingWhiteSpaceFromWordStart(self):
        set_text(self.view, 'foo\n\nbar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 7)

    def testMove2ToEmptyLineFromWord(self):
        set_text(self.view, 'foo\n\nbar\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 7)

    def testMove2ToOneWordLineFromWordStart(self):
        set_text(self.view, 'foo\nbar\nccc\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 6)

    def testMove2ToOneWordLineFromWord(self):
        set_text(self.view, 'foo\nbar\nccc\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 6)

    def testMove2ToWhitespaceline(self):
        set_text(self.view, 'foo\n  \nccc\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 9)

    def testMove2ToWhitespacelineFollowedByLeadingWhitespaceFromWord(self):
        set_text(self.view, 'foo\n  \n ccc\n')
        r = self.R((0, 1), (0, 1))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 10)

    def testMove2ToWhitespacelineFollowedByLeadingWhitespaceFromWordStart(self):
        set_text(self.view, 'foo\n  \n ccc\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 10)


class Test_word_ends_InInternalNormalMode_FromOneCharLongWord(BufferTest):
    def testMove1ToEol(self):
        set_text(self.view, 'x\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=1)
        self.assertEqual(pt, 0)

    def testMove2ToEol(self):
        set_text(self.view, 'a x\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 2)


class Test_words_InInternalNormalMode_FromLine(BufferTest):
    def testMove2ToEol(self):
        set_text(self.view, 'foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_sel(self.view, r)

        pt = word_ends(self.view, r.b, internal=True, count=2)
        self.assertEqual(pt, 6)
