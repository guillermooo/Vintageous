from collections import namedtuple

from Vintageous.tests import ViewTest
from Vintageous.vi.utils import modes

test_data = namedtuple('test_data', 'text startRegion mode expectedRegion msg')

NORMAL_CASES = (
    test_data('012a4', (3, 3), modes.NORMAL, (0, 0), 'Move to beginning'),
    test_data('  2a4', (3, 3), modes.NORMAL, (2, 2), 'Move to first non-space left'),
    test_data('  234', (1, 1), modes.NORMAL, (2, 2), 'Move to first non-space right'),
)

INTERNAL_NORMAL_CASES = (
    test_data('012a4', (3, 3), modes.INTERNAL_NORMAL, (3, 0), 'Internal move to beginning'),
    test_data('  2a4', (3, 3), modes.INTERNAL_NORMAL, (3, 2), 'Internal move to first non-space left'),
    test_data('  234', (1, 1), modes.INTERNAL_NORMAL, (1, 2), 'Internal move to first non-space right'),
    test_data('  a34', (2, 3), modes.INTERNAL_NORMAL, (2, 2), 'Internal move to first non-space self'),
)

VISUAL_MULTI_CHAR_CASES = (
    test_data('0b2a45', (4, 1), modes.VISUAL, (4, 0), 'Visual no crossover'),
    test_data('0a2b45', (1, 4), modes.VISUAL, (2, 0), 'Visual crossover'),
    test_data('  2ba5', (5, 3), modes.VISUAL, (5, 2), 'Visual first non-space right no crossover'),
    test_data('  2ab5', (3, 5), modes.VISUAL, (4, 2), 'Visual first non-space right crossover'),
    test_data('  2345', (2, 0), modes.VISUAL, (1, 3), 'Visual first non-space left crossover'),
    test_data('  2345', (0, 2), modes.VISUAL, (0, 3), 'Visual first non-space left no crossover'),
    test_data('  23a5', (5, 1), modes.VISUAL, (5, 2), 'Visual first non-space reverse'),
    test_data('  23b5', (1, 5), modes.VISUAL, (1, 3), 'Visual first non-space forward'),
)

VISUAL_ONE_CHAR_CASES = (
    test_data('f', (0, 1), modes.VISUAL, (0, 1), 'Visual single character forward'),
    test_data('r', (1, 0), modes.VISUAL, (1, 0), 'Visual single character reverse'),
)

VISUAL_MULTI_LINE_CASES = (
    test_data(' 123\n 678', (0, 5), modes.VISUAL, (0, 2), 'Visual caret on newline'),
    test_data(' 123\n 678', (8, 4), modes.VISUAL, (8, 1), 'Visual caret on newline reverse'),
    test_data(' 123\n 678', (2, 8), modes.VISUAL, (2, 7), 'Visual forward multiline'),
    test_data(' 123\n 678', (8, 2), modes.VISUAL, (8, 1), 'Visual reverse multiline'),
)

class Test_vi_hat(ViewTest):
    def runTests(self, data):
        for (i, data) in enumerate(data):
            self.write(data.text)
            self.clear_sel()
            self.add_sel(self.R(*data.startRegion))
            self.view.run_command('_vi_hat', {'mode': data.mode, 'count': 1})
            self.assert_equal_regions(self.R(*data.expectedRegion), self.first_sel(),
                "Failed on index {} {} : Text:\"{}\" Region:{}"
                    .format(i, data.msg, data.text, data.startRegion))

    def testNormalCases(self):
        self.runTests(NORMAL_CASES)

    def testInternalNormalCases(self):
        self.runTests(INTERNAL_NORMAL_CASES)

    def testVisualMultipleCharacterCases(self):
        self.runTests(VISUAL_MULTI_CHAR_CASES)

    def testVisualSingleCharacterCases(self):
        self.runTests(VISUAL_ONE_CHAR_CASES)

    def testVisualMultipleLinesCases(self):
        self.runTests(VISUAL_MULTI_LINE_CASES)
