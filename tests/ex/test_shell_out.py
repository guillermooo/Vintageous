import unittest
import os

import sublime

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import ViewTest

import Vintageous.ex.plat as plat

class Test_ex_shell_out_no_input(ViewTest):
    @unittest.skipIf(os.name == 'nt', 'not supported on Windows')
    def testCommandOutput(self):
        test_string = 'Testing!'
        test_command_line = '!echo "' + test_string + '"'
        output_panel = self.view.window().get_output_panel('vi_out')
        self.view.window().run_command('ex_shell_out', {'command_line': test_command_line})

        actual = output_panel.substr(self.R(0, output_panel.size()))
        expected = test_string + '\n'
        self.assertEqual(expected, actual)

    @unittest.skipIf(os.name != 'nt', 'Windows')
    def testCommandOutput(self):
        test_string = 'Testing!'
        test_command_line = '!echo "' + test_string + '"'
        output_panel = self.view.window().get_output_panel('vi_out')
        self.view.window().run_command('ex_shell_out', {'command_line': test_command_line})

        actual = output_panel.substr(self.R(0, output_panel.size()))
        expected = '\\"{0}\\"\n'.format(test_string)
        self.assertEqual(expected, actual)

    def tearDown(self):
        # XXX: Ugly hack to make sure that the output panels created in these
        # tests don't hide the overall progress panel.
        self.view.window().run_command('show_panel', {
                                       'panel': 'output.vintageous.tests'
                                       })
        super().tearDown()


class Test_ex_shell_out_filter_through_shell(ViewTest):
    @staticmethod
    def getWordCountCommand():
        if plat.HOST_PLATFORM == plat.WINDOWS:
            return None
        else:
            return 'wc -w'

    @unittest.skipIf(sublime.platform() == 'windows' or sublime.platform() == "osx", 'Windows or OSX')
    def testSimpleFilterThroughShell(self):
        word_count_command = self.__class__.getWordCountCommand()
        # TODO implement test for Windows.
        if not word_count_command:
            return True
        self.view.sel().clear()
        self.write('''aaa
bbb
ccc''')
        self.add_sel(self.R((0, 2), (0, 2)))

        test_command_line = ".!" + word_count_command

        self.view.run_command('ex_shell_out', {
                'command_line': test_command_line
                })

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = '''1
bbb
ccc'''
        self.assertEqual(expected, actual)

    @unittest.skipIf(sublime.platform() == 'windows' or sublime.platform() == "osx", 'Windows or OSX')
    def testMultipleFilterThroughShell(self):
        word_count_command = self.__class__.getWordCountCommand()
        # TODO implement test for Windows.
        if not word_count_command:
            return True
        self.view.sel().clear()
        self.write('''aaa
bbb
ccc
''')
        # Two selections touching all numeric word lines.
        self.add_sel(self.R((1, 0), (1, 0)))

        test_command_line = ".!" + word_count_command

        self.view.run_command('ex_shell_out', {
                'command_line': test_command_line
                })

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = '''aaa
1
ccc
'''
        self.assertEqual(expected, actual)
