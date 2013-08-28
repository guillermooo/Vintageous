import unittest

from Vintageous.test_runner import TestsState
from Vintageous.vi.settings import SettingsManager
from Vintageous.vi.settings import SublimeSettings
from Vintageous.vi.settings import VI_OPTIONS
from Vintageous.vi.settings import vi_user_setting
from Vintageous.vi.settings import VintageSettings
from Vintageous.vi.settings import SCOPE_VIEW
from Vintageous.vi.settings import SCOPE_VI_VIEW
from Vintageous.vi.settings import SCOPE_WINDOW
from Vintageous.vi.settings import set_generic_view_setting
from Vintageous.vi.settings import opt_bool_parser
from Vintageous.vi.settings import set_minimap
from Vintageous.vi.settings import opt_rulers_parser


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
		TestsState.view.settings().erase('vintageous_hlsearch')
		TestsState.view.settings().erase('vintageous_foo')
		TestsState.view.window().settings().erase('vintageous_foo')
		self.settsman = VintageSettings(view=TestsState.view)

	def testKnowsAllSettings(self):
		all_settings = [
			'hlsearch',
			'magic',
			'incsearch',
			'autoindent',
			'showminimap',
			'rulers',
		]

		self.assertEqual(sorted(all_settings), sorted(list(VI_OPTIONS.keys())))

	def testSettingsAreCorrectlyDefined(self):
		KNOWN_OPTIONS = {
			'hlsearch': vi_user_setting(scope=SCOPE_VI_VIEW, values=(True, False, '0', '1'), default=True, parser=opt_bool_parser, action=set_generic_view_setting, noable=True),
			'magic': vi_user_setting(scope=SCOPE_VI_VIEW, values=(True, False, '0', '1'), default=True, parser=opt_bool_parser, action=set_generic_view_setting, noable=True),
			'incsearch': vi_user_setting(scope=SCOPE_VI_VIEW, values=(True, False, '0', '1'), default=True, parser=opt_bool_parser, action=set_generic_view_setting, noable=True),
			'autoindent': vi_user_setting(scope=SCOPE_VI_VIEW, values=(True, False, '0', '1'), default=True, parser=None, action=set_generic_view_setting, noable=False),
			'showminimap': vi_user_setting(scope=SCOPE_WINDOW, values=(True, False, '0', '1'), default=True, parser=None, action=set_minimap, noable=True),
			'rulers': vi_user_setting(scope=SCOPE_VIEW, values=None, default=[], parser=opt_rulers_parser, action=set_generic_view_setting, noable=False),
		}

		self.assertEqual(len(KNOWN_OPTIONS), len(VI_OPTIONS))
		for (k, v) in KNOWN_OPTIONS.items():
			self.assertEqual(VI_OPTIONS[k], v)

	def testCanRetrieveDefaultValue(self):
		self.assertEqual(self.settsman['hlsearch'], True)

	def testCanRetrieveDefaultValueIfSetValueIsInvalid(self):
		self.settsman.view.settings().set('vintageous_hlsearch', 100)
		self.assertEqual(self.settsman['hlsearch'], True)

	def testCanRetrieveWindowLevelSettings(self):
		# TODO: use mock to patch dict
		VI_OPTIONS['foo'] = vi_user_setting(scope=SCOPE_WINDOW, values=(100,), default='bar', parser=None, action=None, noable=False)
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
		self.vi_settings = VintageSettings(view=TestsState.view)

	def testDefaultScopeIsView(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=None, values=(100,), default='bar', parser=None, action=None, noable=False)
		self.vi_settings.view.settings().set('vintageous_foo', 100)
		self.assertEqual(self.vi_settings['foo'], 100)
		del VI_OPTIONS['foo']

	def testReturnsDefaultValueIfUnset(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=None, values=(100,), default='bar', parser=None, action=None, noable=False)
		self.assertEqual(self.vi_settings['foo'], 'bar')
		del VI_OPTIONS['foo']

	def testReturnsDefaultValueIfSetToWrongValue(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=None, values=(100,), default='bar', parser=None, action=None, noable=False)
		self.vi_settings.view.settings().set('vintageous_foo', 'maraca')
		self.assertEqual(self.vi_settings['foo'], 'bar')
		del VI_OPTIONS['foo']

	def testReturnsCorrectValue(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=None, values=(100, 200), default='bar', parser=None, action=None, noable=False)
		self.vi_settings.view.settings().set('vintageous_foo', 200)
		self.assertEqual(self.vi_settings['foo'], 200)
		del VI_OPTIONS['foo']

	def testCanReturnWindowLevelSetting(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=SCOPE_WINDOW, values=(100,), default='bar', parser=None, action=None, noable=False)
		self.vi_settings.view.window().settings().set('vintageous_foo', 100)
		self.assertEqual(self.vi_settings['foo'], 100)
		del VI_OPTIONS['foo']

	def testCanReturnViewLevelSetting(self):
		VI_OPTIONS['foo'] = vi_user_setting(scope=SCOPE_VIEW, values=(100,), default='bar', parser=None, action=None, noable=False)
		self.vi_settings.view.settings().set('vintageous_foo', 100)
		self.assertEqual(self.vi_settings['foo'], 100)
		del VI_OPTIONS['foo']
