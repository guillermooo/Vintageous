from Vintageous.vi.utils import modes

from collections import namedtuple

from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import get_sel
from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest


# TODO: Test against folded regions.
# TODO: Ensure that we only create empty selections while testing. Add assert_all_sels_empty()?
test_data = namedtuple('test_data', 'cmd initial_text regions cmd_params expected actual_func msg')
region_data = namedtuple('region_data', 'regions')


def get_text(test):
    return test.view.substr(test.R(0, test.view.size()))

def  first_sel_wrapper(test):
    return first_sel(test.view)


TESTS_MODES = (
    # NORMAL mode
    test_data(cmd='_vi_j', initial_text='abc\nabc\nabc', regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'xpos': 1},
              expected=region_data([(1, 1), (1, 1)]), actual_func=first_sel_wrapper, msg='move one line down'),
    test_data(cmd='_vi_j', initial_text=(''.join('abc\n' * 60)), regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'count': 50, 'xpos': 1},
              expected=region_data([(50, 1), (50, 1)]), actual_func=first_sel_wrapper, msg='move many lines down'),
    test_data(cmd='_vi_j', initial_text=(''.join('abc\n' * 60)), regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'count': 50, 'xpos': 1},
              expected=region_data([(50, 1), (50, 1)]), actual_func=first_sel_wrapper, msg='move many lines down'),
    test_data(cmd='_vi_j', initial_text='foo\nfoo bar\nfoo bar', regions=[[1, 1]], cmd_params={'mode': modes.NORMAL, 'count': 1, 'xpos': 1},
              expected=region_data([(1, 1), (1, 1)]), actual_func=first_sel_wrapper, msg='move onto longer line'),
    test_data(cmd='_vi_j', initial_text='foo bar\nfoo\nbar', regions=[[5, 5]], cmd_params={'mode': modes.NORMAL, 'count': 1, 'xpos': 5},
              expected=region_data([(1, 4), (1, 4)]), actual_func=first_sel_wrapper, msg='move onto shorter line'),
    test_data(cmd='_vi_j', initial_text='\nfoo\nbar', regions=[[0, 0]], cmd_params={'mode': modes.NORMAL, 'count': 1, 'xpos': 0},
              expected=region_data([(1, 0), (1, 0)]), actual_func=first_sel_wrapper, msg='move from empty line'),
    )


TESTS = TESTS_MODES


class Test_vi_j(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            self.write(data.initial_text)
            for region in data.regions:
                self.add_sel(self.R(*region))

            self.view.run_command(data.cmd, data.cmd_params)

            msg = "failed at test index {0} {1}".format(i, data.msg)
            actual = data.actual_func(self)

            if isinstance(data.expected, region_data):
                self.assertEqual(self.R(*data.expected.regions), actual, msg)
            else:
                self.assertEqual(data.expected, actual, msg)


class Test_vi_j_InNormalMode(ViewTest):
    def testMoveFromEmptyLineToEmptyLine(self):
        self.write('\n\nbar')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_j', {'mode': modes.NORMAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveTooFar(self):
        self.write('foo\nbar\nbaz')
        self.clear_sel()
        self.add_sel(a=1, b=1)

        self.view.run_command('_vi_j', {'mode': modes.NORMAL, 'count': 10000, 'xpos': 1})

        target = self.view.text_point(2, 1)
        expected = self.R(target, target)

        self.assertEqual(expected, first_sel(self.view))


class Test_vi_j_InVisualMode(ViewTest):
    def testMoveOne(self):
        self.write('abc\nabc\nabc')
        self.clear_sel()
        self.add_sel(a=1, b=2)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 2)
        expected = self.R(1, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveReversedNoCrossOver(self):
        self.write('abc\nabc\nabc')
        self.clear_sel()
        self.add_sel(a=10, b=1)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 1)
        expected = self.R(10, target)

        self.assertEqual(expected, first_sel(self.view))

    # FIXME: This is wrong in the implementation.
    def testMoveReversedCrossOver(self):
        self.write('abc\nabc\nabc')
        self.clear_sel()
        self.add_sel(a=6, b=1)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 2, 'xpos': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(5, target)

        self.assertEqual(expected, first_sel(self.view))

    # FIXME: This is wrong in the implementation.
    def testMoveReversedCrossOverTooFar(self):
        self.write('abc\nabc\nabc')
        self.clear_sel()
        self.add_sel(a=6, b=1)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 100, 'xpos': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(5, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveReversedBackToSameLine(self):
        self.write('abc\nabc\nabc')
        self.clear_sel()
        self.add_sel(a=6, b=1)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 1)
        expected = self.R(target, 6)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveReversedDownFromSameLine(self):
        self.write('abc\nabc\nabc')
        self.clear_sel()
        self.add_sel(a=6, b=5)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(5, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany(self):
        self.write(''.join(('abc\n',) * 60))
        self.clear_sel()
        self.add_sel(a=1, b=2)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 50, 'xpos': 1})

        target = self.view.text_point(50, 2)
        expected = self.R(1, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoLongerLine(self):
        self.write('foo\nfoo bar\nfoo bar')
        self.clear_sel()
        self.add_sel(a=1, b=2)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 2)
        expected = self.R(1, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoShorterLine(self):
        self.write('foo bar\nfoo\nbar')
        self.clear_sel()
        self.add_sel(a=5, b=6)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 1, 'xpos': 5})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(5, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLine(self):
        self.write('\nfoo\nbar')
        self.clear_sel()
        self.add_sel(a=0, b=1)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 1)
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLineToEmptyLine(self):
        self.write('\n\nbar')
        self.clear_sel()
        self.add_sel(a=0, b=1)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 1)
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveTooFar(self):
        self.write('foo\nbar\nbaz')
        self.clear_sel()
        self.add_sel(a=1, b=2)

        self.view.run_command('_vi_j', {'mode': modes.VISUAL, 'count': 10000, 'xpos': 1})

        target = self.view.text_point(2, 2)
        expected = self.R(1, target)

        self.assertEqual(expected, first_sel(self.view))


