import unittest

from Vintageous.test_runner import TestsState


class TestSetMotion(unittest.TestCase):
    def setUp(self):
        TestsState.reset_view_state()

    @unittest.skip("Can't set motion because will be run straight away.")
    # TODO: Mock .eval() so it does not reset the state.
    def testCanSetMotion(self):
        TestsState.view.run_command('set_motion', {'motion': 'vi_l'})
        actual = TestsState.view.settings().get('vintage')['motion']
        self.assertEqual('vi_l', actual)
