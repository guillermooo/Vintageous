import unittest
import builtins

import sublime

from unittest import mock
from Vintageous.test_runner import TestsState
from Vintageous.vi import registers
from Vintageous.vi.registers import Registers
from Vintageous.vi.settings import SettingsManager
from Vintageous.state import VintageState


class TestCaseRegistersConstants(unittest.TestCase):
    def testUnnamedConstantValue(self):
        self.assertEqual(registers.REG_UNNAMED, '"')

    def testSmallDeleteConstantValue(self):
        self.assertEqual(registers.REG_SMALL_DELETE, '-')

    def testBlackHoleConstantValue(self):
        self.assertEqual(registers.REG_BLACK_HOLE, '_')

    def testLastInsertedTextConstantValue(self):
        self.assertEqual(registers.REG_LAST_INSERTED_TEXT, '.')

    def testFileNameConstantValue(self):
        self.assertEqual(registers.REG_FILE_NAME, '%')

    def testAltFileNameConstantValue(self):
        self.assertEqual(registers.REG_ALT_FILE_NAME, '#')

    def testExpressionConstantValue(self):
        self.assertEqual(registers.REG_EXPRESSION, '=')

    def testSysClipboard1ConstantValue(self):
        self.assertEqual(registers.REG_SYS_CLIPBOARD_1, '*')

    def testSysClipboard2ConstantValue(self):
        self.assertEqual(registers.REG_SYS_CLIPBOARD_2, '+')

    def testSysClipboardAllConstantValue(self):
        self.assertEqual(registers.REG_SYS_CLIPBOARD_ALL,
                             (registers.REG_SYS_CLIPBOARD_1,
                              registers.REG_SYS_CLIPBOARD_2,))

    def testValidRegisterNamesConstantValue(self):
        names = tuple("{0}".format(c) for c in "abcdefghijklmnopqrstuvwxyz")
        self.assertEqual(registers.REG_VALID_NAMES, names)

    def testValidNumberNamesConstantValue(self):
        names = tuple("{0}".format(c) for c in "0123456789")
        self.assertEqual(registers.REG_VALID_NUMBERS, names)

    def testSysClipboardAllConstantValue(self):
        self.assertEqual(registers.REG_SPECIAL,
                             (registers.REG_UNNAMED,
                              registers.REG_SMALL_DELETE,
                              registers.REG_BLACK_HOLE,
                              registers.REG_LAST_INSERTED_TEXT,
                              registers.REG_FILE_NAME,
                              registers.REG_ALT_FILE_NAME,
                              registers.REG_SYS_CLIPBOARD_1,
                              registers.REG_SYS_CLIPBOARD_2,))

    def testAllConstantValue(self):
        self.assertEqual(registers.REG_ALL,
                            (registers.REG_SPECIAL +
                             registers.REG_VALID_NUMBERS +
                             registers.REG_VALID_NAMES))


