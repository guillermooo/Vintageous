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
        for test in self.iter_tests():
            self.append(test.before_text)
            self.set_sels(test)
            text_data, sel_data = test.run_with(self.view)
            self.assertEqual(*text_data)
            after_sels, before_sels, message = sel_data
            self.assertEqual([(s.a, s.b) for s in before_sels], after_sels, message)
            self.reset()
        if self.view.is_scratch():
            self.view.close()

    def tearDown(self):
        self.view.close()
        super().tearDown()