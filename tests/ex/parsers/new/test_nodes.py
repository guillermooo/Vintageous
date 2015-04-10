import unittest

from Vintageous.ex.parser.nodes import RangeNode
from Vintageous.ex.parser.nodes import CommandLineNode
from Vintageous.ex.parser.tokens import TokenDot
from Vintageous.ex.parser.tokens import TokenDigits
from Vintageous.ex.parser.tokens import TokenSearchForward
from Vintageous.ex.parser.tokens import TokenSearchBackward
from Vintageous.ex.parser.tokens import TokenPercent
from Vintageous.ex.parser.tokens import TokenOffset
from Vintageous.ex.parser.tokens import TokenMark
from Vintageous.ex.parser.scanner_command_substitute import TokenCommandSubstitute

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
        region = RangeNode(start=[TokenOffset([1, 1])]).resolve(self.view)
        self.assert_equal_regions(self.R(16, 24), region)

    def testRetursCurrentLineIfRangeIsEmptyAndAddsOffsets(self):
        self.write('''aaa aaa
bbb bbb
ccc ccc
ddd ddd
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start=[TokenOffset([2])]).resolve(self.view)
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
        region = RangeNode(start=[TokenDigits('2'), TokenOffset([2])]).resolve(self.view)
        self.assert_equal_regions(self.R(24, 32), region)

    def testRetursWholeBufferIfPercentRequested(self):
        self.write('''aaa aaa
bbb bbb
ccc ccc
ddd ddd
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start=[TokenPercent()]).resolve(self.view)
        self.assert_equal_regions(self.R(0, 32), region)


class Tests_SearchForward(ViewTest):

    def testCanSearchForward(self):
        self.write('''aaa aaa
bbb bbb
ccc cat
ddd cat
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start=[TokenSearchForward('cat')]).resolve(self.view)
        self.assert_equal_regions(self.R(16, 24), region)

    def testCanSearchForwardWithOffset(self):
        self.write('''aaa aaa
bbb bbb
ccc cat
ddd ddd
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start=[TokenSearchForward('cat'), TokenOffset([1])]).resolve(self.view)
        self.assert_equal_regions(self.R(24, 32), region)

    def testFailedSearchThrows(self):
        self.write('''aaa aaa
bbb bbb
ccc cat
ddd cat
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        line_range = RangeNode(start=[TokenSearchForward('dog')])
        self.assertRaises(ValueError, line_range.resolve, self.view)

    def testCanSearchMultipleTimesForward(self):
        self.write('''aaa aaa
bbb bbb
ccc cat
ddd ddd
eee eee
fff cat
''')
        self.clear_sel()
        self.add_sel(self.R((0,0), (0,0)))
        region = RangeNode(start=[TokenSearchForward('cat'), TokenSearchForward('cat')]).resolve(self.view)
        self.assert_equal_regions(self.R(40, 48), region)


class Tests_SearchBackward(ViewTest):

    def testCanSearchBackward(self):
        self.write('''aaa aaa
bbb bbb
ccc cat
ddd ddd
xxx xxx
''')
        self.clear_sel()
        self.add_sel(self.R(self.view.size()))
        region = RangeNode(start=[TokenSearchBackward('cat')]).resolve(self.view)
        self.assert_equal_regions(self.R(16, 24), region)

    def testCanSearchBackwardWithOffset(self):
        self.write('''aaa aaa
bbb bbb
ccc cat
ddd ddd
xxx xxx
''')
        self.clear_sel()
        self.add_sel(self.R(self.view.size()))
        region = RangeNode(start=[TokenSearchBackward('cat'), TokenOffset([1])]).resolve(self.view)
        self.assert_equal_regions(self.R(24, 32), region)

    def testFailedSearchThrows(self):
        self.write('''aaa aaa
bbb bbb
ccc cat
ddd cat
''')
        self.clear_sel()
        self.add_sel(self.R(self.view.size()))
        line_range = RangeNode(start=[TokenSearchBackward('dog')])
        self.assertRaises(ValueError, line_range.resolve, self.view)

    def testCanSearchMultipleTimesBackward(self):
        self.write('''aaa aaa
bbb bbb
ccc cat
ddd cat
eee eee
fff fff
''')
        self.clear_sel()
        self.add_sel(self.R(self.view.size()))
        region = RangeNode(start=[TokenSearchBackward('cat'), TokenSearchBackward('cat')]).resolve(self.view)
        self.assert_equal_regions(self.R(16, 24), region)


class Tests_Line0(ViewTest):
    def testCanCalculateVisualStart(self):
        self.write('''xxx xxx
aaa aaa
xxx xxx
bbb bbb
''')
        self.clear_sel()
        self.add_sel(self.R(8, 10))
        region = RangeNode(start=[TokenDigits('0')]).resolve(self.view)
        self.assert_equal_regions(self.R(-1, -1), region)


class Tests_Marks(ViewTest):
    def testCanCalculateVisualStart(self):
        self.write('''xxx xxx
aaa aaa
xxx xxx
bbb bbb
''')
        self.clear_sel()
        self.add_sel(self.R(8, 10))
        region = RangeNode(start=[TokenMark("<")]).resolve(self.view)
        self.assert_equal_regions(self.R(8, 16), region)

    def testCanCalculateVisualStartWithMultipleSels(self):
        self.write('''xxx xxx
aaa aaa
xxx xxx
bbb bbb
xxx xxx
ccc ccc
''')
        self.clear_sel()
        self.add_sel(self.R(8, 10))
        self.add_sel(self.R(24, 27))
        region = RangeNode(start=[TokenMark("<")]).resolve(self.view)
        self.assert_equal_regions(self.R(8, 16), region)

    def testCanCalculateVisualEnd(self):
        self.write('''xxx xxx
aaa aaa
xxx xxx
bbb bbb
''')
        self.clear_sel()
        self.add_sel(self.R(8, 10))
        region = RangeNode(start=[TokenMark(">")]).resolve(self.view)
        self.assert_equal_regions(self.R(8, 16), region)

    def testCanCalculateVisualEndWithMultipleSels(self):
        self.write('''xxx xxx
aaa aaa
xxx xxx
bbb bbb
xxx xxx
ccc ccc
''')
        self.clear_sel()
        self.add_sel(self.R(8, 10))
        self.add_sel(self.R(24, 27))
        region = RangeNode(start=[TokenMark(">")]).resolve(self.view)
        self.assert_equal_regions(self.R(8, 16), region)

    def testCanCalculateVisualEndWithMultipleSels(self):
        self.write('''xxx xxx
aaa aaa
xxx xxx
bbb bbb
xxx xxx
ccc ccc
''')
        self.clear_sel()
        self.add_sel(self.R(8, 10))
        region = RangeNode(start=[TokenMark("<"), TokenMark(">")]).resolve(self.view)
        self.assert_equal_regions(self.R(8, 16), region)
