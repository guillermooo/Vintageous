import unittest

from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE

from Vintageous.tests.commands import set_text
from Vintageous.tests.commands import add_selection
from Vintageous.tests.commands import get_sel
from Vintageous.tests.commands import first_sel
from Vintageous.tests.commands import BufferTest


class Test_vi_e_InNormalMode(BufferTest):
    def testMoveToEndOfWord(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_selection(self.view, a=1, b=1)
        
        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        target = self.view.text_point(0, 2)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveToEndOfWord_FromPreviousWord(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_selection(self.view, a=2, b=2)
        
        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        target = self.view.text_point(1, 2)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveToEndOfWord_OnLastLine(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_selection(self.view, a=8, b=8)
        
        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveToEndOfWord_OnMiddleLine_WithTrailingWhitespace(self):
        set_text(self.view, 'abc\nabc   \nabc')
        add_selection(self.view, a=6, b=6)
        
        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        target = self.view.text_point(2, 2)

        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveToEndOfWord_OnLastLine_WithTrailingWhitespace(self):
        set_text(self.view, 'abc\nabc\nabc   ')
        add_selection(self.view, a=8, b=8)
        
        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

        self.view.run_command('_vi_e', {'mode': MODE_NORMAL, 'count': 1})

        target = self.view.text_point(2,5)
        expected = self.R(target, target)
        
        self.assertEqual(expected, first_sel(self.view))

class Test_vi_e_InVisualMode(BufferTest):
    def testMoveToEndOfWord(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_selection(self.view, a=1, b=2)
        
        self.view.run_command('_vi_e', {'mode': MODE_VISUAL, 'count': 1})

        target = self.view.text_point(0, 3)
        expected = self.R(1, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveToEndOfWord_FromPreviousWord(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_selection(self.view, a=2, b=3)
        
        self.view.run_command('_vi_e', {'mode': MODE_VISUAL, 'count': 1})

        target = self.view.text_point(1, 3)
        expected = self.R(2, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveToEndOfWord_OnLastLine(self):
        set_text(self.view, 'abc\nabc\nabc')
        add_selection(self.view, a=8, b=9)
        
        self.view.run_command('_vi_e', {'mode': MODE_VISUAL, 'count': 1})

        target = self.view.text_point(2, 3)
        expected = self.R(8, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveToEndOfWord_OnMiddleLine_WithTrailingWhitespace(self):
        set_text(self.view, 'abc\nabc   \nabc')
        add_selection(self.view, a=6, b=7)
        
        self.view.run_command('_vi_e', {'mode': MODE_VISUAL, 'count': 1})

        target = self.view.text_point(2, 3)
        expected = self.R(6, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveToEndOfWord_OnLastLine_WithTrailingWhitespace(self):
        set_text(self.view, 'abc\nabc\nabc   ')
        add_selection(self.view, a=8, b=9)
        
        self.view.run_command('_vi_e', {'mode': MODE_VISUAL, 'count': 1})

        target = self.view.text_point(2, 3)
        expected = self.R(8, target)

        self.assertEqual(expected, first_sel(self.view))

        self.view.run_command('_vi_e', {'mode': MODE_VISUAL, 'count': 1})

        target = self.view.text_point(2,6)
        expected = self.R(8, target)
        
        self.assertEqual(expected, first_sel(self.view))


