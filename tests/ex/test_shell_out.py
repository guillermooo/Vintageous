import unittest

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import BufferTest

import Vintageous.ex.plat as plat
from Vintageous.ex.ex_command_parser import parse_command

class Test_ex_shell_out_no_input(BufferTest):
    def testCommandOutput(self):
        test_string = 'Testing!'
        test_command_line = ':!echo "' + test_string + '"'
        ex_cmd = parse_command(test_command_line)
        ex_cmd.args['line_range'] = ex_cmd.line_range

        output_panel = self.view.window().get_output_panel('vi_out')
        self.view.run_command(ex_cmd.command, ex_cmd.args)

        actual = output_panel.substr(self.R(0, output_panel.size()))
        expected = test_string + '\n'
        self.assertEqual(expected, actual)

class Test_ex_shell_out_filter_through_shell(BufferTest):
    @staticmethod
    def getWordCountCommand():
        if plat.HOST_PLATFORM == plat.WINDOWS:
            return None
        else:
            return 'wc -w'

    def testSimpleFilterThroughShell(self):
        word_count_command = self.__class__.getWordCountCommand()
        # TODO implement test for Windows.
        if not word_count_command:
            return True
        set_text(self.view, 'One two three four\nfive six seven eight\nnine ten.')
        add_sel(self.view, self.R((0, 8), (1, 3)))

        test_command_line = ":'<,'>!" + word_count_command
        ex_cmd = parse_command(test_command_line)
        ex_cmd.args['line_range'] = ex_cmd.line_range

        self.view.run_command(ex_cmd.command, ex_cmd.args)

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = '8\nnine ten.'
        self.assertEqual(expected, actual)
        self.assertEqual(1, len(self.view.sel()))
        cursor = get_sel(self.view, 0)
        self.assertEqual(cursor.begin(), cursor.end())
        self.assertEqual(self.view.text_point(0, 0), cursor.begin())

    def testMultipleFilterThroughShell(self):
        word_count_command = self.__class__.getWordCountCommand()
        # TODO implement test for Windows.
        if not word_count_command:
            return True
        set_text(self.view, '''Beginning of test!
One two three four
five six seven eight
nine ten.
These two lines shouldn't be replaced
by the command.
One two three four five six
seven eight nine
ten
eleven
twelve
End of Test!
''')
        # Two selections touching all numeric word lines.
        add_sel(self.view, self.R((1, 11), (3, 1)))
        add_sel(self.view, self.R((6, 1), (10, 5)))

        test_command_line = ":'<,'>!" + word_count_command
        ex_cmd = parse_command(test_command_line)
        ex_cmd.args['line_range'] = ex_cmd.line_range

        self.view.run_command(ex_cmd.command, ex_cmd.args)

        actual = self.view.substr(self.R(0, self.view.size()))
        expected = '''Beginning of test!
10
These two lines shouldn't be replaced
by the command.
12
End of Test!
'''
        self.assertEqual(expected, actual)
        self.assertEqual(2, len(self.view.sel()))
        cursor0 = get_sel(self.view, 0)
        cursor1 = get_sel(self.view, 1)
        self.assertEqual(cursor0.begin(), cursor0.end())
        self.assertEqual(cursor1.begin(), cursor1.end())
        self.assertEqual(self.view.text_point(1, 0), cursor0.begin())
        self.assertEqual(self.view.text_point(4, 0), cursor1.begin())

