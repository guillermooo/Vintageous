import unittest

# from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
# from Vintageous.vi.constants import MODE_VISUAL
# from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests.commands import BufferTest
from Vintageous.tests.commands import set_text
from Vintageous.tests.commands import add_selection

from Vintageous.vi.units import next_big_word_start
from Vintageous.vi.units import big_words
from Vintageous.vi.units import CLASS_VI_INTERNAL_BIG_WORD_START
from Vintageous.vi.units import CLASS_VI_BIG_WORD_START


class Test_next_big_word_start_InNormalMode(BufferTest):
    def testFromPunctuationStartToNextWord(self):
        set_text(self.view, ' (foo) bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 7)

    def testFromPunctuationStartToNextPunctuation(self):
        set_text(self.view, ' (foo) (bar)\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 7)

    def testFromWordStartToNextPunctuation(self):
        set_text(self.view, 'foo (bar)\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testFromWordStartToToNextWord(self):
        set_text(self.view, 'foo, bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 5)

    def testFromWordToToNextWord(self):
        set_text(self.view, 'foo, bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 5)

    def testFromWordToToNextPunctuation(self):
        set_text(self.view, 'foo (bar)\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testFromSpaceToNextPunctuation(self):
        set_text(self.view, '  (bar)\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testFromEmptyLineToNextPunctuation(self):
        set_text(self.view, '\n...\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 1)

    def testFromEmptyLineToNextPunctuationLedByWhiteSpace(self):
        set_text(self.view, '\n  ...\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testFromWhitespaceLineToNextPunctuation(self):
        set_text(self.view, '   \n...\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    @unittest.skip("FIXME: Sublime Text bug in classify at BOF.")
    def testFromPunctuationStartAtBofToNextWord(self):
        set_text(self.view, '(foo) bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 15)

    def testMoveToNextAlphabeticWord(self):
        set_text(self.view, 'foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testMoveToNextNumericWord(self):
        set_text(self.view, 'foo 123\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testMoveToNextAlphaNumericWord(self):
        set_text(self.view, 'foo bar123\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 4)

    def testMoveToNextAlphabeticWordSkippingWhiteSpace(self):
        set_text(self.view, 'foo  \tbar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, 0)
        self.assertEqual(pt, 6)

    def testMoveToNextWordAtEol(self):
        set_text(self.view, 'foo bar\nfoo bar\n')
        r = self.R((0, 4), (0, 4))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 8)

    def testMoveToNextWordAtEolSkippingWhiteSpaceInNextLine(self):
        set_text(self.view, 'foo bar\n  foo bar\n')
        r = self.R((0, 4), (0, 4))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 10)

    def testMoveToNextWordAtEolSkippingWhiteSpaceInCurrentLine(self):
        set_text(self.view, 'foo bar  \nfoo bar\n')
        r = self.R((0, 4), (0, 4))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 10)

    def testMoveToNextWordAtEolSkippingWhiteSpaceInBothLines(self):
        set_text(self.view, 'foo bar  \n  foo bar\n')
        r = self.R((0, 4), (0, 4))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 12)

    def testSkipNextPunctuationFromAlphanumericWord(self):
        set_text(self.view, 'foo, bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 5)

    def testMoveToNextPunctuationFromPunctuation(self):
        set_text(self.view, 'foo, (bar)\n')
        r = self.R((0, 3), (0, 3))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 5)

    def testMoveToNextEmptyLine(self):
        set_text(self.view, 'foo bar\n\nfoo bar')
        r = self.R((0, 4), (0, 4))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 8)

    def testMoveToNextWordFromWhiteSpace(self):
        set_text(self.view, '  foo bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 2)

    def testMoveToNextEmptyLineFromWhiteSpace(self):
        set_text(self.view, '  \n\nfoo bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 3)

    def testMoveToNextWordSkippingWhiteSpaceOnlyLine(self):
        set_text(self.view, 'foo bar\n\t  \nfoo bar')
        r = self.R((0, 5), (0, 5))
        add_selection(self.view, r)
        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 12)

    def testMoveToNextEmptyLineSkippingWhiteSpaceOnlyLine(self):
        set_text(self.view, 'foo bar\n\t  \n\nfoo bar')
        r = self.R((0, 5), (0, 5))
        add_selection(self.view, r)
        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 12)

    def testSkipNextInterpunctuation(self):
        set_text(self.view, 'foo-bar\nfoo')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)
        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 8)

    # Perhaps this one depends on the user configuration ('word_separators').
    def testMoveToNextWordSkippingUnderscores(self):
        set_text(self.view, 'foo_bar foo bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)
        pt = next_big_word_start(self.view, r.b)
        self.assertEqual(pt, 8)


class Test_big_words_InNormalMode(BufferTest):
    def testMoveToNextAlphabeticWord(self):
        # FIXME: Sublime Text bug: can't classify at BOF.
        set_text(self.view, ' (foo)... bar... foo bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = big_words(self.view, r.b, count=2)
        self.assertEqual(pt, 17)


class Test_next_big_word_start_InInternalMode(BufferTest):
    def testFromPunctuationStartToNextWord(self):
        set_text(self.view, ' (foo) bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 7)

    def testFromPunctuationStartToNextPunctuation(self):
        set_text(self.view, ' (foo) (bar)\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 7)

    def testFromWordStartToNextPunctuation(self):
        set_text(self.view, 'foo (bar)\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 4)

    def testFromWordStartToToNextWord(self):
        set_text(self.view, 'foo, bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 5)

    def testFromWordToToNextWord(self):
        set_text(self.view, 'foo, bar\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 5)

    def testFromWordToToNextPunctuation(self):
        set_text(self.view, 'foo (bar)\n')
        r = self.R((0, 1), (0, 1))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 4)

    def testFromSpaceToNextPunctuation(self):
        set_text(self.view, '  (bar)\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 2)

    def testFromEmptyLineToNextPunctuation(self):
        set_text(self.view, '\n...\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 1)

    def testFromEmptyLineToNextPunctuationLedByWhiteSpace(self):
        set_text(self.view, '\n  ...\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 3)

    def testFromWhitespaceLineToNextPunctuation(self):
        set_text(self.view, '   \n...\n\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 3)

    @unittest.skip("FIXME: Sublime Text bug in classify at BOF.")
    def testFromPunctuationStartAtBofToNextWord(self):
        set_text(self.view, '(foo) bar\n')
        r = self.R((0, 0), (0, 0))
        add_selection(self.view, r)

        pt = next_big_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
        self.assertEqual(pt, 15)
#     def testMoveToNextAlphabeticWord(self):
#         set_text(self.view, 'Xoo bar\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 4)

#     def testMoveToNextNumericWord(self):
#         set_text(self.view, 'Xoo 123\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 4)

#     def testMoveToNextAlphanumericWord(self):
#         set_text(self.view, 'Xoo bar123\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 4)

#     def testMoveToNextAlphabeticWordSkippingWhiteSpace(self):
#         set_text(self.view, 'Xoo  \tbar\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 6)

#     def testMoveToEolIfAtLastWordInLine(self):
#         set_text(self.view, 'foo Xar\nfoo bar\n')
#         r = self.R((0, 4), (0, 4))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 7)

#     def testMoveToEolIfNextLineLedByWhiteSpace(self):
#         set_text(self.view, 'foo Xar\n  foo bar\n')
#         r = self.R((0, 4), (0, 4))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 7)

#     def testMoveToEolIfTrailingWhiteSpaceInCurrentLine(self):
#         set_text(self.view, 'foo Xar  \nfoo bar\n')
#         r = self.R((0, 4), (0, 4))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 9)

#     def testMoveToEolIfTrailingWhiteSpaceInCurrentLineAndLeadingWhiteSpaceInNextLine(self):
#         set_text(self.view, 'foo Xar  \n  foo bar\n')
#         r = self.R((0, 4), (0, 4))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 9)

#     def testSkipNextPunctuationFromAlphanumericWord(self):
#         set_text(self.view, 'Xoo, bar\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 5)

#     def testMoveToNextPunctuationFromPunctuation(self):
#         set_text(self.view, 'foo, (bar)\n')
#         r = self.R((0, 3), (0, 3))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 5)

#     def testMoveToNextEmptyLine(self):
#         set_text(self.view, 'foo Xar\n\nfoo bar')
#         r = self.R((0, 4), (0, 4))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 7)

#     def testMoveToNextWordFromWhiteSpace(self):
#         set_text(self.view, '  foo bar\n')
#         r = self.R((0, 1), (0, 1))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 2)

#     def testMoveToEolFromWhiteSpaceLineFollowedByNonEmptyLineFollowedByNonWhiteSpaceLine(self):
#         set_text(self.view, '  \n\nfoo bar\n')
#         r = self.R((0, 1), (0, 1))
#         add_selection(self.view, r)

#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 2)

#     def testMoveToEolIfFollowedByWhiteSpaceOnlyLine(self):
#         set_text(self.view, 'foo bXr\n\t  \nfoo bar')
#         r = self.R((0, 5), (0, 5))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 7)

#     def testMoveToEolIfWhiteSpaceOnlyLineFollowedByEmptyLine(self):
#         set_text(self.view, 'foo bXr\n\t  \n\nfoo bar')
#         r = self.R((0, 5), (0, 5))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 7)

#     def testSkipNextInterpunctuation(self):
#         set_text(self.view, 'Xoo-bar foo\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 7)

#     # Perhaps this one depends on the user configuration ('word_separators').
#     def testMoveToNextWordSkippingUnderscores(self):
#         set_text(self.view, 'Xoo_bar foo bar\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 8)

#     def testMoveToEolIfAtLastNonWhiteSpaceCharacterInLine(self):
#         set_text(self.view, 'foo baX\n')
#         r = self.R((0, 6), (0, 6))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 7)

#     def testMoveToEndOfInterPunctuationIfAtInterpunctuation(self):
#         set_text(self.view, 'foo-bar\n')
#         r = self.R((0, 3), (0, 3))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 4)

#     def testMoveToEndOfLongInterPunctuationIfAtInterpunctuation(self):
#         set_text(self.view, 'foo-.!?bar\n')
#         r = self.R((0, 3), (0, 3))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 7)

#     def testMoveToEndOfLineIfEmptyLine(self):
#         set_text(self.view, '\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 1)

#     def testMoveToEndOfLineIfEmptyLineFollowedByEmptyLine(self):
#         set_text(self.view, '\n\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 1)

#     def testMoveToEndOfLineIfEmptyLineBetweenEmptyLines(self):
#         set_text(self.view, '\n\n\n')
#         r = self.R((0, 1), (0, 1))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 2)

#     def testMoveToEolIfWhiteSpaceOnlyLine(self):
#         set_text(self.view, '  \t\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)
#         pt = next_word_start(self.view, r.b, classes=CLASS_VI_INTERNAL_BIG_WORD_START)
#         self.assertEqual(pt, 3)


# class Test_big_words_InInternalNormalMode(BufferTest):
#     def testAdvanceTwoWordsInSameLine(self):
#         set_text(self.view, 'foo bar foo bar\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = words(self.view, r.b, count=2, internal=True)
#         self.assertEqual(pt, 8)

#     def testAdvanceThreeWordsInSameLine(self):
#         set_text(self.view, 'foo bar foo bar\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = words(self.view, r.b, count=3, internal=True)
#         self.assertEqual(pt, 12)

#     def testFromLastWordInLineToNextWord(self):
#         set_text(self.view, 'foo bar\nfoo bar\n')
#         r = self.R((0, 5), (0, 5))
#         add_selection(self.view, r)

#         pt = words(self.view, r.b, count=2, internal=True)
#         self.assertEqual(pt, 12)

#     def testFromLastWordInLineFollowedByWhiteSpaceToNextWord(self):
#         set_text(self.view, 'foo bar  \nxxx yyy\n')
#         r = self.R((0, 4), (0, 4))
#         add_selection(self.view, r)

#         pt = words(self.view, r.b, count=2, internal=True)
#         self.assertEqual(pt, 14)

#     def testFromLastWordInLineToNextWordLedByWhiteSpace(self):
#         set_text(self.view, 'foo bar\n  xxx yyy\n')
#         r = self.R((0, 4), (0, 4))
#         add_selection(self.view, r)

#         pt = words(self.view, r.b, count=2, internal=True)
#         self.assertEqual(pt, 14)

#     def testTreatEmptyLinesAsWords(self):
#         set_text(self.view, '\n\n\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = words(self.view, r.b, count=2, internal=True)
#         self.assertEqual(pt, 2)

#     def testSkipWhiteSpaceInLineIfCountGreaterThanOne(self):
#         set_text(self.view, '   \n\n\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = words(self.view, r.b, count=2, internal=True)
#         self.assertEqual(pt, 5)

#     def testFromWhiteSpaceIncludeLastNewLineIfMovingLineWiseAndHitsEol(self):
#         set_text(self.view, '   \nfoo bar\n   xxx yyy')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = words(self.view, r.b, count=3, internal=True)
#         self.assertEqual(pt, 12)

#     def testFromEmptyLineDontEatUpWhiteSpaceIfMovingOne(self):
#         set_text(self.view, '\n   foo bar\n')
#         r = self.R((0, 0), (0, 0))
#         add_selection(self.view, r)

#         pt = words(self.view, r.b, count=1, internal=True)
#         self.assertEqual(pt, 1)
