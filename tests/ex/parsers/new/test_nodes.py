import unittest

from Vintageous.ex.parsers.new.nodes import RangeNode
from Vintageous.ex.parsers.new.nodes import CommandLineNode
from Vintageous.ex.parsers.new.tokens import TokenDot
from Vintageous.ex.parsers.new.tokens import TokenDigits
from Vintageous.ex.parsers.new.tokens_commands import TokenCommandSubstitute

from Vintageous.tests import ViewTest


class RangeNode_Tests(unittest.TestCase):
    def testCanInstantiate(self):
        node = RangeNode('foo', 'bar', ';')
        node.start_offset = [10]
        node.end_offset = [10]
        self.assertEqual(node.start, 'foo')
        self.assertEqual(node.end, 'bar')
        self.assertEqual(node.start_offset, [10])
        self.assertEqual(node.end_offset, [10])
        self.assertEqual(node.separator, ';')

    def test_CanDetectIfItsEmpty(self):
        node = RangeNode()
        self.assertTrue(node.is_empty)

    def test_CanDetectDoesNotHaveOffsets(self):
        node = RangeNode()
        self.assertFalse(node.has_offsets)

    def test_CanDetectHasOffsets(self):
        node = RangeNode(start_offset=[100])
        self.assertTrue(node.has_offsets)
        node = RangeNode(end_offset=[100])
        self.assertTrue(node.has_offsets)
        node = RangeNode(start_offset=[200], end_offset=[100])
        self.assertTrue(node.has_offsets)

class CommandLineNode_Tests(unittest.TestCase):
    def testCanInstantiate(self):
        range_node = RangeNode("foo", "bar", False)
        range_node.start_offset = [10]
        range_node.end_offset = [10]
        command = TokenCommandSubstitute({})
        node = CommandLineNode(range_node, command)
        self.assertEqual(range_node, node.line_range)
        self.assertEqual(command, node.command)


class RangeNode_resolve_notation_Tests(ViewTest):
    def testRetursCurrentLineIfRangeIsEmpty(self):
        self.write('''aaa aaa
bbb bbb
ccc ccc
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode().resolve(self.view)
        self.assert_equal_regions(self.R(0, 8), region)

    def testRetursCurrentLineIfRangeIsEmpty2(self):
        self.write('''aaa aaa
bbb bbb
ccc ccc
''')
        self.clear_sel()
        self.add_sel(self.R((1,0), (1,0)))
        region = RangeNode().resolve(self.view)
        self.assert_equal_regions(self.R(8, 16), region)

    def testRetursCurrentLineIfRangeIsEmptyAndAddsOffset(self):
        self.write('''aaa aaa
bbb bbb
ccc ccc
ddd ddd
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start_offset=[1, 1]).resolve(self.view)
        self.assert_equal_regions(self.R(16, 24), region)

    def testRetursCurrentLineIfRangeIsEmptyAndAddsOffsets(self):
        self.write('''aaa aaa
bbb bbb
ccc ccc
ddd ddd
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start_offset=[2]).resolve(self.view)
        self.assert_equal_regions(self.R(16, 24), region)

    def testRetursRequestedStartLineNumber(self):
        self.write('''aaa aaa
bbb bbb
ccc ccc
ddd ddd
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start=[TokenDigits('2')]).resolve(self.view)
        self.assert_equal_regions(self.R(8, 16), region)

    def testRetursRequestedStartLineNumberAndAddsOffset(self):
        self.write('''aaa aaa
bbb bbb
ccc ccc
ddd ddd
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start=[TokenDigits('2')], start_offset=[1]).resolve(self.view)
        self.assert_equal_regions(self.R(16, 24), region)

    def testRetursRequestedStartLineNumberAndAddsOffset(self):
        self.write('''aaa aaa
bbb bbb
ccc ccc
ddd ddd
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start=[TokenDigits('2')], start_offset=[2]).resolve(self.view)
        self.assert_equal_regions(self.R(24, 32), region)