# TODO: Ensure that we only create empty selections while testing. Add assert_all_sels_empty()?
class Test_vi_j_InInternalNormalMode(ViewTest):
    def testMoveOne(self):
        self.write('abc\nabc\nabc')
        self.clear_sel()
        self.add_sel(a=1, b=1)

        self.view.run_command('_vi_j', {'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany(self):
        self.write(''.join(('abc\n',) * 60))
        self.clear_sel()
        self.add_sel(a=1, b=1)

        self.view.run_command('_vi_j', {'mode': modes.INTERNAL_NORMAL, 'count': 50, 'xpos': 1})

        target = self.view.text_point(50, 2)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoLongerLine(self):
        self.write('foo\nfoo bar\nfoo bar')
        self.clear_sel()
        self.add_sel(a=1, b=1)

        self.view.run_command('_vi_j', {'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveOntoShorterLine(self):
        self.write('foo bar\nfoo\nbar')
        self.clear_sel()
        self.add_sel(a=5, b=5)

        self.view.run_command('_vi_j', {'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 5})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLine(self):
        self.write('\nfoo\nbar')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_j', {'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLineToEmptyLine(self):
        self.write('\n\nbar')
        self.clear_sel()
        self.add_sel(a=0, b=0)

        self.view.run_command('_vi_j', {'mode': modes.INTERNAL_NORMAL, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveTooFar(self):
        self.write('foo\nbar\nbaz')
        self.clear_sel()
        self.add_sel(a=1, b=1)

        self.view.run_command('_vi_j', {'mode': modes.INTERNAL_NORMAL, 'count': 10000, 'xpos': 1})

        target = self.view.text_point(2, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))


class Test_vi_j_InVisualLineMode(ViewTest):
    def testMoveOne(self):
        self.write('abc\nabc\nabc')
        self.clear_sel()
        self.add_sel(a=0, b=4)
        self.view.run_command('_vi_j', {'mode': modes.VISUAL_LINE, 'count': 1, 'xpos': 1})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveMany(self):
        self.write(''.join(('abc\n',) * 60))
        self.clear_sel()
        self.add_sel(a=0, b=4)
        self.view.run_command('_vi_j', {'mode': modes.VISUAL_LINE, 'count': 50, 'xpos': 1})

        target = self.view.text_point(50, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLine(self):
        self.write('\nfoo\nbar')
        self.clear_sel()
        self.add_sel(a=0, b=1)
        self.view.run_command('_vi_j', {'mode': modes.VISUAL_LINE, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveFromEmptyLineToEmptyLine(self):
        self.write('\n\nbar')
        self.clear_sel()
        self.add_sel(a=0, b=1)
        self.view.run_command('_vi_j', {'mode': modes.VISUAL_LINE, 'count': 1, 'xpos': 0})

        target = self.view.text_point(1, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))

    def testMoveTooFar(self):
        self.write('foo\nbar\nbaz')
        self.clear_sel()
        self.add_sel(a=0, b=4)
        self.view.run_command('_vi_j', {'mode': modes.VISUAL_LINE, 'count': 10000, 'xpos': 1})

        target = self.view.text_point(2, 0)
        target = self.view.full_line(target).b
        expected = self.R(0, target)

        self.assertEqual(expected, first_sel(self.view))
