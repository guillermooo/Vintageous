import unittest

from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL

from Vintageous.tests import ViewTest
from Vintageous.tests import set_text
from Vintageous.tests import add_sel

from Vintageous.vi.text_objects import a_word


class Test_a_word_InInternalNormalMode_Inclusive(ViewTest):
    def testReturnsFullWord_CountOne(self):
        set_text(self.view, 'foo bar baz\n')
        r = self.R(5, 5)
        add_sel(self.view, r)

        reg = a_word(self.view, r.b)
        self.assertEqual('bar ', self.view.substr(reg))

    def testReturnsWordAndPrecedingWhiteSpace_CountOne(self):
        set_text(self.view, '(foo bar) baz\n')
        r = self.R(5, 5)
        add_sel(self.view, r)

        reg = a_word(self.view, r.b)
        self.assertEqual(' bar', self.view.substr(reg))

    def testReturnsWordAndAllPrecedingWhiteSpace_CountOne(self):
        set_text(self.view, '(foo   bar) baz\n')
        r = self.R(8, 8)
        add_sel(self.view, r)

        reg = a_word(self.view, r.b)
        self.assertEqual('   bar', self.view.substr(reg))
