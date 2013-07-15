import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests.commands import set_text
from Vintageous.tests.commands import add_selection
from Vintageous.tests.commands import get_sel
from Vintageous.tests.commands import first_sel
from Vintageous.tests.commands import make_region_at_row
from Vintageous.tests.commands import BufferTest


# TODO: Test against folded regions.
# TODO: Ensure that we only create empty selections while testing. Add assert_all_sels_empty()?
# TODO: Test different values for xpos in combination with the starting col.
class Test_vi_k_InNormalMode(BufferTest):
    def testMoveOne(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_selection(self.view, make_region_at_row(self.view, row=1, col=1, size=0))

        self.view.run_command('_vi_k', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 1})

        expected = make_region_at_row(self.view, row=0, col=1, size=0)
        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_selection(self.view, make_region_at_row(self.view, row=2, col=1, size=0))

        self.view.run_command('_vi_k', {'mode': MODE_NORMAL, 'count': 2, 'xpos': 1})

        expected = make_region_at_row(self.view, row=0, col=1, size=0)
        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoLongerLine(self):
        set_text(self.view, 'foo bar\nfoo')
        add_selection(self.view, make_region_at_row(self.view, row=1, col=1, size=0))

        self.view.run_command('_vi_k', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 1})

        expected = make_region_at_row(self.view, row=0, col=1, size=0)
        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoShorterLine(self):
        set_text(self.view, 'foo\nfoo bar')
        add_selection(self.view, make_region_at_row(self.view, row=1, col=5, size=0))

        self.view.run_command('_vi_k', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 5})

        expected = make_region_at_row(self.view, row=0, col=2, size=0)
        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLine(self):
        set_text(self.view, 'foo\n\n')
        add_selection(self.view, make_region_at_row(self.view, row=1, col=0, size=0))

        self.view.run_command('_vi_k', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 1})

        expected = make_region_at_row(self.view, row=0, col=1, size=0)
        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLineToEmptyLine(self):
        set_text(self.view, '\n\n\n')
        add_selection(self.view, make_region_at_row(self.view, row=1, col=0, size=0))

        self.view.run_command('_vi_k', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 0})

        expected = make_region_at_row(self.view, row=0, col=0, size=0)
        self.assertEqual(expected, first_sel(self.view))

    def testMoveTooFar(self):
        set_text(self.view, 'foo\nbar\nbaz\n')
        add_selection(self.view, make_region_at_row(self.view, row=2, col=1, size=0))

        self.view.run_command('_vi_k', {'mode': MODE_NORMAL, 'count': 100, 'xpos': 1})

        expected = make_region_at_row(self.view, row=0, col=1, size=0)
        self.assertEqual(expected, first_sel(self.view))


class Test_vi_k_InVisualMode(BufferTest):
    def testMoveOne(self):
        set_text(self.view, 'foo\nbar\nbaz\n')
        add_selection(self.view, self.R((1, 1), (1, 2)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 2})

        expected = self.R((1, 2), (0, 2))
        self.assertEqual(expected, first_sel(self.view))

    def testMoveOppositeEndGreaterWithSelOfSize1(self):
        set_text(self.view, 'foo\nbar\nbaz\n')
        add_selection(self.view, self.R((2, 1), (2, 2)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 2})

        expected = self.R((2, 2), (1, 2))
        self.assertEqual(expected, first_sel(self.view))

    def testMoveOppositeEndSmallerWithSelOfSize2(self):
        set_text(self.view, 'foo\nbar\nbaz\n')
        add_selection(self.view, self.R((1, 1), (1, 3)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 3})

        expected = self.R((1, 2), (0, 3))
        self.assertEqual(expected, first_sel(self.view))

    def testMoveOppositeEndSmallerWithSelOfSize3(self):
        set_text(self.view, 'foobar\nbarfoo\nbuzzfizz\n')
        add_selection(self.view, self.R((1, 1), (1, 4)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 3})

        expected = self.R((1, 2), (0, 3))
        self.assertEqual(expected, first_sel(self.view))

    def testMove_OppositeEndSmaller_DifferentLines_NoCrossOver(self):
        set_text(self.view, 'foo\nbar\nbaz\n')
        add_selection(self.view, self.R((0, 1), (2, 1)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 1})

        expected = self.R((0, 1), (1, 2))
        self.assertEqual(expected, first_sel(self.view))

    def testMove_OppositeEndSmaller_DifferentLines_CrossOver_XposAt0(self):
        set_text(self.view, 'foo\nbar\nbaz\n')
        add_selection(self.view, self.R((1, 0), (2, 1)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 2, 'xpos': 0})

        expected = self.R((1, 1), (0, 0))
        self.assertEqual(expected, first_sel(self.view))

    def testMove_OppositeEndSmaller_DifferentLines_CrossOver_Non0Xpos(self):
        set_text(self.view, 'foo bar\nfoo bar\nfoo bar\n')
        add_selection(self.view, self.R((1, 4), (2, 4)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 2, 'xpos': 4})

        expected = self.R((1, 5), (0, 4))
        self.assertEqual(expected, first_sel(self.view))

    def testMoveBackToSameLineSameXpos(self):
        set_text(self.view, 'foo\nbar\nbaz\n')
        add_selection(self.view, self.R((0, 1), (1, 1)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 1})

        expected = self.R((0, 2), (0, 1))
        self.assertEqual(expected, first_sel(self.view))

    def testMoveBackToSameLine_OppositeEndHasGreaterXpos(self):
        set_text(self.view, 'foo\nbar\nbaz\n')
        add_selection(self.view, self.R((0, 2), (1, 0)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 0})

        expected = self.R((0, 3), (0, 0))
        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany_OppositeEndGreater_FromSameLine(self):
        set_text(self.view, ''.join(('foo\n',) * 50))
        add_selection(self.view, self.R((20, 2), (20, 1)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 10, 'xpos': 1})

        expected = self.R((20, 2), (10, 1))
        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany_OppositeEndGreater_DifferentLines(self):
        set_text(self.view, ''.join(('foo\n',) * 50))
        add_selection(self.view, self.R((21, 2), (20, 1)))

        self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 10, 'xpos': 1})

        expected = self.R((21, 2), (10, 1))
        self.assertEqual(expected, first_sel(self.view))