class TestCaseRegisters(unittest.TestCase):
    def setUp(self):
        sublime.set_clipboard('')
        registers._REGISTER_DATA = {}
        TestsState.view.settings().erase('vintage')
        TestsState.view.settings().erase('vintageous_use_sys_clipboard')
        # self.regs = Registers(view=TestsState.view,
                              # settings=SettingsManager(view=TestsState.view))
        self.regs = VintageState(TestsState.view).registers

    def testCanInitializeClass(self):
        self.assertEqual(self.regs.view, TestsState.view)
        self.assertTrue(getattr(self.regs, 'settings'))

    def testCanSetUnanmedRegister(self):
        self.regs._set_default_register(["foo"])
        self.assertEqual(registers._REGISTER_DATA[registers.REG_UNNAMED],
                         ["foo"])

    def testSettingLongRegisterNameThrowsAssertionError(self):
        self.assertRaises(AssertionError, self.regs.set, "aa", "foo")

    def testSettingNonListValueThrowsAssertionError(self):
        self.assertRaises(AssertionError, self.regs.set, "a", "foo")

    @unittest.skip("Not implemented.")
    def testUnknownRegisterNameThrowsException(self):
        # XXX Doesn't pass at the moment.
        self.assertRaises(Exception, self.regs.set, "~", "foo")

    def testRegisterDataIsAlwaysStoredAsString(self):
        self.regs.set('"', [100])
        self.assertEqual(registers._REGISTER_DATA[registers.REG_UNNAMED],
                         ["100"])

    def testSettingBlackHoleRegisterDoesNothing(self):
        registers._REGISTER_DATA[registers.REG_UNNAMED] = ["bar"]
        # In this case it doesn't matter whether we're setting a list or not,
        # because we are discarding the value anyway.
        self.regs.set(registers.REG_BLACK_HOLE, "foo")
        self.assertTrue(registers.REG_BLACK_HOLE not in registers._REGISTER_DATA)
        self.assertTrue(registers._REGISTER_DATA[registers.REG_UNNAMED], ["bar"])

    def testSettingExpressionRegisterDoesntPopulateUnnamedRegister(self):
        self.regs.set("=", [100])
        self.assertTrue(registers.REG_UNNAMED not in registers._REGISTER_DATA)
        self.assertEqual(registers._REGISTER_DATA[registers.REG_EXPRESSION],
                        ["100"])

    def testCanSetNormalRegisters(self):
        for name in registers.REG_VALID_NAMES:
            self.regs.set(name, [name])

        for number in registers.REG_VALID_NUMBERS:
            self.regs.set(number, [number])

        for name in registers.REG_VALID_NAMES:
            self.assertEqual(registers._REGISTER_DATA[name], [name])

        for number in registers.REG_VALID_NUMBERS:
            self.assertEqual(registers._REGISTER_DATA[number], [number])

    def testSettingNormalRegisterSetsUnnamedRegisterToo(self):
        self.regs.set('a', [100])
        self.assertEqual(registers._REGISTER_DATA[registers.REG_UNNAMED], ['100'])

        self.regs.set('0', [200])
        self.assertEqual(registers._REGISTER_DATA[registers.REG_UNNAMED], ['200'])

    def testSettingRegisterSetsClipboardIfNeeded(self):
        self.regs.settings.view['vintageous_use_sys_clipboard'] = True
        self.regs.set('a', [100])
        self.assertEqual(sublime.get_clipboard(), '100')

    def testCanAppendToSingleValue(self):
        self.regs.set('a', ['foo'])
        self.regs.append_to('A', ['bar'])
        self.assertEqual(registers._REGISTER_DATA['a'], ['foobar'])

    def testCanAppendToMultipleBalancedValues(self):
        self.regs.set('a', ['foo', 'bar'])
        self.regs.append_to('A', ['fizz', 'buzz'])
        self.assertEqual(registers._REGISTER_DATA['a'], ['foofizz', 'barbuzz'])

    def testCanAppendToMultipleValuesMoreExistingValues(self):
        self.regs.set('a', ['foo', 'bar'])
        self.regs.append_to('A', ['fizz'])
        self.assertEqual(registers._REGISTER_DATA['a'], ['foofizz', 'bar'])

    def testCanAppendToMultipleValuesMoreNewValues(self):
        self.regs.set('a', ['foo'])
        self.regs.append_to('A', ['fizz', 'buzz'])
        self.assertEqual(registers._REGISTER_DATA['a'], ['foofizz', 'buzz'])

    def testAppendingSetsDefaultRegister(self):
        self.regs.set('a', ['foo'])
        self.regs.append_to('A', ['bar'])
        self.assertEqual(registers._REGISTER_DATA[registers.REG_UNNAMED],
                         ['foobar'])

    def testAppendSetsClipboardIfNeeded(self):
        self.regs.settings.view['vintageous_use_sys_clipboard'] = True
        self.regs.set('a', ['foo'])
        self.regs.append_to('A', ['bar'])
        self.assertEqual(sublime.get_clipboard(), 'foobar')

    def testGetDefaultToUnnamedRegister(self):
        registers._REGISTER_DATA['"'] = ['foo']
        self.assertEqual(self.regs.get(), ['foo'])

    def testGettingBlackHoleRegisterReturnsNone(self):
        self.assertEqual(self.regs.get(registers.REG_BLACK_HOLE), None)

    def testCanGetFileNameRegister(self):
        fname = self.regs.get(registers.REG_FILE_NAME)
        self.assertEqual(fname, [TestsState.view.file_name()])

    def testCanGetClipboardRegisters(self):
        self.regs.set(registers.REG_SYS_CLIPBOARD_1, ['foo'])
        self.assertEqual(self.regs.get(registers.REG_SYS_CLIPBOARD_1), ['foo'])
        self.assertEqual(self.regs.get(registers.REG_SYS_CLIPBOARD_2), ['foo'])

    def testGetSysClipboardAlwaysIfRequested(self):
        self.regs.settings.view['vintageous_use_sys_clipboard'] = True
        sublime.set_clipboard('foo')
        self.assertEqual(self.regs.get(), ['foo'])

    def testGettingExpressionRegisterClearsExpressionRegister(self):
        registers._REGISTER_DATA[registers.REG_EXPRESSION] = ['100']
        self.assertEqual(self.regs.get(), ['100'])
        self.assertEqual(registers._REGISTER_DATA[registers.REG_EXPRESSION], '')

    def testCanGetNumberRegister(self):
        registers._REGISTER_DATA['5'] = ['foo']
        self.assertEqual(self.regs.get('5'), ['foo'])

    def testCanGetRegisterEvenIfRequestingItThroughACapitalLetter(self):
        registers._REGISTER_DATA['a'] = ['foo']
        self.assertEqual(self.regs.get('A'), ['foo'])

    def testCanGetRegistersWithDictSyntax(self):
        registers._REGISTER_DATA['a'] = ['foo']
        self.assertEqual(self.regs.get('a'), self.regs['a'])

    def testCanSetRegistersWithDictSyntax(self):
        self.regs['a'] = ['100']
        self.assertEqual(self.regs['a'], ['100'])

    def testCanAppendToRegisteWithDictSyntax(self):
        self.regs['a'] = ['100']
        self.regs['A'] = ['100']
        self.assertEqual(self.regs['a'], ['100100'])

    def testCanConvertToDict(self):
        self.regs['a'] = ['100']
        self.regs['b'] = ['200']
        values = {name: self.regs.get(name) for name in registers.REG_ALL}
        values.update({'a': ['100'], 'b': ['200']})
        self.assertEqual(self.regs.to_dict(), values)

    def testGettingEmptyRegisterReturnsNone(self):
        self.assertEqual(self.regs.get('a'), None)

    def testCanSetSmallDeleteRegister(self):
        self.regs[registers.REG_SMALL_DELETE] = ['foo']
        self.assertEqual(registers._REGISTER_DATA[registers.REG_SMALL_DELETE], ['foo'])

    def testCanGetSmallDeleteRegister(self):
        registers._REGISTER_DATA[registers.REG_SMALL_DELETE] = ['foo']
        self.assertEqual(self.regs.get(registers.REG_SMALL_DELETE), ['foo'])


