import unittest

import sublime

from Vintageous.test_runner import TestsState
from Vintageous.tests.borrowed import mock
from Vintageous.vi.constants import MODE_INSERT
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.constants import MODE_NORMAL_INSERT
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_REPLACE
from Vintageous.vi.constants import DIGRAPH_ACTION
from Vintageous.vi.constants import DIGRAPH_MOTION
from Vintageous.vi.constants import INCOMPLETE_ACTIONS
from Vintageous.vi.constants import ACTIONS_EXITING_TO_INSERT_MODE
from Vintageous.vi.constants import digraphs
from Vintageous.vi.constants import mode_to_str
from Vintageous.vi.constants import regions_transformer


class Test_constants(unittest.TestCase):
    def testModeConstantsHaveTheRightValue(self):
        self.assertEqual(MODE_INSERT, 1)
        self.assertEqual(MODE_NORMAL, 1 << 1)
        self.assertEqual(MODE_VISUAL, 1 << 2)
        self.assertEqual(MODE_VISUAL_LINE, 1 << 3)
        self.assertEqual(MODE_NORMAL_INSERT, 1 << 4)
        self.assertEqual(_MODE_INTERNAL_NORMAL, 1 << 5)
        self.assertEqual(MODE_REPLACE, 1 << 6)

    def testDigraphConstantValues(self):
        self.assertEqual(DIGRAPH_ACTION, 1)
        self.assertEqual(DIGRAPH_MOTION, 2)

    def testDigraphData(self):

        keys = [('vi_d', 'vi_d'),
                ('vi_c', 'vi_c'),
                ('vi_y', 'vi_y'),
                ('vi_equals', 'vi_equals'),
                ('vi_lambda', 'vi_lambda'),
                ('vi_antilambda', 'vi_antilambda'),
                ('vi_g_action', 'vi_g_big_u'),
                ('vi_g_action', 'vi_g_u'),
                ('vi_g_action', 'vi_g_q'),
                ('vi_g_action', 'vi_g_v'),
                ('vi_z_action', 'vi_z_enter'),
                ('vi_z_action', 'vi_z_t'),
                ('vi_z_action', 'vi_z_minus'),
                ('vi_z_action', 'vi_z_b'),
                ('vi_z_action', 'vi_zz'),
                ('vi_ctrl_w_action', 'vi_ctrl_w_v'),
                ('vi_ctrl_r_action', 'vi_ctrl_r_equals'),
                ('vi_g_action', 'vi_gg'),
                ('vi_g_action', 'vi_g_d'),
                ('vi_g_action', 'vi_g_big_d'),
                ('vi_g_action', 'vi_g_star'),
                ('vi_g_action', 'vi_g_octothorp'),
                ('vi_f_first_step', 'vi_set_user_input'),]

        for k in keys:
            self.assertTrue(k in digraphs)

        self.assertEqual(len(keys), len(digraphs))

        data = (
            (('vi_d', 'vi_d'), ('vi_dd', DIGRAPH_ACTION)),
            (('vi_c', 'vi_c'), ('vi_cc', DIGRAPH_ACTION)),
            (('vi_y', 'vi_y'), ('vi_yy', DIGRAPH_ACTION)),
            (('vi_equals', 'vi_equals'), ('vi_equals_equals', DIGRAPH_ACTION)),
            (('vi_lambda', 'vi_lambda'), ('vi_double_lambda', DIGRAPH_ACTION)),
            (('vi_antilambda', 'vi_antilambda'), ('vi_double_antilambda', DIGRAPH_ACTION)),
            (('vi_g_action', 'vi_g_big_u'), ('vi_g_big_u', DIGRAPH_ACTION)),
            (('vi_g_action', 'vi_g_u'), ('vi_g_u', DIGRAPH_ACTION)),
            (('vi_g_action', 'vi_g_q'), ('vi_g_q', DIGRAPH_ACTION)),
            (('vi_g_action', 'vi_g_v'), ('vi_g_v', DIGRAPH_ACTION)),
            (('vi_z_action', 'vi_z_enter'), ('vi_z_enter', DIGRAPH_ACTION)),
            (('vi_z_action', 'vi_z_t'), ('vi_z_t', DIGRAPH_ACTION)),
            (('vi_z_action', 'vi_z_minus'), ('vi_z_minus', DIGRAPH_ACTION)),
            (('vi_z_action', 'vi_z_b'), ('vi_z_b', DIGRAPH_ACTION)),
            (('vi_z_action', 'vi_zz'), ('vi_zz', DIGRAPH_ACTION)),
            (('vi_ctrl_w_action', 'vi_ctrl_w_v'), ('vi_ctrl_w_v', DIGRAPH_ACTION)),
            (('vi_ctrl_r_action', 'vi_ctrl_r_equals'), ('vi_ctrl_r_equals', DIGRAPH_ACTION)),
            (('vi_g_action', 'vi_gg'), ('vi_gg', DIGRAPH_MOTION)),
            (('vi_g_action', 'vi_g_d'), ('vi_g_d', DIGRAPH_MOTION)),
            (('vi_g_action', 'vi_g_big_d'), ('vi_g_big_d', DIGRAPH_MOTION)),
            (('vi_g_action', 'vi_g_star'), ('vi_g_star', DIGRAPH_MOTION)),
            (('vi_g_action', 'vi_g_octothorp'), ('vi_g_octothorp', DIGRAPH_MOTION)),
            (('vi_f_first_step', 'vi_set_user_input'), ('vi_f', DIGRAPH_MOTION)),
        )

        for k, v in data:
            self.assertEqual(digraphs[k], v)


    def testIncompleteActions(self):
        expected = (
            'vi_g_action',
            'vi_z_action',
            'vi_ctrl_w_action',
            'vi_ctrl_r_action',
        )

        self.assertEqual(expected, INCOMPLETE_ACTIONS)

    def testActionsExitingToInsertMode(self):
        expected = ('vi_ctrl_r_action',)

        self.assertEqual(expected, ACTIONS_EXITING_TO_INSERT_MODE)


class Test_mode_to_str(unittest.TestCase):
    def testReturnsUnknownForUnknownModes(self):
        self.assertEqual(mode_to_str(5000), '<unknown>')

    def testCanTranslateKnownModes(self):
        self.assertEqual(mode_to_str(MODE_INSERT), "INSERT")
        self.assertEqual(mode_to_str(MODE_NORMAL), "")
        self.assertEqual(mode_to_str(MODE_VISUAL_LINE), "VISUAL LINE")
        self.assertEqual(mode_to_str(MODE_REPLACE), "REPLACE")
        self.assertEqual(mode_to_str(MODE_NORMAL_INSERT), "INSERT")
        self.assertEqual(mode_to_str(_MODE_INTERNAL_NORMAL), "<unknown>")


class Test_regions_transformer(unittest.TestCase):
    def tearDown(self):
        TestsState.view.sel().clear()
        TestsState.view.sel().add(sublime.Region(0, 0))

    def testCanTransformRegions(self):
        TestsState.view.sel().clear()
        TestsState.view.sel().add(sublime.Region(0, 100))
        TestsState.view.sel().add(sublime.Region(200, 300))
        TestsState.view.sel().add(sublime.Region(400, 500))

        transf = lambda view, x: sublime.Region(x.a, x.b - (x.size() - 1))
        regions_transformer(TestsState.view, transf)

        regions = list(TestsState.view.sel())

        for r in regions:
            self.assertEqual(r.size(), 1)
