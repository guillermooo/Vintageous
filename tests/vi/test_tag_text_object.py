import unittest
from collections import namedtuple

import sublime

from Vintageous.vi.text_objects import previous_begin_tag
from Vintageous.vi.text_objects import find_containing_tag
from Vintageous.vi.text_objects import next_end_tag
from Vintageous.vi.text_objects import get_region_end
from Vintageous.vi.text_objects import next_unbalanced_tag
from Vintageous.vi.utils import modes
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


test_data = namedtuple('test_data', 'content args expected msg')

R = sublime.Region


TESTS_SEARCH_TAG_FORWARD = (
    test_data(content='<a>foo', args={'start': 0}, expected=(R(0, 3), 'a', False), msg='find tag'),
    test_data(content='<a>foo', args={'start': 1}, expected=(None, None, None), msg="don't find tag"),
    test_data(content='<a>foo</a>', args={'start': 1}, expected=(R(6, 10), 'a', True), msg='find other tag'),


    test_data(content='<a hey="ho">foo', args={'start': 0}, expected=(R(0, 12), 'a', False), msg='find tag with attributes'),
)

TESTS_SEARCH_TAG_BACKWARD = (
    test_data(content='<a>foo', args={'pattern': r'</?(a) *?.*?>', 'start': 0, 'end': 6}, expected=(R(0, 3), 'a', True), msg='find tag'),
    test_data(content='<a>foo', args={'pattern': r'</?(a) *?.*?>', 'start': 0, 'end': 0}, expected=(None, None, None), msg="don't find tag"),
    test_data(content='</a>foo', args={'pattern': r'</?(a) *?.*?>', 'start': 0, 'end': 6}, expected=(R(0, 4), 'a', False), msg='find a closing tag'),
    test_data(content='<a>foo</a>', args={'pattern': r'</?(a) *?.*?>', 'start': 0, 'end': 5}, expected=(R(0, 3), 'a', True), msg='find other tag'),

    test_data(content='<a hey="ho">foo', args={'pattern': r'</?(a) *?.*?>', 'start': 0, 'end': 14}, expected=(R(0, 12), 'a', True), msg='find tag with attributes'),
)


TESTS_NEXT_UNBALANCED_END_TAG = (
    test_data(content='<p>foo <p>bar</p> baz</p>', args={'search': next_end_tag, 'search_args': {'start': 3}, 'restart_at': get_region_end}, expected=(R(21, 25), 'p'), msg='find end tag skipping nested'),
)



class Test_next_unbalanced_end_tag(ViewTest):
    def test_next_unbalanced_end_tag(self):
        self.view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
        for (i, data) in enumerate(TESTS_NEXT_UNBALANCED_END_TAG):
            self.write(data.content)
            actual = next_unbalanced_tag(self.view, **data.args)

            msg = "failed at test index {0}: {1}".format(i, data.msg)
            self.assertEqual(data.expected, actual, msg)



class Test_TagSearch(ViewTest):
    def test_next_end_tag(self):
        self.view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
        for (i, data) in enumerate(TESTS_SEARCH_TAG_FORWARD):
            self.write(data.content)
            actual = next_end_tag(self.view, **data.args)

            msg = "failed at test index {0}: {1}".format(i, data.msg)
            self.assertEqual(data.expected, actual, msg)

    def test_previous_begin_tag(self):
        self.view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
        for (i, data) in enumerate(TESTS_SEARCH_TAG_BACKWARD):
            self.write(data.content)
            actual = previous_begin_tag(self.view, **data.args)

            msg = "failed at test index {0}: {1}".format(i, data.msg)
            self.assertEqual(data.expected, actual, msg)


TESTS_CONTAINING_TAG = (
    test_data(content='<a>foo</a>', args={'start': 4}, expected=(R(0, 3), R(6, 10), 'a'), msg='find tag'),
    test_data(content='<div>foo</div>', args={'start': 5}, expected=(R(0, 5), R(8, 14), 'div'), msg='find long tag'),
    test_data(content='<div class="foo">foo</div>', args={'start': 17}, expected=(R(0, 17), R(20, 26), 'div'), msg='find tag with attributes'),

    test_data(content='<div>foo</div>', args={'start': 2}, expected=(R(0, 5), R(8, 14), 'div'), msg='find tag from within start tag'),
    test_data(content='<div>foo</div>', args={'start': 13}, expected=(R(0, 5), R(8, 14), 'div'), msg='find tag from within end tag'),

    test_data(content='<div>foo <p>bar</p></div>', args={'start': 12}, expected=(R(9, 12), R(15, 19), 'p'), msg='find nested tag from inside'),
)

class Test_FindContainingTag(ViewTest):
    def test_find_containing_tag(self):
        self.view.set_syntax_file('Packages/HTML/HTML.tmLanguage')
        for (i, data) in enumerate(TESTS_CONTAINING_TAG):
            self.write(data.content)
            actual = find_containing_tag(self.view, **data.args)

            msg = "failed at test index {0}: {1}".format(i, data.msg)
            self.assertEqual(data.expected, actual, msg)
