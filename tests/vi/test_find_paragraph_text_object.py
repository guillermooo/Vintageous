import unittest

from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL

from Vintageous.tests import ViewTest
from Vintageous.tests import set_text
from Vintageous.tests import add_sel

from Vintageous.vi.text_objects import find_paragraph_text_object

# Define a TEXT to experiment with.
# Note that some of the whitespace lines have trailing spaces.

INNER_PARAGRAPHS = [
'''
1  ip0 line1
2  ip0 line2
3  ip0 line3
''',
'''

   
''',
'''
6  ip2 line1
7  ip2 line2
8  ip2 line3
''',
'''

''',
'''
10 ip4 line1
11 ip4 line2
12 ip4 line3
''',
'''

           

''',
'''
16 ip6 line1
17 ip6 line2
18 ip6 line3
''',
]

for i, p in enumerate(INNER_PARAGRAPHS):
    INNER_PARAGRAPHS[i] = p[1:]

TEXT = ''.join(INNER_PARAGRAPHS)

class Test_find_paragraph_text_object_InInternalNormalMode_Inclusive(ViewTest):

    def testReturnsFullParagraph_CountOne(self):
        set_text(self.view, TEXT)
        r = self.R((6, 2), (6, 2))
        add_sel(self.view, r)
        expected = ''.join(INNER_PARAGRAPHS[2:4])
        reg = find_paragraph_text_object(self.view, r)
        self.assertEqual(expected, self.view.substr(reg))

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


class Test_find_paragraph_text_object_InInternalNormalMode_Exclusive(ViewTest):

    def testReturnsFullParagraph_CountOne(self):
        set_text(self.view, TEXT)
        r = self.R((6, 2), (6, 2))
        add_sel(self.view, r)
        expected = ''.join(INNER_PARAGRAPHS[2:3])
        reg = find_paragraph_text_object(self.view, r, inclusive=False)
        self.assertEqual(expected, self.view.substr(reg))

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