class Test_get_selected_text(unittest.TestCase):
    def setUp(self):
        sublime.set_clipboard('')
        registers._REGISTER_DATA = {}
        TestsState.view.settings().erase('vintage')
        TestsState.view.settings().erase('vintageous_use_sys_clipboard')
        self.regs = VintageState(TestsState.view).registers
        self.regs.view = mock.Mock()

    def testExtractsSubstrings(self):
        self.regs.view.sel.return_value = [10, 20, 30]
        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': False,
        }
        self.regs.get_selected_text(vi_cmd_data)
        self.assertEqual(self.regs.view.substr.call_count, 3)

    def testReturnsFragments(self):
        self.regs.view.sel.return_value = [10, 20, 30]
        self.regs.view.substr.side_effect = lambda x: x
        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': False,
        }
        rv = self.regs.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, [10, 20, 30])

    def testCanSynthetizeNewLineAtEof(self):
        self.regs.view.substr.return_value = "AAA"
        self.regs.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]
        self.regs.view.size.return_value = 0

        vi_cmd_data = {
            'synthetize_new_line_at_eof': True,
            'yanks_linewise': False,
        }
        rv = self.regs.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA", "AAA\n"])

    def testDoesntSynthetizeNewLineAtEofIfNotNeeded(self):
        self.regs.view.substr.return_value = "AAA\n"
        self.regs.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]
        self.regs.view.size.return_value = 0

        vi_cmd_data = {
            'synthetize_new_line_at_eof': True,
            'yanks_linewise': False,
        }
        rv = self.regs.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA\n", "AAA\n"])

    def testDoesntSynthetizeNewLineAtEofIfNotAtEof(self):
        self.regs.view.substr.return_value = "AAA"
        self.regs.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]
        self.regs.view.size.return_value = 100

        vi_cmd_data = {
            'synthetize_new_line_at_eof': True,
            'yanks_linewise': False,
        }
        rv = self.regs.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA", "AAA"])

    def testCanYankLinewise(self):
        self.regs.view.substr.return_value = "AAA"
        self.regs.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]

        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': True,
        }
        rv = self.regs.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA\n", "AAA\n"])

    def testDoesNotYankLinewiseIfNonEmptyStringFollowedByNewLine(self):
        self.regs.view.substr.return_value = "AAA\n"
        self.regs.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]

        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': True,
        }
        rv = self.regs.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["AAA\n", "AAA\n"])

    def testYankLinewiseIfEmptyStringFollowedByNewLine(self):
        self.regs.view.substr.return_value = "\n"
        self.regs.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]

        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': True,
        }
        rv = self.regs.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["\n\n", "\n\n"])

    def testYankLinewiseIfTwoTrailingNewLines(self):
        self.regs.view.substr.return_value = "\n\n"
        self.regs.view.sel.return_value = [sublime.Region(10, 10), sublime.Region(10, 10)]

        vi_cmd_data = {
            'synthetize_new_line_at_eof': False,
            'yanks_linewise': True,
        }
        rv = self.regs.get_selected_text(vi_cmd_data)
        self.assertEqual(rv, ["\n\n\n", "\n\n\n"])


