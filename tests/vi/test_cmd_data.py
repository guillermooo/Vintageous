import unittest

import sublime

from Vintageous.tests.borrowed import mock
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_INSERT
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_REPLACE
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.vi.constants import MODE_NORMAL_INSERT
from Vintageous.vi.cmd_data import CmdData


known_keys = [
    'pre_motion',
    'motion',
    'motion_required',
    'action',
    'post_action',
    'count',
    '_user_provided_count',
    'pre_every_motion',
    'post_every_motion',
    'post_motion',
    'can_yank',
    'yanks_linewise',
    'register',
    'mode',
    'reposition_caret',
    'follow_up_mode',
    'is_digraph_start',
    'user_input',
    '__reorient_caret',
    'is_jump',
    'creates_jump_at_current_position',
    'cancel_action_if_motion_fails',
    '_repeat_action',
    'last_buffer_search',
    'last_character_search',
    'restore_original_carets',
    'xpos',
    'must_update_xpos',
    'scroll_into_view',
    'scroll_command',
    '_change_mode_to',
    '_exit_mode',
    '_exit_mode_command',
    'must_blink_on_error',
    'next_mode',
    'selection_modifier',
    'align_with_xpos',
    'last_motion',
    'synthetize_new_line_at_eof',
    '_mark_groups_for_gluing',
    'populates_small_delete_register',
]


class Test_CmdData(unittest.TestCase):
    def setUp(self):
        state = mock.Mock()
        state.count = 100
        state.user_provided_count = 200
        state.register = 300
        state.mode = 400
        state.user_input = 500
        state.last_buffer_search = 600
        state.last_character_search = 700
        state.xpos = 800
        self.state = state
        self.cmd_data = CmdData(self.state)

    def testHasExpectedAmountOfKeys(self):
        self.assertEqual(len(known_keys), len(self.cmd_data))

    def testHasExpectedKeys(self):
        for k in known_keys:
            self.assertTrue(k in self.cmd_data)

    def testCanBeInitialized(self):
        cmd_data = CmdData(self.state)
        self.assertEqual(self.cmd_data['count'], 100)
        self.assertEqual(self.cmd_data['_user_provided_count'], 200)
        self.assertEqual(self.cmd_data['register'], 300)
        self.assertEqual(self.cmd_data['mode'], 400)
        self.assertEqual(self.cmd_data['user_input'], 500)
        self.assertEqual(self.cmd_data['last_buffer_search'], 600)
        self.assertEqual(self.cmd_data['last_character_search'], 700)
        self.assertEqual(self.cmd_data['xpos'], 800)

        self.assertEqual(self.cmd_data['pre_motion'], None)
        self.assertEqual(self.cmd_data['motion'], {})
        self.assertEqual(self.cmd_data['motion_required'], True)
        self.assertEqual(self.cmd_data['action'], {})
        self.assertEqual(self.cmd_data['post_action'], None)
        self.assertEqual(self.cmd_data['pre_every_motion'], None)
        self.assertEqual(self.cmd_data['post_every_motion'], None)
        self.assertEqual(self.cmd_data['post_motion'], [])
        self.assertEqual(self.cmd_data['can_yank'], False)
        self.assertEqual(self.cmd_data['yanks_linewise'], False)
        self.assertEqual(self.cmd_data['reposition_caret'], None)
        self.assertEqual(self.cmd_data['follow_up_mode'], None)
        self.assertEqual(self.cmd_data['is_digraph_start'], False)
        self.assertEqual(self.cmd_data['__reorient_caret'], False)
        self.assertEqual(self.cmd_data['is_jump'], False)
        self.assertEqual(self.cmd_data['creates_jump_at_current_position'], False)
        self.assertEqual(self.cmd_data['cancel_action_if_motion_fails'], False)
        self.assertEqual(self.cmd_data['_repeat_action'], False)
        self.assertEqual(self.cmd_data['restore_original_carets'], False)
        self.assertEqual(self.cmd_data['must_update_xpos'], True)
        self.assertEqual(self.cmd_data['scroll_into_view'], True)
        self.assertEqual(self.cmd_data['scroll_command'], None)
        self.assertEqual(self.cmd_data['_change_mode_to'], None)
        self.assertEqual(self.cmd_data['_exit_mode'], None)
        self.assertEqual(self.cmd_data['_exit_mode_command'], None)
        self.assertEqual(self.cmd_data['must_blink_on_error'], False)
        self.assertEqual(self.cmd_data['next_mode'], MODE_NORMAL)
        self.assertEqual(self.cmd_data['selection_modifier'], None)
        self.assertEqual(self.cmd_data['align_with_xpos'], False)
        self.assertEqual(self.cmd_data['last_motion'], None)
        self.assertEqual(self.cmd_data['synthetize_new_line_at_eof'], False)
        self.assertEqual(self.cmd_data['_mark_groups_for_gluing'], True)
        self.assertEqual(self.cmd_data['populates_small_delete_register'], False)

    def testCurrentModeIsCarriedOver(self):
        self.state.mode = MODE_VISUAL
        cmd_data = CmdData(self.state)
        self.assertEqual(cmd_data['mode'], MODE_VISUAL)

        self.state.mode = MODE_VISUAL_LINE
        cmd_data = CmdData(self.state)
        self.assertEqual(cmd_data['mode'], MODE_VISUAL_LINE)
