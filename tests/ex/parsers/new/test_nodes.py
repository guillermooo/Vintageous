import unittest

from Vintageous.ex.parsers.new.nodes import RangeNode
from Vintageous.ex.parsers.new.nodes import CommandLineNode
from Vintageous.ex.parsers.new.tokens_commands import TokenCommandSubstitute


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


class CommandLineNode_Tests(unittest.TestCase):
    def testCanInstantiate(self):
        range_node = RangeNode("foo", "bar", False)
        range_node.start_offset = [10]
        range_node.end_offset = [10]
        command = TokenCommandSubstitute({})
        node = CommandLineNode(range_node, command)
        self.assertEqual(range_node, node.line_range)
        self.assertEqual(command, node.command)

