import unittest

from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL

from Vintageous.tests import BufferTest
from Vintageous.tests import set_text
from Vintageous.tests import add_sel

from Vintageous.vi.text_objects import find_paragraph_text_object


class Test_find_paragraph_text_object_InInternalNormalMode_Inclusive(BufferTest):
    def testReturnsFullParagraph_CountOne(self):
        text = (
            'line 1 in paragraph 1',
            'line 2 in paragraph 1',
            'line 3 in paragraph 1',
            '',
            'line 1 in paragraph 2',
            'line 2 in paragraph 2',
            'line 3 in paragraph 2',
            '',
            'line 1 in paragraph 3',
            'line 2 in paragraph 3',
            'line 3 in paragraph 3',
        )
        set_text(self.view, '\n'.join(text))
        r = self.R((4, 2), (4, 2))
        add_sel(self.view, r)

        expected = (
            '\nline 1 in paragraph 2\n',
            'line 2 in paragraph 2\n',
            'line 3 in paragraph 2\n',
            )

        reg = find_paragraph_text_object(self.view, r)
        self.assertEqual(''.join(expected), self.view.substr(reg))

    # def testReturnsWordAndPrecedingWhiteSpace_CountOne(self):
    #     set_text(self.view, '(foo bar) baz\n')
    #     r = self.R(5, 5)
    #     add_sel(self.view, r)

    #     reg = a_word(self.view, r.b)
    #     self.assertEqual(' bar', self.view.substr(reg))

    # def testReturnsWordAndAllPrecedingWhiteSpace_CountOne(self):
    #     set_text(self.view, '(foo   bar) baz\n')
    #     r = self.R(8, 8)
    #     add_sel(self.view, r)

    #     reg = a_word(self.view, r.b)
    #     self.assertEqual('   bar', self.view.substr(reg))


class Test_find_paragraph_text_object_InInternalNormalMode_Exclusive(BufferTest):
    def testReturnsFullParagraph_CountOne(self):
        text = (
            'line 1 in paragraph 1',
            'line 2 in paragraph 1',
            'line 3 in paragraph 1',
            '',
            'line 1 in paragraph 2',
            'line 2 in paragraph 2',
            'line 3 in paragraph 2',
            '',
            'line 1 in paragraph 3',
            'line 2 in paragraph 3',
            'line 3 in paragraph 3',
        )
        set_text(self.view, '\n'.join(text))
        r = self.R((4, 2), (4, 2))
        add_sel(self.view, r)

        expected = (
            'line 1 in paragraph 2\n',
            'line 2 in paragraph 2\n',
            'line 3 in paragraph 2\n',
            )

        reg = find_paragraph_text_object(self.view, r, inclusive=False)
        self.assertEqual(''.join(expected), self.view.substr(reg))

    # def testReturnsWordAndPrecedingWhiteSpace_CountOne(self):
    #     set_text(self.view, '(foo bar) baz\n')
    #     r = self.R(5, 5)
    #     add_sel(self.view, r)

    #     reg = a_word(self.view, r.b)
    #     self.assertEqual(' bar', self.view.substr(reg))

    # def testReturnsWordAndAllPrecedingWhiteSpace_CountOne(self):
    #     set_text(self.view, '(foo   bar) baz\n')
    #     r = self.R(8, 8)
    #     add_sel(self.view, r)

    #     reg = a_word(self.view, r.b)
    #     self.assertEqual('   bar', self.view.substr(reg))
