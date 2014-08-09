import unittest

import sublime

from Vintageous.tests import ViewTest
from Vintageous.vi.variables import _SPECIAL_STRINGS
from Vintageous.vi.variables import _DEFAULTS
from Vintageous.vi.variables import _VARIABLES
from Vintageous.vi.variables import is_key_name
from Vintageous.vi.variables import set_
from Vintageous.vi.variables import get
from Vintageous.vi import variables


class Test_special_strings(ViewTest):
    def test_IncludesLeaderString(self):
        self.assertEqual(_SPECIAL_STRINGS['<leader>'], 'mapleader')

    def test_IncludesLocalLeaderString(self):
        self.assertEqual(_SPECIAL_STRINGS['<localleader>'], 'maplocalleader')


class Test_default_values(ViewTest):
    def test_HasDefaultValueForLeader(self):
        self.assertEqual(_DEFAULTS['mapleader'], '\\')

    def test_HasDefaultValueForLocalLeader(self):
        self.assertEqual(_DEFAULTS['maplocalleader'], '\\')


class Test_is_key_name(ViewTest):
    def test_SucceedsIfNamePresent(self):
        self.assertTrue(is_key_name('<Leader>'))
        # test that it's case-insentitive
        self.assertTrue(is_key_name('<leader>'))

    def test_FailsIfNameAbsent(self):
        self.assertFalse(is_key_name('<Leaderx>'))


class Test_set_(ViewTest):
    def testCanSetValue(self):
        set_('dog', 'cat')
        self.assertEqual(variables._VARIABLES['dog'], 'cat')


class Test_get(ViewTest):
    def setUp(self):
        super().setUp()
        variables._VARIABLES = {}

    def testCanGetSetValue(self):
        set_('dog', 'cat')
        self.assertEqual(get('dog'), 'cat')
