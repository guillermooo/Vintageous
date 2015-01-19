from collections import namedtuple
import os

import sublime

from Vintageous.vi.utils import modes
from Vintageous.tests.cmd_tester import ViCmdTester


_path_to_test_specs = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class AllCommandsTester(ViCmdTester):
    def setUp(self):
        self.path_to_test_specs = _path_to_test_specs

    def test_all(self):
        self.reset()
        for t in self.get_tests():
            self.append(t.before_text)
            self.set_sels()
            self.view.run_command(t.cmd_name, t.args)
            self.assertEqual(
                self.view.substr(sublime.Region(0, self.view.size())),
                t.after_text,
                t.message
                )
            self.reset()
        if self.view.is_scratch():
            self.view.close()