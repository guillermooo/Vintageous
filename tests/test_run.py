import unittest
import builtins

import sublime
import sublime_plugin


from unittest import mock
from unittest.mock import call

from Vintageous.run import ViExecutionState
from Vintageous.run import ViRunCommand
from Vintageous.vi.constants import MODE_NORMAL
from Vintageous.vi.constants import MODE_VISUAL
from Vintageous.vi.constants import _MODE_INTERNAL_NORMAL


class Test_ExecutionState(unittest.TestCase):
    def testCanResetWordState(self):
        ViExecutionState.select_word_begin_from_empty_line = True
        ViExecutionState.reset_word_state()
        self.assertFalse(ViExecutionState.select_word_begin_from_empty_line)

    def testCanReset(self):
        ViExecutionState.select_word_begin_from_empty_line = True
        ViExecutionState.reset()
        self.assertFalse(ViExecutionState.select_word_begin_from_empty_line)

    def testHasExpectedInitialValues(self):
        self.assertFalse(ViExecutionState.select_word_begin_from_empty_line)


class Test_ViRunCommand(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoPostAction(self):
        vi_cmd_data = {'post_action': ['foo', {'bar': 1}]}
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.do_post_action(vi_cmd_data)
            rc.assert_called_once_with('foo', {'bar': 1})

    def testDontDoPostActionIfUndefined(self):
        vi_cmd_data = {'post_action': None}
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.do_post_action(vi_cmd_data)
            self.assertEqual(rc.call_count, 0)

    def testAddJumpToList(self):
        vi_cmd_data = {'is_jump': True}

        with mock.patch.object(self.vi_run.view, 'window') as rc:
            x = mock.Mock()
            rc.return_value = x

            self.vi_run.add_to_jump_list(vi_cmd_data)
            self.assertEqual(rc.call_count, 1)
            x.run_command.assert_called_once_with('vi_add_to_jump_list')

    def testDontAddJumpToListIfNotRequested(self):
        vi_cmd_data = {'is_jump': False}

        with mock.patch.object(self.vi_run.view, 'window') as rc:
            x = mock.Mock()
            rc.return_value = x

            self.vi_run.add_to_jump_list(vi_cmd_data)
            self.assertEqual(rc.call_count, 0)
            self.assertEqual(x.run_command.call_count, 0)

    @mock.patch('Vintageous.state.VintageState')
    def testDebug(self, mocked_state):
        x = mock.Mock()
        x.settings.view = {'vintageous_verbose': True}
        mocked_state.return_value = x

        with mock.patch.object(builtins, 'print') as p:
            self.vi_run.debug(['one', 'two'])
            p.assert_called_once_with('Vintageous:', ['one', 'two'])


class Test_do_action(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNothingIfNoActionAvailable(self):
        vi_cmd_data = {'action': None}
        with mock.patch.object(self.vi_run, 'debug') as deb:
            self.vi_run.do_action(vi_cmd_data)
            deb.assert_called_once_with('Vintageous: Action command: ', None)

    @mock.patch('Vintageous.run.VintageState.registers')
    def testCallsYank(self, mocked_regs):
        mocked_regs.yank = mock.Mock()
        vi_cmd_data = {
            'action': {'command': 'foo', 'args': {}},
            '_repeat_action': False,
            'is_window_command': False,
            }
        self.vi_run.do_action(vi_cmd_data)
        mocked_regs.yank.assert_called_once_with(vi_cmd_data)

    @mock.patch('Vintageous.run.VintageState.registers')
    def testRunsCommandOnceIfMustNotRepeatAction(self, mocked_regs):
        mocked_regs.yank = mock.Mock()
        vi_cmd_data = {
            'action': {'command': 'foo', 'args': {}},
            '_repeat_action': False,
            'is_window_command': False,
            }
        self.vi_run.do_action(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {})

    @mock.patch('Vintageous.run.VintageState.registers')
    def testRunsCommandExpectedTimes(self, mocked_regs):
        mocked_regs.yank = mock.Mock()
        vi_cmd_data = {
            'action': {'command': 'foo', 'args': {}},
            '_repeat_action': True,
            'count': 10,
            'is_window_command': False,
            }
        self.vi_run.do_action(vi_cmd_data)
        self.assertEqual(self.vi_run.view.run_command.call_count, 10)


class Test_do_post_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNotRunIfUnset(self):
        vi_cmd_data = {'post_motion': []}
        self.vi_run.do_post_motion(vi_cmd_data)
        self.assertEqual(self.vi_run.view.run_command.call_count, 0)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'post_motion': [['foo', {'bar': 100}]]}
        self.vi_run.do_post_motion(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100})


