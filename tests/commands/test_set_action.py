import unittest

import sublime

from Vintageous.test_runner import TestsState


class TestSetAction(unittest.TestCase):
    def setUp(self):
        TestsState.reset_view_state()

    def testCanSetAction(self):
        TestsState.view.run_command('set_action', {'action': 'vi_d'})
        actual = TestsState.view.settings().get('vintage')['action']
        self.assertEqual('vi_d', actual)

    def tearDown(self):
        TestsState.reset_view_state()
