import unittest

import sublime

from Vintageous.state import State
from Vintageous.vi.utils import modes
from Vintageous.vi.mappings import Mappings
from Vintageous.vi.mappings import _mappings
from Vintageous.vi.mappings import mapping_status
from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import make_region
from Vintageous.tests import ViewTest
from Vintageous.vi.cmd_base import cmd_types


adding_tests = (
    (modes.NORMAL,               'G', 'G_', 'adding to normal mode'),
    (modes.VISUAL,               'G', 'G_', 'adding to visual mode'),
    (modes.OPERATOR_PENDING,     'G', 'G_', 'adding to operator pending mode'),
    (modes.VISUAL_LINE,          'G', 'G_', 'adding to visual line mode'),
    (modes.VISUAL_BLOCK,         'G', 'G_', 'adding to visual block mode'),
)


class Test_Mappings_AddingAndRemoving(ViewTest):
    def setUp(self):
        super().setUp()
        self.mappings = Mappings(self.state)
        self.mappings.clear()

    def testCanAdd(self):
        for (i, data) in enumerate(adding_tests):
            mode, keys, target, msg = data
            self.mappings.add(mode, keys, target)
            self.assertEqual(_mappings[mode][keys], {'name': target, 'type': cmd_types.USER}, '{0} [{1}] failed'.format(msg, i))
            self.mappings.clear()

    def testCanRemove(self):
        for (i, data) in enumerate(adding_tests):
            mode, keys, target, msg = data
            self.mappings.add(mode, keys, target)
            self.mappings.remove(mode, keys)

        self.assertFalse(_mappings[modes.NORMAL])
        self.assertFalse(_mappings[modes.VISUAL])
        self.assertFalse(_mappings[modes.VISUAL_LINE])
        self.assertFalse(_mappings[modes.VISUAL_BLOCK])


expanding_tests = (
    ((modes.NORMAL, 'G',     'G_'),     ('G',      'G',     'G_',   '',   'G',      mapping_status.COMPLETE)),
    ((modes.NORMAL, '<C-m>', 'daw'),    ('<C-m>',  '<C-m>', 'daw',  '',   '<C-m>',  mapping_status.COMPLETE)),
    ((modes.NORMAL, '<C-m>', 'daw'),    ('<C-m>x', '<C-m>', 'daw',  'x',  '<C-m>x', mapping_status.COMPLETE)),
    ((modes.NORMAL, 'xxA',   'daw'),    ('xx',     'xx',    '',     '',   'xx',     mapping_status.INCOMPLETE)),
)


class Test_Mapping_Expanding(ViewTest):
    def setUp(self):
        super().setUp()
        self.mappings = Mappings(self.state)
        self.mappings.clear()

    def testCanExpand(self):
        for (i, data) in enumerate(expanding_tests):
            setup_data, test_data = data

            mode, keys, new_mapping = setup_data
            self.mappings.add(mode, keys, new_mapping)

            self.state.mode = modes.NORMAL

            seq, expected_head, expected_mapping, expected_tail, expected_full, expected_status = test_data
            result = self.mappings.expand_first(seq)

            self.assertEqual(result.head, expected_head, '[{0}] head failed'.format(i))
            self.assertEqual(result.tail, expected_tail, '[{0}] tail failed'.format(i))
            self.assertEqual(result.mapping, expected_mapping, '[{0}] mapping failed'.format(i))
            self.assertEqual(result.sequence, expected_full, '[{0}] sequence failed'.format(i))
            self.assertEqual(result.status, expected_status, '[{0}] status failed'.format(i))

            self.mappings.clear()