class Test_yank(unittest.TestCase):
    def setUp(self):
        sublime.set_clipboard('')
        registers._REGISTER_DATA = {}
        TestsState.view.settings().erase('vintage')
        TestsState.view.settings().erase('vintageous_use_sys_clipboard')
        self.regs = VintageState(TestsState.view).registers
        self.regs.view = mock.Mock()

    def testDontYankIfWeDontHaveTo(self):
        vi_cmd_data = {'can_yank': False, 'populates_small_delete_register': False}
        self.regs.yank(vi_cmd_data)
        self.assertEqual(registers._REGISTER_DATA, {})

    def testYanksToUnnamedRegisterIfNoRegisterNameProvided(self):
        vi_cmd_data = {
            'can_yank': True,
            'register': None,
            'populates_small_delete_register': False,
            }

        with mock.patch.object(self.regs, 'get_selected_text') as gst:
            gst.return_value = ['foo']
            self.regs.yank(vi_cmd_data)
            self.assertEqual(registers._REGISTER_DATA, {'"': ['foo']})

    def testYanksToRegisters(self):
        vi_cmd_data = {
            'can_yank': True,
            'register': 'a',
            'populates_small_delete_register': False,
            }

        with mock.patch.object(self.regs, 'get_selected_text') as gst:
            gst.return_value = ['foo']
            self.regs.yank(vi_cmd_data)
            self.assertEqual(registers._REGISTER_DATA, {'"': ['foo'], 'a': ['foo']})

    def testCanPopulateSmallDeleteRegister(self):
        # TODO: Do we really need to populate the unnamed reg when we're populating the small
        # delete one?
        vi_cmd_data = {
            'can_yank': False,
            'populates_small_delete_register': True,
            }

        with mock.patch.object(builtins, 'all') as a, \
             mock.patch.object(self.regs, 'get_selected_text') as gst:
                gst.return_value = ['foo']
                self.regs.view.sel.return_value = range(1)
                a.return_value = True
                self.regs.yank(vi_cmd_data)
                self.assertEqual(registers._REGISTER_DATA, {'"': ['foo'], '-': ['foo']})

    def testDoesNotPopulateSmallDeleteRegisterIfWeShouldNot(self):
        # TODO: Do we really need to populate the unnamed reg when we're populating the small
        # delete one?
        vi_cmd_data = {
            'can_yank': False,
            'populates_small_delete_register': True,
            }

        with mock.patch.object(builtins, 'all') as a, \
             mock.patch.object(self.regs, 'get_selected_text') as gst:
                gst.return_value = ['foo']
                self.regs.view.sel.return_value = range(1)
                a.return_value = False
                self.regs.yank(vi_cmd_data)
                self.assertEqual(registers._REGISTER_DATA, {})

