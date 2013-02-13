import unittest

from Vintageous.test_runner import TestsState

from Vintageous.vi.settings import SublimeSettings


class TestSublimeSettings(unittest.TestCase):
	def setUp(self):
		TestsState.view.settings().erase('foo')
		self.setts = SublimeSettings(view=TestsState.view)

	def testCanInitializeClass(self):
		self.assertEqual(self.setts.view, TestsState.view)

	def testCanSetSetting(self):
		self.assertEqual(TestsState.view.settings().get('foo'), None)
		self.assertEqual(self.setts['foo'], None)

		self.setts['foo'] = 100
		self.assertEqual(TestsState.view.settings().get('foo'), 100)

	def testCanGetSetting(self):
		self.setts = SublimeSettings(view=TestsState.view)
		self.setts['foo'] = 100
		self.assertEqual(self.setts['foo'], 100)

	def testCanGetNonexistingKey(self):
		self.assertEqual(self.setts['foo'], None)
