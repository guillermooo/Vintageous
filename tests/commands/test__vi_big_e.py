from collections import namedtuple

from Vintageous.tests import ViewTest
from Vintageous.vi.utils import modes

test_data = namedtuple('test_data', 'text startRegion mode expectedRegion msg')

ALL_CASES = (
	test_data('01. 4',  (1, 1), modes.NORMAL,          (2, 2), 'Normal'),
	test_data('012 4',  (1, 1), modes.INTERNAL_NORMAL, (1, 3), 'Internal Normal'),
	test_data('0ab3 5', (1, 3), modes.VISUAL,          (1, 4), 'Visual Forward'),
	test_data('0b2 a5', (5, 1), modes.VISUAL,          (5, 2), 'Visual Reverse no crossover'),
	test_data('0ba3 5', (3, 1), modes.VISUAL,          (2, 4), 'Visual Reverse crossover'),
)

class Test_vi_big_e(ViewTest):
	def runTests(self, data):
		for (i, data) in enumerate(data):
			self.write(data.text)
			self.clear_sel()
			self.add_sel(self.R(*data.startRegion))
			self.view.run_command('_vi_big_e', {'mode': data.mode, 'count': 1})
			self.assert_equal_regions(self.R(*data.expectedRegion), self.first_sel(),
				"Failed on index {} {} : Text:\"{}\" Region:{}"
					.format(i, data.msg, data.text, data.startRegion))

	def testAllCases(self):
		self.runTests(ALL_CASES)
