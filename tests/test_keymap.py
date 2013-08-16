import unittest
import json
import os

import sublime

HERE = os.path.dirname(__file__)

PATH_TO_KEYMAP = os.path.abspath(os.path.join(HERE, '..', 'Default.sublime-keymap'))


class TestKeyBindings(unittest.TestCase):
    def setUp(self):
        self.kbs = sublime.decode_value(sublime.load_resource('Packages/Vintageous/Default.sublime-keymap'))
        self.known_kbs = sublime.decode_value(sublime.load_resource('Packages/Vintageous/tests/data/Default.sublime-keymap_'))

    def testHasExpectedNumberOfKeyBindings(self):
        self.assertEqual(len(self.kbs), len(self.known_kbs))

    def testAllKeyBindingsMatch(self):
        for kb in self.kbs:
            self.assertTrue(kb in self.known_kbs)