class Test_do_pre_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNotRunIfUnset(self):
        vi_cmd_data = {'pre_motion': []}
        self.vi_run.do_pre_motion(vi_cmd_data)
        self.assertEqual(self.vi_run.view.run_command.call_count, 0)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'post_motion': [['foo', {'bar': 100}]]}
        self.vi_run.do_post_motion(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100})


class Test_do_post_every_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNotRunIfUnset(self):
        vi_cmd_data = {'post_every_motion': None}
        self.vi_run.do_post_every_motion(vi_cmd_data, 0, 0)
        self.assertEqual(self.vi_run.view.run_command.call_count, 0)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'post_every_motion': ['foo', {'bar': 100}]}
        self.vi_run.do_post_every_motion(vi_cmd_data, 100, 200)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100, 'current_iteration': 100, 'total_iterations': 200})

    def testRunsAsExpectedIfMissingArgs(self):
        vi_cmd_data = {'post_every_motion': ['foo']}
        self.vi_run.do_post_every_motion(vi_cmd_data, 100, 200)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'current_iteration': 100, 'total_iterations': 200})


class Test_do_pre_every_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testDoesNotRunIfUnset(self):
        vi_cmd_data = {'pre_every_motion': None}
        self.vi_run.do_pre_every_motion(vi_cmd_data, 0, 0)
        self.assertEqual(self.vi_run.view.run_command.call_count, 0)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'pre_every_motion': ['foo', {'bar': 100}]}
        self.vi_run.do_pre_every_motion(vi_cmd_data, 100, 200)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100, 'current_iteration': 100, 'total_iterations': 200})

    def testRunsAsExpectedIfMissingArgs(self):
        vi_cmd_data = {'pre_every_motion': ['foo']}
        self.vi_run.do_pre_every_motion(vi_cmd_data, 100, 200)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'current_iteration': 100, 'total_iterations': 200})


class Test_do_last_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testRunsEvenIfUnset(self):
        # TODO: Does this behavior make sense?
        vi_cmd_data = {'last_motion': []}
        self.vi_run.do_last_motion(vi_cmd_data)
        self.assertEqual(self.vi_run.view.run_command.call_count, 1)

    def testRunsAsExpectedIfSet(self):
        vi_cmd_data = {'last_motion': ['foo', {'bar': 100}]}
        self.vi_run.do_last_motion(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100})


class Test_do_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testCallsDebug(self):
        vi_cmd_data = {'motion': {'command': 'foo', 'args': {'bar': 100}}}
        with mock.patch.object(self.vi_run, 'debug') as db:
            self.vi_run.do_motion(vi_cmd_data)
            db.assert_called_once_with('Vintageous: Motion command: ', vi_cmd_data['motion']['command'], vi_cmd_data['motion']['args'])

    def testCallsRunCommand(self):
        vi_cmd_data = {'motion': {'command': 'foo', 'args': {'bar': 100}}}
        self.vi_run.do_motion(vi_cmd_data)
        self.vi_run.view.run_command.assert_called_once_with('foo', {'bar': 100})


