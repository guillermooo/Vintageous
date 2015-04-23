from collections import namedtuple

from Vintageous.tests import ViewTest
from Vintageous.vi.utils import modes

test_data = namedtuple('test_data', 'text startRegion mode count expectedRegion msg')

NORMAL_CASES = (
    test_data('  2a4', (3, 3), modes.NORMAL, 1, (2, 2), 'Move to first non-space left'),
    test_data('  234', (1, 1), modes.NORMAL, 1, (2, 2), 'Move to first non-space right'),
)

INTERNAL_NORMAL_CASES = (
    # Test cases for 'c' behavior, 'd' behaves differently
    test_data(' 12\n 56', (0, 0), modes.INTERNAL_NORMAL, 1, (0, 4), 'Internal before first space'),
    test_data(' 12\n 56', (2, 2), modes.INTERNAL_NORMAL, 1, (0, 4), 'Internal after first space'),
    test_data(' 12\n 56', (6, 6), modes.INTERNAL_NORMAL, 1, (4, 8), 'Internal from 2nd line'),
)

VISUAL_MULTI_CHAR_CASES = (
    test_data('  2ba5', (5, 3), modes.VISUAL, 1, (5, 2), 'Visual first non-space right no crossover'),
    test_data('  2ab5', (3, 5), modes.VISUAL, 1, (4, 2), 'Visual first non-space right crossover'),
    test_data('  2345', (2, 0), modes.VISUAL, 1, (1, 3), 'Visual first non-space left crossover'),
    test_data('  2345', (0, 2), modes.VISUAL, 1, (0, 3), 'Visual first non-space left no crossover'),
    test_data('  23b5', (1, 5), modes.VISUAL, 1, (1, 3), 'Visual first non-space forward'),
    test_data('  23a5', (5, 1), modes.VISUAL, 1, (5, 2), 'Visual first non-space reverse'),
)

VISUAL_ONE_CHAR_CASES = (
    test_data('f', (0, 1), modes.VISUAL, 1, (0, 1), 'Visual single character forward'),
    test_data('r', (1, 0), modes.VISUAL, 1, (1, 0), 'Visual single character reverse'),
)

VISUAL_MULTI_LINE_CASES = (
    test_data(' 123\n 678', (0, 5), modes.VISUAL, 1, (0, 2), 'Visual caret on newline'),
    test_data(' 123\n 678', (8, 4), modes.VISUAL, 1, (8, 1), 'Visual caret on newline reverse'),
    test_data(' 123\n 678', (2, 8), modes.VISUAL, 1, (2, 7), 'Visual forward multiline'),
    test_data(' 123\n 678', (8, 2), modes.VISUAL, 1, (8, 1), 'Visual reverse multiline'),
)

MULTI_COUNT_NORMAL_CASES = (
    test_data(' 123\n 678', (0, 0), modes.NORMAL, 2, (6, 6), 'Normal count 2 move right'),
    test_data(' 123\n 678', (2, 2), modes.NORMAL, 2, (6, 6), 'Normal count 2 move left'),
    test_data(' 123\n 678', (0, 0), modes.NORMAL, 3, (6, 6), 'Normal count 3 with only 2 lines'),
)

MULTI_COUNT_INTERNAL_NORMAL_CASES = (
    # Test cases for 'c' behavior, 'd' behaves differently
    test_data(' 123\n 678\n bcd', (2, 2), modes.INTERNAL_NORMAL, 2, (0, 10),  'Internal count 2'),
    test_data(' 123\n 678\n bcd', (7, 7), modes.INTERNAL_NORMAL, 3, (5, 15), 'Internal over count'),
)

MULTI_COUNT_VISUAL_CASES = (
    test_data(' 123\n 678', (0, 3), modes.VISUAL, 2, (0, 7), 'Visual count 2 no crossover'),
    test_data(' 123\n 678', (3, 0), modes.VISUAL, 2, (2, 7), 'Visual count 2 crossover'),
    test_data(' 123\n 678', (0, 3), modes.VISUAL, 3, (0, 7), 'Visual count 3 with only 2 lines'),
)

class Test_vi_underscore(ViewTest):
    def runTests(self, data):
        for (i, data) in enumerate(data):
            self.write(data.text)
            self.clear_sel()
            self.add_sel(self.R(*data.startRegion))
            self.view.run_command('_vi_underscore', {'mode': data.mode, 'count': data.count})
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

    def testMultipleCountNormalCases(self):
        self.runTests(MULTI_COUNT_NORMAL_CASES)

    def testMultipleCountInternalNormalCases(self):
        self.runTests(MULTI_COUNT_INTERNAL_NORMAL_CASES)

    def testMultipleCountVisualCases(self):
        self.runTests(MULTI_COUNT_VISUAL_CASES)
