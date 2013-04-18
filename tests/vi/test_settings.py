import unittest

from Vintageous.test_runner import TestsState
from Vintageous.vi.settings import SettingsManager
from Vintageous.vi.settings import SublimeSettings
from Vintageous.vi.settings import VI_OPTIONS
from Vintageous.vi.settings import vi_user_setting
from Vintageous.vi.settings import VintageSettings
from Vintageous.vi.settings import SCOPE_VIEW
from Vintageous.vi.settings import SCOPE_WINDOW


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

class TestViEditorSettings(unittest.TestCase):
	def setUp(self):
		TestsState.view.settings().erase('vintage')
		TestsState.view.settings().erase('vintageous_nohlsearch')
		TestsState.view.settings().erase('vintageous_foo')
		TestsState.view.window().settings().erase('vintageous_foo')
		self.settsman = VintageSettings(view=TestsState.view)

	def testKnowsAllSettings(self):
		all_settings = [
			'nohlsearch',
			'incsearch'
			]

		self.assertEqual(sorted(all_settings), sorted(list(VI_OPTIONS.keys())))

	def testSettingsAreCorrectlyDefined(self):
		self.assertEqual(VI_OPTIONS['nohlsearch'], vi_user_setting(scope=SCOPE_VIEW, values=(True, False), default=False, parser=None))
		self.assertEqual(VI_OPTIONS['incsearch'], vi_user_setting(scope=SCOPE_VIEW, values=(True, False), default=True, parser=None))

	def testCanRetrieveDefaultValue(self):
		self.assertEqual(self.settsman['nohlsearch'], False)

	def testCanRetrieveDefaultValueIfSetValueIsInvalid(self):
		self.settsman.view.settings().set('vintageous_nohlsearch', 100)
		self.assertEqual(self.settsman['nohlsearch'], False)

	def testCanRetrieveWindowLevelSettings(self):
		# TODO: use mock to patch dict
		VI_OPTIONS['foo'] = vi_user_setting(scope=SCOPE_WINDOW, values=(100,), default='bar', parser=None)
		self.settsman.view.window().settings().set('vintageous_foo', 100)
		self.assertEqual(self.settsman['foo'], 100)
		del VI_OPTIONS['foo']

	@unittest.skip("Not implemented")
	def testCanDiscriminateWindowSettingsFromViewSettings(self):
		pass
		# TODO: use mock to patch dict
		# TODO: Scopes must be consulted in order from bottom to top: VIEW, WINDOW.
		# VI_OPTIONS['foo'] = vi_user_setting(scope=SCOPE_WINDOW, values=(True, False), default='bar', parser=None)
		# VI_OPTIONS['foo'] = vi_user_setting(scope=SCOPE_VIEW, values=(True, False), default='buzz', parser=None)


class Test_get_option(unittest.TestCase):
	def setUp(self):
		TestsState.view.settings().erase('vintage')
		TestsState.view.settings().erase('vintageous_foo')
		self.settsman = VintageSettings(view=TestsState.view)

	def testDefaultScopeIsView(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=None, values=(100,), default='bar', parser=None)
		self.settsman.view.settings().set('vintageous_foo', 100)
		self.assertEqual(self.settsman['foo'], 100)

	def testReturnsDefaultValueIfUnset(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=None, values=(100,), default='bar', parser=None)
		self.assertEqual(self.settsman['foo'], 'bar')

	def testReturnsDefaultValueIfSetToWrongValue(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=None, values=(100,), default='bar', parser=None)
		self.settsman.view.settings().set('vintageous_foo', 'maraca')
		self.assertEqual(self.settsman['foo'], 'bar')

	def testReturnsCorrectValue(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=None, values=(100, 200), default='bar', parser=None)
		self.settsman.view.settings().set('vintageous_foo', 200)
		self.assertEqual(self.settsman['foo'], 200)

	def testCanReturnWindowLevelSetting(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=SCOPE_WINDOW, values=(100,), default='bar', parser=None)
		self.settsman.view.window().settings().set('vintageous_foo', 100)
		self.assertEqual(self.settsman['foo'], 100)

	def testCanReturnViewLevelSetting(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=SCOPE_VIEW, values=(100,), default='bar', parser=None)
		self.settsman.view.settings().set('vintageous_foo', 100)
		self.assertEqual(self.settsman['foo'], 100)