class Test_do_modify_selections(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testCanDetectSelectionModifier(self):
        vi_cmd_data = { 'selection_modifier': ['foo'], 'align_with_xpos': None }
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.do_modify_selections(vi_cmd_data)
            rc.assert_called_with('foo')

    @mock.patch('Vintageous.run.VintageState')
    def testCanDetectAlignXpos(self, mocked_state):
        x = mock.Mock()
        x.xpos = 100
        mocked_state.return_value = x
        vi_cmd_data = { 'selection_modifier': [], 'align_with_xpos': True }
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.do_modify_selections(vi_cmd_data)
            rc.assert_called_with('_align_b_with_xpos', {'xpos': 100})


class Test_restore_original_carets_if_needed(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testCanRestoreOriginalCarets(self):
        vi_cmd_data = { 'restore_original_carets': True }
        self.vi_run.old_sels = [100]
        sel = mock.Mock()
        self.vi_run.view.sel.return_value = sel
        self.vi_run.restore_original_carets_if_needed(vi_cmd_data)
        sel.clear.assert_called_once_with()
        sel.add.assert_called_with(100)


class Test_reposition_caret(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testCanRepositionCaret(self):
        self.vi_run.view.has_non_empty_selection_region.return_value = True
        vi_cmd_data = { 'reposition_caret': ['foo', {'bar': 100}]}
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.reposition_caret(vi_cmd_data)
            rc.assert_called_with('foo', {'bar': 100})

    def testKnowsItShouldNotRun(self):
        self.vi_run.view.has_non_empty_selection_region.return_value = False
        vi_cmd_data = { 'reposition_caret': ['foo', {'bar': 100}]}
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.reposition_caret(vi_cmd_data)
            self.assertEqual(rc.call_count, 0)


class Test_reorient_caret(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testCanRepositionCaret(self):
        self.vi_run.view.has_non_empty_selection_region.return_value = True
        vi_cmd_data = { 'reposition_caret': ['foo', {'bar': 100}]}
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.reposition_caret(vi_cmd_data)
            rc.assert_called_with('foo', {'bar': 100})

    def testKnowsItShouldNotRun(self):
        self.vi_run.view.has_non_empty_selection_region.return_value = False
        vi_cmd_data = { 'reposition_caret': ['foo', {'bar': 100}]}
        with mock.patch.object(self.vi_run.view, 'run_command') as rc:
            self.vi_run.reposition_caret(vi_cmd_data)
            self.assertEqual(rc.call_count, 0)


class Test_save_caret_pos(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testSavesCarets(self):
        self.vi_run.view.sel.return_value = [100]
        self.vi_run.save_caret_pos()
        self.assertEqual(self.vi_run.old_sels, [100])


class Test_do_whole_motion(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    def testAbortsIfMustRepeatAction(self):
        vi_cmd_data = { '_repeat_action': True}
        with mock.patch.object(self.vi_run, 'do_pre_motion') as dprem:
            self.vi_run.do_whole_motion(vi_cmd_data)
            self.assertEqual(dprem.call_count, 0)

    def testCallsAllSteps(self):
        vi_cmd_data = { '_repeat_action': False,
                        'count': 1,
                        'last_motion': False,
                      }

        with mock.patch.object(self.vi_run, 'reorient_caret') as rec, \
             mock.patch.object(self.vi_run, 'do_pre_motion') as dprm, \
             mock.patch.object(self.vi_run, 'do_pre_every_motion') as dprem, \
             mock.patch.object(self.vi_run, 'do_motion') as dm, \
             mock.patch.object(self.vi_run, 'do_post_every_motion') as dpostem, \
             mock.patch.object(self.vi_run, 'do_last_motion') as dlm, \
             mock.patch.object(self.vi_run, 'do_post_motion') as dpostm, \
             mock.patch.object(self.vi_run, 'reposition_caret') as repc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl:

            self.vi_run.do_whole_motion(vi_cmd_data)

            self.assertEqual(rec.call_count, 1)
            self.assertEqual(dprm.call_count, 1)
            self.assertEqual(dprem.call_count, 1)
            self.assertEqual(dm.call_count, 1)
            self.assertEqual(dpostem.call_count, 1)
            self.assertEqual(dlm.call_count, 0)
            self.assertEqual(dpostm.call_count, 1)
            self.assertEqual(repc.call_count, 1)
            self.assertEqual(addtjl.call_count, 1)

    def testCallsAllStepsNeededIfLastMotionPresent(self):
        vi_cmd_data = { '_repeat_action': False,
                        'count': 1,
                        'last_motion': '_whatever',
                      }

        with mock.patch.object(self.vi_run, 'reorient_caret') as rec, \
             mock.patch.object(self.vi_run, 'do_pre_motion') as dprm, \
             mock.patch.object(self.vi_run, 'do_pre_every_motion') as dprem, \
             mock.patch.object(self.vi_run, 'do_motion') as dm, \
             mock.patch.object(self.vi_run, 'do_post_every_motion') as dpostem, \
             mock.patch.object(self.vi_run, 'do_last_motion') as dlm, \
             mock.patch.object(self.vi_run, 'do_post_motion') as dpostm, \
             mock.patch.object(self.vi_run, 'reposition_caret') as repc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl:

            self.vi_run.do_whole_motion(vi_cmd_data)

            self.assertEqual(rec.call_count, 1)
            self.assertEqual(dprm.call_count, 1)
            self.assertEqual(dprem.call_count, 1)
            self.assertEqual(dm.call_count, 0)
            self.assertEqual(dpostem.call_count, 0)
            self.assertEqual(dlm.call_count, 1)
            self.assertEqual(dpostm.call_count, 1)
            self.assertEqual(repc.call_count, 1)
            self.assertEqual(addtjl.call_count, 1)


class Test_run(unittest.TestCase):
    def setUp(self):
        self.vi_run = ViRunCommand(mock.Mock())

    @mock.patch('Vintageous.run.VintageState')
    def testFinallySection(self, mocked_state):
        vi_cmd_data = { '_repeat_action': True,
                        'creates_jump_at_current_position': False,
                        'is_jump': False,
                        'action': None,
                        'mode': None,
                        'must_update_xpos': False,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = []

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 1)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 1)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

    @mock.patch('Vintageous.run.VintageState')
    def testFinallySectionWhenXposMustBeUpdated(self, mocked_state):
        vi_cmd_data = { '_repeat_action': True,
                        'creates_jump_at_current_position': False,
                        'is_jump': False,
                        'action': None,
                        'mode': None,
                        'must_update_xpos': True,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = []

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 1)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 1)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)
                self.assertEqual(thing.update_xpos.call_count, 1)

    @mock.patch('Vintageous.run.VintageState')
    def testFinallySectionWhenMustScrollIntoView(self, mocked_state):
        vi_cmd_data = { '_repeat_action': True,
                        'creates_jump_at_current_position': False,
                        'is_jump': False,
                        'action': None,
                        'mode': None,
                        'must_update_xpos': False,
                        'scroll_into_view': True,
                        'scroll_command': None,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = []

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        self.vi_run.view.sel.return_value = [500]

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 1)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 1)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

                self.vi_run.view.show.assert_called_with(500)

    @mock.patch('Vintageous.run.VintageState')
    def testCanCreateJumpIfRequestedAtCurrentPosition(self, mocked_state):
        vi_cmd_data = { '_repeat_action': True,
                        'creates_jump_at_current_position': True,
                        'is_jump': False,
                        'action': None,
                        'mode': None,
                        'must_update_xpos': False,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = []

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        self.vi_run.view.sel.return_value = [500]

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 1)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 1)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

                addtjl.assert_called_once_with(vi_cmd_data)

    @mock.patch('Vintageous.run.VintageState')
    def testCanCreateJumpIfRequestedAsJump(self, mocked_state):
        vi_cmd_data = { '_repeat_action': True,
                        'creates_jump_at_current_position': False,
                        'is_jump': True,
                        'action': None,
                        'mode': None,
                        'must_update_xpos': False,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = []

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        self.vi_run.view.sel.return_value = [500]

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 1)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 1)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

                addtjl.assert_called_once_with(vi_cmd_data)

    @mock.patch('Vintageous.run.VintageState')
    def testCanDoMotionOnly(self, mocked_state):
        vi_cmd_data = {
                        'creates_jump_at_current_position': False,
                        'is_jump': False,
                        'action': None,
                        'mode': None,
                        'must_update_xpos': False,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = []

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        self.vi_run.view.sel.return_value = [500]

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 1)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 1)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

                self.assertEqual(addtjl.call_count, 0)


    @mock.patch('Vintageous.run.VintageState')
    def testSignalsErrorIfLoneMotionFails(self, mocked_state):
        vi_cmd_data = {
                        'creates_jump_at_current_position': False,
                        'is_jump': False,
                        'action': None,
                        'mode': MODE_NORMAL,
                        'must_update_xpos': False,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = []

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        self.vi_run.view.sel.return_value = [500]

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl, \
             mock.patch('Vintageous.run.utils') as ut:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 1)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 1)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

                self.assertEqual(addtjl.call_count, 0)
                self.assertEqual(ut.blink.call_count, 1)

