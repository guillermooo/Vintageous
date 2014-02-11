import unittest

import sublime

from Vintageous.state import state
from Vintageous.vi.utils import modes
from Vintageous.vi.mappings import Mappings
from Vintageous.vi.mappings import _mappings
from Vintageous.vi.mappings import mapping_status
from Vintageous.tests import set_text
from Vintageous.tests import add_sel
from Vintageous.tests import make_region
from Vintageous.tests import BufferTest
from Vintageous.vi.keys import parse_sequence


adding_tests = (
    (modes.NORMAL, 'G', 'G_'),
    (modes.VISUAL, 'G', 'G_'),
    (modes.OPERATOR_PENDING, 'G', 'G_'),
    (modes.VISUAL_LINE, 'G', 'G_'),
    (modes.VISUAL_BLOCK, 'G', 'G_'),
)


class Test_Mappings_AddingAndRemoving(BufferTest):
    def setUp(self):
        super().setUp()
        self.state = state.State(self.view)
        self.mappings = Mappings(self.state)
        self.mappings.clear()

    def testCanAdd(self):
        for (i, data) in enumerate(adding_tests):
            mode, keys, target = data
            self.mappings.add(mode, keys, target)
            self.assertEqual(_mappings[mode][keys], target, '[{0}] failed')
            self.mappings.clear()


expanding_tests = (
    ((modes.NORMAL, 'G',        'G_'),  ('G',           'G',        'G_',   '',   'G',          mapping_status.COMPLETE)),
    ((modes.NORMAL, '<ctrl+m>', 'daw'), ('<ctrl+m>',    '<ctrl+m>', 'daw',  '',   '<ctrl+m>',   mapping_status.COMPLETE)),
    ((modes.NORMAL, '<ctrl+m>', 'daw'), ('<ctrl+m>x',   '<ctrl+m>', 'daw',  'x',  '<ctrl+m>x',  mapping_status.COMPLETE)),
    ((modes.NORMAL, 'xxA',      'daw'), ('xx',          'xx',       '',     '',   'xx',         mapping_status.INCOMPLETE)),
)


class Test_Mapping_Expanding(BufferTest):
    def setUp(self):
        super().setUp()
        self.state = state.State(self.view)
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

            self.assertEqual(result.head, expected_head, '[{0}] failed'.format(i))
            self.assertEqual(result.tail, expected_tail, '[{0}] failed'.format(i))
            self.assertEqual(result.mapping, expected_mapping, '[{0}] failed'.format(i))
            self.assertEqual(result.sequence, expected_full, '[{0}] failed'.format(i))
            self.assertEqual(result.status, expected_status, '[{0}] failed'.format(i))

            self.mappings.clear()