#     def testMoveMany(self):
#         set_text(self.view, ''.join(('abc\n',) * 60))
#         add_selection(self.view, a=1, b=2)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 50, 'xpos': 1})

#         target = self.view.text_point(50, 2)
#         expected = self.R(1, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveOntoLongerLine(self):
#         set_text(self.view, 'foo\nfoo bar\nfoo bar')
#         add_selection(self.view, a=1, b=2)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 1})

#         target = self.view.text_point(1, 2)
#         expected = self.R(1, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveOntoShorterLine(self):
#         set_text(self.view, 'foo bar\nfoo\nbar')
#         add_selection(self.view, a=5, b=6)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 5})

#         target = self.view.text_point(1, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(5, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveFromEmptyLine(self):
#         set_text(self.view, '\nfoo\nbar')
#         add_selection(self.view, a=0, b=1)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 0})

#         target = self.view.text_point(1, 1)
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveFromEmptyLineToEmptyLine(self):
#         set_text(self.view, '\n\nbar')
#         add_selection(self.view, a=0, b=1)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 0})

#         target = self.view.text_point(1, 1)
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveTooFar(self):
#         set_text(self.view, 'foo\nbar\nbaz')
#         add_selection(self.view, a=1, b=2)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL, 'count': 10000, 'xpos': 1})

#         target = self.view.text_point(2, 2)
#         expected = self.R(1, target)

#         self.assertEqual(expected, first_sel(self.view))


# # TODO: Ensure that we only create empty selections while testing. Add assert_all_sels_empty()?
# class Test_vi_k_InInternalNormalMode(BufferTest):
#     def testMoveOne(self):
#         set_text(self.view, 'abc\nabc\nabc')
#         add_selection(self.view, a=1, b=1)

#         self.view.run_command('_vi_k', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 1})

#         target = self.view.text_point(1, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveMany(self):
#         set_text(self.view, ''.join(('abc\n',) * 60))
#         add_selection(self.view, a=1, b=1)

#         self.view.run_command('_vi_k', {'mode': _MODE_INTERNAL_NORMAL, 'count': 50, 'xpos': 1})

#         target = self.view.text_point(50, 2)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveOntoLongerLine(self):
#         set_text(self.view, 'foo\nfoo bar\nfoo bar')
#         add_selection(self.view, a=1, b=1)

#         self.view.run_command('_vi_k', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 1})

#         target = self.view.text_point(1, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveOntoShorterLine(self):
#         set_text(self.view, 'foo bar\nfoo\nbar')
#         add_selection(self.view, a=5, b=5)

#         self.view.run_command('_vi_k', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 5})

#         target = self.view.text_point(1, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveFromEmptyLine(self):
#         set_text(self.view, '\nfoo\nbar')
#         add_selection(self.view, a=0, b=0)

#         self.view.run_command('_vi_k', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 0})

#         target = self.view.text_point(1, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveFromEmptyLineToEmptyLine(self):
#         set_text(self.view, '\n\nbar')
#         add_selection(self.view, a=0, b=0)

#         self.view.run_command('_vi_k', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 0})

#         target = self.view.text_point(1, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveTooFar(self):
#         set_text(self.view, 'foo\nbar\nbaz')
#         add_selection(self.view, a=1, b=1)

#         self.view.run_command('_vi_k', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10000, 'xpos': 1})

#         target = self.view.text_point(2, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))


# class Test_vi_k_InVisualLineMode(BufferTest):
#     def testMoveOne(self):
#         set_text(self.view, 'abc\nabc\nabc')
#         add_selection(self.view, a=0, b=4)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL_LINE, 'count': 1, 'xpos': 1})

#         target = self.view.text_point(1, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveMany(self):
#         set_text(self.view, ''.join(('abc\n',) * 60))
#         add_selection(self.view, a=0, b=4)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL_LINE, 'count': 50, 'xpos': 1})

#         target = self.view.text_point(50, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveFromEmptyLine(self):
#         set_text(self.view, '\nfoo\nbar')
#         add_selection(self.view, a=0, b=1)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL_LINE, 'count': 1, 'xpos': 0})

#         target = self.view.text_point(1, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveFromEmptyLineToEmptyLine(self):
#         set_text(self.view, '\n\nbar')
#         add_selection(self.view, a=0, b=1)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL_LINE, 'count': 1, 'xpos': 0})

#         target = self.view.text_point(1, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))

#     def testMoveTooFar(self):
#         set_text(self.view, 'foo\nbar\nbaz')
#         add_selection(self.view, a=0, b=4)

#         self.view.run_command('_vi_k', {'mode': MODE_VISUAL_LINE, 'count': 10000, 'xpos': 1})

#         target = self.view.text_point(2, 0)
#         target = self.view.full_line(target).b
#         expected = self.R(0, target)

#         self.assertEqual(expected, first_sel(self.view))
