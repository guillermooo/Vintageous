from collections import namedtuple

from Vintageous.tests import ViewTest
from Vintageous.vi.utils import modes

test_data = namedtuple('test_data', 'text startRegion findChar mode expectedRegion msg')

NORMAL_CASES = (
    test_data('0x23a5', (4, 4), 'x', modes.NORMAL, (2, 2), 'Find behind'),
    test_data('012xa5', (4, 4), 'x', modes.NORMAL, (4, 4), 'Find previous'),
    test_data('0123x5', (4, 4), 'x', modes.NORMAL, (4, 4), 'Find self'),
    test_data('0xx3a5', (4, 4), 'x', modes.NORMAL, (3, 3), 'Find multiple'),
    test_data('01x3x5', (4, 4), 'x', modes.NORMAL, (3, 3), 'Find self multiple'),
)

INTERNAL_NORMAL_CASES = (
    test_data('0x23a5', (4, 4), 'x', modes.INTERNAL_NORMAL, (4, 2), 'Find behind'),
    test_data('012xa5', (4, 4), 'x', modes.INTERNAL_NORMAL, (4, 4), 'Find previous'),
    test_data('0123x5', (4, 4), 'x', modes.INTERNAL_NORMAL, (4, 4), 'Find self'),
    test_data('0xx3a5', (4, 4), 'x', modes.INTERNAL_NORMAL, (4, 3), 'Find multiple'),
    test_data('01x3x5', (4, 4), 'x', modes.INTERNAL_NORMAL, (4, 3), 'Find self multiple'),
)

VISUAL_MULTI_CHAR_CASES = (
    test_data('0x2ba5', (5, 3), 'x', modes.VISUAL, (5, 2), 'Reverse'),
    test_data('0x23a5', (5, 1), 'x', modes.VISUAL, (5, 1), 'Reverse find b'),
    test_data('0ax3b5', (1, 5), 'x', modes.VISUAL, (1, 4), 'Forward no crossover'),
    test_data('0x2ab5', (3, 5), 'x', modes.VISUAL, (4, 2), 'Forward crossover'),
    test_data('01x3b5', (2, 5), 'x', modes.VISUAL, (2, 4), 'Forward find a'),
    test_data('01a3x5', (2, 5), 'x', modes.VISUAL, (2, 5), 'Forward find b'),
    test_data('0xb3a5', (5, 2), 'x', modes.VISUAL, (5, 2), 'Reverse find b-1'),
    test_data('0a2xb5', (1, 5), 'x', modes.VISUAL, (1, 5), 'Forward find b-1'),
    test_data('0xa3b5', (2, 5), 'x', modes.VISUAL, (2, 3), 'Forward find a-1'),
)

VISUAL_ONE_CHAR_CASES = (
    test_data('xa', (2, 0), 'x', modes.VISUAL, (2, 0), 'Reverse find b'),
    test_data('xb', (0, 2), 'x', modes.VISUAL, (0, 2), 'Forward find a'),
    test_data('xr', (2, 1), 'x', modes.VISUAL, (2, 1), 'Reverse find previous'),
    test_data('xf', (1, 2), 'x', modes.VISUAL, (1, 2), 'Forward find previous'),
    test_data('r',  (1, 0), 'r', modes.VISUAL, (1, 0), 'Reverse find self'),
    test_data('f',  (0, 1), 'f', modes.VISUAL, (0, 1), 'Forward find self'),
)

VISUAL_MULTI_MATCHES_CASES = (
    test_data('0xxba5', (5, 3), 'x', modes.VISUAL, (5, 3), 'Reverse find first'),
    test_data('01xxa5', (5, 3), 'x', modes.VISUAL, (5, 3), 'Reverse find b'),
    test_data('01xxb5', (3, 5), 'x', modes.VISUAL, (3, 5), 'Forward find a'),
    test_data('01xxb5', (2, 5), 'x', modes.VISUAL, (2, 5), 'Forward find a'),
    test_data('01xax5', (3, 5), 'x', modes.VISUAL, (3, 4), 'Forward find b'),
)

VISUAL_MULTI_LINE_CASES = (
    test_data('012\n456',   (2, 7), '0', modes.VISUAL, (2, 7), 'Select L1->L2, find on L1'),
    test_data('012\n456',   (2, 7), '4', modes.VISUAL, (2, 6), 'Select L1->L2, find on L2'),
    test_data('012\n456',   (2, 4), '0', modes.VISUAL, (3, 1), 'Select L1->LF, find on L1'),
    test_data('012\n456',   (2, 4), '5', modes.VISUAL, (2, 4), 'Select L1->LF, find on L2'),
    test_data('012\n456',   (7, 2), '0', modes.VISUAL, (7, 1), 'Select L2->L1, find on L1'),
    test_data('012\n456',   (7, 2), '4', modes.VISUAL, (7, 2), 'Select L2->L1, find on L2'),
    test_data('012\n456',   (7, 3), '0', modes.VISUAL, (7, 1), 'Select L2->LF, find on L1'),
    test_data('012\n456',   (7, 3), '4', modes.VISUAL, (7, 3), 'Select L2->LF, find on L2'),
    test_data('0123\n5678', (2, 4), '0', modes.VISUAL, (3, 1), 'Select L1->LF-1, find on L1'),
)

SKIP_CASES = (
    test_data('xxxx', (2, 2), 'x', modes.NORMAL, (1, 1), 'Skip past previous match'),
    test_data('xxxx', (1, 1), 'x', modes.NORMAL, (1, 1), 'Does not skip past final match'),
)

class Test_vi_big_t(ViewTest):
    def runTests(self, data, skipping=False):
        for (i, data) in enumerate(data):
            self.write(data.text)
            self.clear_sel()
            self.add_sel(self.R(*data.startRegion))
            self.view.run_command('_vi_reverse_find_in_line',
                {'mode': data.mode, 'count': 1, 'char': data.findChar, 'inclusive': False, 'skipping': skipping})
            self.assert_equal_regions(self.R(*data.expectedRegion), self.first_sel(),
                "Failed on index {} {} : Text:\"{}\" Region:{} Find:'{}'"
                    .format(i, data.msg, data.text, data.startRegion, data.findChar))

    def runTestsWithSkip(self, data):
        self.runTests(data, skipping=True)

    def testNormalCases(self):
        self.runTests(NORMAL_CASES)

    def testInternalNormalCases(self):
        self.runTests(INTERNAL_NORMAL_CASES)

    def testVisualMultipleCharacterCases(self):
        self.runTests(VISUAL_MULTI_CHAR_CASES)

    def testVisualSingleCharacterCases(self):
        self.runTests(VISUAL_ONE_CHAR_CASES)

    def testVisualMultipleMatchesCases(self):
        self.runTests(VISUAL_MULTI_MATCHES_CASES)

    def testVisualMultipleLinesCases(self):
        self.runTests(VISUAL_MULTI_LINE_CASES)

    def testSkipCases(self):
        self.runTestsWithSkip(SKIP_CASES)
