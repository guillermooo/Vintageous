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


# TODO: Test against folded regions.
# TODO: Ensure that we only create empty selections while testing. Add assert_all_sels_empty()?
class Test_vi_j_InNormalMode(BufferTest):
    def testMoveOne(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, a=1, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 1)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany(self):
        set_text(self.view, ''.join(('abc\n',) * 60))
        add_sel(self.view, a=1, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_NORMAL, 'count': 50, 'xpos': 1})

        target = self.view.text_point(50, 1)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoLongerLine(self):
        set_text(self.view, 'foo\nfoo bar\nfoo bar')
        add_sel(self.view, a=1, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 1)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoShorterLine(self):
        set_text(self.view, 'foo bar\nfoo\nbar')
        add_sel(self.view, a=5, b=5)

        self.view.run_command('_vi_j', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 5})

        target = self.view.text_point(1, 0)
        target = self.view.line(target).b - 1
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLine(self):
        set_text(self.view, '\nfoo\nbar')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_j', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLineToEmptyLine(self):
        set_text(self.view, '\n\nbar')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_j', {'mode': MODE_NORMAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveTooFar(self):
        set_text(self.view, 'foo\nbar\nbaz')
        add_sel(self.view, a=1, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_NORMAL, 'count': 10000, 'xpos': 1})

        target = self.view.text_point(2, 1)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))


class Test_vi_j_InVisualMode(BufferTest):
    def testMoveOne(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, a=1, b=2)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 2)
        expected = self.R(1, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveReversedNoCrossOver(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, a=10, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 1)
        expected = self.R(10, target)

        self.assertEqual(expected, first_sel(self.view))

    # FIXME: This is wrong in the implementation.
    def testMoveReversedCrossOver(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, a=6, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 2, 'xpos': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(5, target)

        self.assertEqual(expected, first_sel(self.view))

    # FIXME: This is wrong in the implementation.
    def testMoveReversedCrossOverTooFar(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, a=6, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 100, 'xpos': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(5, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveReversedBackToSameLine(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, a=6, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 1)
        expected = self.R(target, 6)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveReversedDownFromSameLine(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, a=6, b=5)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(5, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany(self):
        set_text(self.view, ''.join(('abc\n',) * 60))
        add_sel(self.view, a=1, b=2)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 50, 'xpos': 1})

        target = self.view.text_point(50, 2)
        expected = self.R(1, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoLongerLine(self):
        set_text(self.view, 'foo\nfoo bar\nfoo bar')
        add_sel(self.view, a=1, b=2)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 2)
        expected = self.R(1, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoShorterLine(self):
        set_text(self.view, 'foo bar\nfoo\nbar')
        add_sel(self.view, a=5, b=6)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 5})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(5, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLine(self):
        set_text(self.view, '\nfoo\nbar')
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 1)
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLineToEmptyLine(self):
        set_text(self.view, '\n\nbar')
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 1)
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveTooFar(self):
        set_text(self.view, 'foo\nbar\nbaz')
        add_sel(self.view, a=1, b=2)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL, 'count': 10000, 'xpos': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(1, target)

        self.assertEqual(expected, first_sel(self.view))


# TODO: Ensure that we only create empty selections while testing. Add assert_all_sels_empty()?
class Test_vi_j_InInternalNormalMode(BufferTest):
    def testMoveOne(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, a=1, b=1)

        self.view.run_command('_vi_j', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany(self):
        set_text(self.view, ''.join(('abc\n',) * 60))
        add_sel(self.view, a=1, b=1)

        self.view.run_command('_vi_j', {'mode': _MODE_INTERNAL_NORMAL, 'count': 50, 'xpos': 1})

        target = self.view.text_point(50, 2)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoLongerLine(self):
        set_text(self.view, 'foo\nfoo bar\nfoo bar')
        add_sel(self.view, a=1, b=1)

        self.view.run_command('_vi_j', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoShorterLine(self):
        set_text(self.view, 'foo bar\nfoo\nbar')
        add_sel(self.view, a=5, b=5)

        self.view.run_command('_vi_j', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 5})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLine(self):
        set_text(self.view, '\nfoo\nbar')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_j', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLineToEmptyLine(self):
        set_text(self.view, '\n\nbar')
        add_sel(self.view, a=0, b=0)

        self.view.run_command('_vi_j', {'mode': _MODE_INTERNAL_NORMAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveTooFar(self):
        set_text(self.view, 'foo\nbar\nbaz')
        add_sel(self.view, a=1, b=1)

        self.view.run_command('_vi_j', {'mode': _MODE_INTERNAL_NORMAL, 'count': 10000, 'xpos': 1})

        target = self.view.text_point(2, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))


class Test_vi_j_InVisualLineMode(BufferTest):
    def testMoveOne(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_sel(self.view, a=0, b=4)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL_LINE, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany(self):
        set_text(self.view, ''.join(('abc\n',) * 60))
        add_sel(self.view, a=0, b=4)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL_LINE, 'count': 50, 'xpos': 1})

        target = self.view.text_point(50, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLine(self):
        set_text(self.view, '\nfoo\nbar')
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL_LINE, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLineToEmptyLine(self):
        set_text(self.view, '\n\nbar')
        add_sel(self.view, a=0, b=1)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL_LINE, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveTooFar(self):
        set_text(self.view, 'foo\nbar\nbaz')
        add_sel(self.view, a=0, b=4)

        self.view.run_command('_vi_j', {'mode': MODE_VISUAL_LINE, 'count': 10000, 'xpos': 1})

        target = self.view.text_point(2, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))
