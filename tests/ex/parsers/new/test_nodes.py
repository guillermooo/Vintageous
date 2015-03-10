import unittest

from Vintageous.ex.parsers.new.nodes import RangeNode
from Vintageous.ex.parsers.new.nodes import CommandNode
from Vintageous.ex.parsers.new.nodes import CommandLineNode
from Vintageous.ex.parsers.new.tokens_commands import TokenCommandSubstitute


class RangeNode_Tests(unittest.TestCase):
    def testCanInstantiate(self):
        node = RangeNode('foo', 'bar', False)
        node.start_offset = [10]
        node.end_offset = [10]
        self.assertEqual(node.start_line, 'foo')
        self.assertEqual(node.end_line, 'bar')
        self.assertEqual(node.must_recompute_start_line, False)
        self.assertEqual(node.start_offset, [10])
        self.assertEqual(node.end_offset, [10])


class CommandNode_Tests(unittest.TestCase):
    def testCanInstantiate(self):
        command = TokenCommandSubstitute({'hello': 'world', 'flags': ['r']})
        node = CommandNode(command)
        self.assertEqual('substitute', node.name)
        self.assertEqual({'hello': 'world', 'flags': ['r']}, node.arguments)
        self.assertEqual(['r'], node.flags)
        self.assertEqual(1, node.count)


class CommandLineNode_Tests(unittest.TestCase):
    def testCanInstantiate(self):
        range_node = RangeNode("foo", "bar", False)
        range_node.start_offset = [10]
        range_node.end_offset = [10]
        command = TokenCommandSubstitute({})
        node = CommandLineNode(range_node, command)
        self.assertEqual(range_node, node.line_range)
        self.assertEqual(command, node.command)