# test lone action + non-empty sels
# test lone action + empty sels
# test action abortion branch


    @mock.patch('Vintageous.run.VintageState')
    def testCanDoLoneAction(self, mocked_state):
        vi_cmd_data = {
                        'creates_jump_at_current_position': False,
                        'is_jump': False,
                        'action': 'foo',
                        'mode': None,
                        'motion': None,
                        'motion_required': None,
                        'must_update_xpos': False,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = []

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        self.vi_run.view.sel.return_value = [500]

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl, \
             mock.patch.object(self.vi_run, 'do_action') as doac:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 0)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 1)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

                self.assertEqual(addtjl.call_count, 0)
                doac.assert_called_with(vi_cmd_data)

    @mock.patch('Vintageous.run.VintageState')
    def testCanDoLoneAction(self, mocked_state):
        vi_cmd_data = {
                        'creates_jump_at_current_position': False,
                        'is_jump': False,
                        'action': 'foo',
                        'mode': None,
                        'motion': None,
                        'motion_required': None,
                        'must_update_xpos': False,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = []

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        self.vi_run.view.sel.return_value = [500]

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl, \
             mock.patch.object(self.vi_run, 'do_action') as doac:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 0)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 1)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

                self.assertEqual(addtjl.call_count, 0)
                doac.assert_called_with(vi_cmd_data)

    @mock.patch('Vintageous.run.VintageState')
    def testAbortsActionIfMotionFailedInModeInternalNormal(self, mocked_state):
        vi_cmd_data = {
                        'creates_jump_at_current_position': False,
                        'is_jump': False,
                        'action': 'foo',
                        'mode': _MODE_INTERNAL_NORMAL,
                        'cancel_action_if_motion_fails': True,
                        'motion': 'bar',
                        'motion_required': None,
                        'must_update_xpos': False,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = [sublime.Region(0, 2)]

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        self.vi_run.view.sel.return_value = [500]

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl, \
             mock.patch.object(self.vi_run, 'do_action') as doac, \
             mock.patch('Vintageous.run.utils') as ut:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 1)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 2)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

                self.assertEqual(addtjl.call_count, 0)
                doac.assertEqual(doac.call_count, 0)
                self.assertEqual(ut.blink.call_count, 1)

    @mock.patch('Vintageous.run.VintageState')
    def testAbortsActionIfMotionFailedInModeVisual(self, mocked_state):
        vi_cmd_data = {
                        'creates_jump_at_current_position': False,
                        'is_jump': False,
                        'action': 'foo',
                        'mode': MODE_VISUAL,
                        'cancel_action_if_motion_fails': True,
                        'motion': 'bar',
                        'motion_required': None,
                        'must_update_xpos': False,
                        'scroll_into_view': False,
                        'next_mode': 10,
                        'follow_up_mode': 100,
                      }

        self.vi_run.view.sel.return_value = [sublime.Region(0, 2)]

        thing = mock.Mock()
        thing.next_mode = 0
        mocked_state.return_value = thing

        self.vi_run.view.sel.return_value = [500]

        with mock.patch.object(self.vi_run, 'save_caret_pos') as savec, \
             mock.patch.object(self.vi_run, 'do_whole_motion') as dowhm, \
             mock.patch.object(self.vi_run, 'debug') as debug, \
             mock.patch.object(self.vi_run, 'do_post_action') as doposac, \
             mock.patch.object(self.vi_run, 'do_modify_selections') as domodsel, \
             mock.patch.object(self.vi_run, 'restore_original_carets_if_needed') as restorc, \
             mock.patch.object(self.vi_run, 'add_to_jump_list') as addtjl, \
             mock.patch.object(self.vi_run, 'do_action') as doac, \
             mock.patch('Vintageous.run.utils') as ut:

                self.vi_run.run(None, **vi_cmd_data)
                self.assertEqual(savec.call_count, 1)
                self.assertEqual(dowhm.call_count, 1)
                self.assertEqual(debug.call_count, 1)
                self.assertEqual(doposac.call_count, 1)
                self.assertEqual(domodsel.call_count, 1)
                self.assertEqual(restorc.call_count, 2)

                self.assertEqual(thing.next_mode, 10)
                self.assertEqual(thing.next_mode_command, 100)

                self.assertEqual(addtjl.call_count, 0)
                doac.assertEqual(doac.call_count, 0)
                self.assertEqual(ut.blink.call_count, 1)
