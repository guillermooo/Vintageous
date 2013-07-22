import unittest

# from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
# from Vintageous.vi.constants import MODE_VISUAL
# from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests.commands import BufferTest
from Vintageous.tests.commands import set_text
from Vintageous.tests.commands import add_selection

from Vintageous.vi.units import next_word_start
from Vintageous.vi.units import words
from Vintageous.vi.units import CLASS_VI_INTERNAL_WORD_START


class Test_next_word_start_InNormalMode_FromWhitespace(BufferTest):
    def testToWordStart(self):
        set_text(self.view, '  foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToPunctuationStart(self):
        set_text(self.view, '  (foo)\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToEmptyLine(self):
        set_text(self.view, '  \n\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToWhitespaceLine(self):
        set_text(self.view, '  \n  \n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 6)

    def testToEofWithNewline(self):
        set_text(self.view, '  \n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEof(self):
        set_text(self.view, '   ')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneWordLine(self):
        set_text(self.view, '   \nfoo\nbar')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, '   \n foo\nbar')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 5)

    def testToOneCharWord(self):
        set_text(self.view, '  a foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneCharLine(self):
        set_text(self.view, '  \na\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, '  \n a\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)


class Test_next_word_start_InNormalMode_FromWordStart(BufferTest):
    def testToWordStart(self):
        set_text(self.view, 'foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToPunctuationStart(self):
        set_text(self.view, 'foo (bar)\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToEmptyLine(self):
        set_text(self.view, 'foo\n\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToWhitespaceLine(self):
        set_text(self.view, 'foo\n  \n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 7)

    def testToEofWithNewline(self):
        set_text(self.view, 'foo\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToEof(self):
        set_text(self.view, 'foo')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneWordLine(self):
        set_text(self.view, 'foo\nbar\nbaz')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n bar\nbaz')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 5)

    def testToOneCharWord(self):
        set_text(self.view, 'foo a bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneCharLine(self):
        set_text(self.view, 'foo\na\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n a\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 5)


class Test_next_word_start_InNormalMode_FromWord(BufferTest):
    def testToWordStart(self):
        set_text(self.view, 'foo bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToPunctuationStart(self):
        set_text(self.view, 'foo (bar)\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToEmptyLine(self):
        set_text(self.view, 'foo\n\n\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToWhitespaceLine(self):
        set_text(self.view, 'foo\n  \n\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 7)

    def testToEofWithNewline(self):
        set_text(self.view, 'foo\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToEof(self):
        set_text(self.view, 'foo')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneWordLine(self):
        set_text(self.view, 'foo\nbar\nbaz')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n bar\nbaz')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 5)

    def testToOneCharWord(self):
        set_text(self.view, 'foo a bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneCharLine(self):
        set_text(self.view, 'foo\na\n\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, 'foo\n a\n\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 5)


class Test_next_word_start_InNormalMode_FromPunctuationStart(BufferTest):
    def testToWordStart(self):
        set_text(self.view, ':foo\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToPunctuationStart(self):
        set_text(self.view, ': (foo)\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToEmptyLine(self):
        set_text(self.view, ':\n\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToWhitespaceLine(self):
        set_text(self.view, ':\n  \n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 5)

    def testToEofWithNewline(self):
        set_text(self.view, ':\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToEof(self):
        set_text(self.view, ':')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToOneWordLine(self):
        set_text(self.view, ':\nbar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, ':\n bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharWord(self):
        set_text(self.view, ':a bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 1)

    def testToOneCharLine(self):
        set_text(self.view, ':\na\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, ':\n a\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)


class Test_next_word_start_InNormalMode_FromPunctuation(BufferTest):
    def testToWordStart(self):
        set_text(self.view, '::foo\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToPunctuationStart(self):
        set_text(self.view, ':: (foo)\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEmptyLine(self):
        set_text(self.view, '::\n\n\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToWhitespaceLine(self):
        set_text(self.view, '::\n  \n\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 6)

    def testToEofWithNewline(self):
        set_text(self.view, '::\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToEof(self):
        set_text(self.view, '::')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneWordLine(self):
        set_text(self.view, '::\nbar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneWordLineWithLeadingWhitespace(self):
        set_text(self.view, '::\n bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testToOneCharWord(self):
        set_text(self.view, '::a bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testToOneCharLine(self):
        set_text(self.view, '::\na\n\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testToOneCharLineWithLeadingWhitespace(self):
        set_text(self.view, '::\n a\n\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_word_start(self.view, r.b)
        self.assertEqual(pt, 4)
