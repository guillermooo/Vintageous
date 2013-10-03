import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import BufferTest

from Vintageous.vi.text_objects import find_prev_lone_bracket
from Vintageous.vi.text_objects import find_next_lone_bracket
from Vintageous.vi.search import reverse_search_by_pt


class Test_find_prev_lone_bracket_SingleLine_Flat(BufferTest):
    def testReturnsNoneIfNoPreviousLoneBracket(self):
        set_text(self.view, 'abc')

        region = find_prev_lone_bracket(self.view, 1, ('\\{', '\\}'))
        self.assertIsNone(region)

    # TODO: Fix this.
    # Vim finds the current opening bracket if the caret is at its index.
    def testCanFindPreviousLoneBracketAtSelfPosition(self):
        set_text(self.view,'a{b}c')
        add_sel(self.view, self.R(1, 1))

        region = find_prev_lone_bracket(self.view, 1, ('\\{', '\\}'))
        self.assertEqual(region, self.R(1, 2))

    def testCanFindPreviousLoneBracketAtBof(self):
        set_text(self.view,'{ab}c')

        region = find_prev_lone_bracket(self.view, 2, ('\\{', '\\}'))
        self.assertEqual(region, self.R(0, 1))

    def testReturnsNoneIfNoPreviousLoneBracketButLineHasBrackets(self):
        set_text(self.view,'abc{ab}c')

        region = find_prev_lone_bracket(self.view, 2, ('\\{', '\\}'))
        self.assertEqual(region, None)

    def testReturnsNoneIfCaretAfterAllBracketPairs(self):
        set_text(self.view,'ab{cd}efg')

        region = find_prev_lone_bracket(self.view, 7, ('\\{', '\\}'))
        self.assertEqual(region, None)

    def testFindsUnbalancedBracket(self):
        set_text(self.view,'a{bc')

        region = find_prev_lone_bracket(self.view, 3, ('\\{', '\\}'))
        self.assertEqual(region, self.R(1, 2))


class Test_find_prev_lone_bracket_SingleLine_Nested(BufferTest):
    def testFindsOuterFromRhs(self):
        set_text(self.view, 'foo {bar {foo} bar}')

        region = find_prev_lone_bracket(self.view, 16, ('\\{', '\\}'))
        self.assertEqual(region, self.R(4, 5))

    def testFindsOuterFromLhs(self):
        set_text(self.view, 'foo {bar {foo} bar}')

        region = find_prev_lone_bracket(self.view, 7, ('\\{', '\\}'))
        self.assertEqual(region, self.R(4, 5))

    def testFindsInner(self):
        set_text(self.view, 'foo {bar {foo} bar}')

        region = find_prev_lone_bracket(self.view, 13, ('\\{', '\\}'))
        self.assertEqual(region, self.R(9, 10))

    def testFindsOuterIfUnbalancedOuter(self):
        set_text(self.view, 'foo {bar {foo} bar')

        region = find_prev_lone_bracket(self.view, 16, ('\\{', '\\}'))
        self.assertEqual(region, self.R(4, 5))

    def testFindsInnerIfUnbalancedOuter(self):
        set_text(self.view, 'foo {bar {foo} bar')

        region = find_prev_lone_bracket(self.view, 12, ('\\{', '\\}'))
        self.assertEqual(region, self.R(9, 10))


class Test_find_prev_lone_bracket_MultipleLines_Flat(BufferTest):
    def testReturnsNoneIfNoPreviousLoneBracket(self):
        set_text(self.view, 'foo\nbar')

        region = find_prev_lone_bracket(self.view, 5, ('\\{', '\\}'))
        self.assertIsNone(region)

    # TODO: Fix this.
    # Vim finds the current opening bracket if the caret is at its index.
    def testCanFindPreviousLoneBracketAtSelfPosition(self):
        set_text(self.view,'a{\nb}c')
        add_sel(self.view, self.R(1, 1))

        region = find_prev_lone_bracket(self.view, 1, ('\\{', '\\}'))
        self.assertEqual(region, self.R(1, 2))

    def testCanFindPreviousLoneBracketAtBof(self):
        set_text(self.view,'{a\nb}c')

        region = find_prev_lone_bracket(self.view, 2, ('\\{', '\\}'))
        self.assertEqual(region, self.R(0, 1))

    def testReturnsNoneIfNoPreviousLoneBracketButLineHasBrackets(self):
        set_text(self.view,'abc{a\nb}c')

        region = find_prev_lone_bracket(self.view, 2, ('\\{', '\\}'))
        self.assertIsNone(region)

    def testReturnsNoneIfCaretAfterAllBracketPairs(self):
        set_text(self.view,'ab{c\nd}efg')

        region = find_prev_lone_bracket(self.view, 7, ('\\{', '\\}'))
        self.assertIsNone(region)

    def testFindsUnbalancedBracket(self):
        set_text(self.view,'a{\nbc')

        region = find_prev_lone_bracket(self.view, 4, ('\\{', '\\}'))
        self.assertEqual(region, self.R(1, 2))


class Test_find_prev_lone_bracket_MultipleLines_Nested(BufferTest):
    def testFindsOuterFromRhs(self):
        set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo}')

        region = find_prev_lone_bracket(self.view, 20, ('\\{', '\\}'))
        self.assertEqual(region, self.R(4, 5))

    def testFindsOuterFromLhs(self):
        set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo}')

        region = find_prev_lone_bracket(self.view, 7, ('\\{', '\\}'))
        self.assertEqual(region, self.R(4, 5))

    def testFindsInner(self):
        set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo}')

        region = find_prev_lone_bracket(self.view, 13, ('\\{', '\\}'))
        self.assertEqual(region, self.R(9, 10))

    def testFindsOuterIfUnbalancedOuter(self):
        set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo')

        region = find_prev_lone_bracket(self.view, 20, ('\\{', '\\}'))
        self.assertEqual(region, self.R(4, 5))

    def testFindsInnerIfUnbalancedOuter(self):
        set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo')

        region = find_prev_lone_bracket(self.view, 16, ('\\{', '\\}'))
        self.assertEqual(region, self.R(9, 10))


class Test_find_find_next_lone_bracket_MultipleLines_Nested(BufferTest):
    # def testFindsOuterFromRhs(self):
    #     set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo}')

    #     region = find_next_lone_bracket(self.view, 20, ('\\{', '\\}'))
    #     self.assertEqual(region, self.R(4, 5))

    # def testFindsOuterFromLhs(self):
    #     set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo}')

    #     region = find_next_lone_bracket(self.view, 8, ('\\{', '\\}'))
    #     self.assertEqual(region, self.R(4, 5))

    def testFindsOuterFromLhs_DeeplyNested(self):
        set_text(self.view, 'foo {bar\n{foo\nbar {foo} bar}\nfoo}')

        region = find_next_lone_bracket(self.view, 7, ('\\{', '\\}'))
        self.assertEqual(region, self.R(32, 33))

    # def testFindsInner(self):
    #     set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo}')

    #     region = find_next_lone_bracket(self.view, 13, ('\\{', '\\}'))
    #     self.assertEqual(region, self.R(9, 10))

    # def testFindsOuterIfUnbalancedOuter(self):
    #     set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo')

    #     region = find_next_lone_bracket(self.view, 20, ('\\{', '\\}'))
    #     self.assertEqual(region, self.R(4, 5))

    # def testFindsInnerIfUnbalancedOuter(self):
    #     set_text(self.view, 'foo {bar\n{foo\nbar}\nfoo')

    #     region = find_next_lone_bracket(self.view, 16, ('\\{', '\\}'))
    #     self.assertEqual(region, self.R(9, 10))
