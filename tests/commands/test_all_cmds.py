import os

from Vintageous.tests.cmd_tester import ViCmdTester


_path_to_test_specs = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


class AllCommandsTester(ViCmdTester):
    def setUp(self):
        self.path_to_test_specs = _path_to_test_specs

    def test_all(self):
        self.reset()
        for test in self.iter_tests():
            test.run_with(self)
            self.reset()

        if self.view.is_scratch():
            self.view.close()

    def tearDown(self):
        if self.view.is_scratch():
            self.view.close()
        super().tearDown()
