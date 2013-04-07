import unittest

from Vintageous.test_runner import TestsState
from Vintageous.vi.settings import (SublimeSettings, VintageSettings,
								    SettingsManager,)


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
		self.setts['foo'] = 100
		self.assertEqual(self.setts['foo'], 100)

	def testCanGetNonexistingKey(self):
		self.assertEqual(self.setts['foo'], None)


class TestVintageSettings(unittest.TestCase):
	def setUp(self):
		TestsState.view.settings().erase('vintage')
		self.setts = VintageSettings(view=TestsState.view)

	def testCanInitializeClass(self):
		self.assertEqual(self.setts.view, TestsState.view)
		self.assertEqual(TestsState.view.settings().get('vintage'), {})

	def testCanSetSetting(self):
		self.assertEqual(self.setts['foo'], None)

		self.setts['foo'] = 100
		self.assertEqual(TestsState.view.settings().get('vintage')['foo'], 100)

	def testCanGetSetting(self):
		self.setts['foo'] = 100
		self.assertEqual(self.setts['foo'], 100)

	def testCanGetNonexistingKey(self):
		self.assertEqual(self.setts['foo'], None)


class TestSettingsManager(unittest.TestCase):
	def setUp(self):
		TestsState.view.settings().erase('vintage')
		self.settsman = SettingsManager(view=TestsState.view)

	def testCanInitializeClass(self):
		self.assertEqual(TestsState.view, self.settsman.v)

	def testCanAccessViSsettings(self):
		self.settsman.vi['foo'] = 100
		self.assertEqual(self.settsman.vi['foo'], 100)

	def testCanAccessViewSettings(self):
		self.settsman.view['foo'] = 100
		self.assertEqual(self.settsman.view['foo'], 100)