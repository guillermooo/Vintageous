import unittest

from Vintageous.ex.parsers.new.parser import start_parsing
from Vintageous.ex.parsers.new.scanner import Scanner


class parse_line_ref_Tests(unittest.TestCase):
    def test_CanParseEmpty(self):
        parsed = start_parsing('')
        self.assertEqual(parsed.line_range, None)
        self.assertEqual(parsed.command, None)

    def test_CanParseDotAsStartLine(self):
        parsed = start_parsing('.')
        self.assertEqual(parsed.line_range.start_line, '.')
        self.assertEqual(parsed.line_range.end_line, None)

    def test_CanParseDotWithOffset(self):
        parsed = start_parsing('.+10')
        self.assertEqual(parsed.line_range.start_line, '.')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_CanParseLoneOffset(self):
        parsed = start_parsing('+10')
        self.assertEqual(parsed.line_range.start_line, None)
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_FailsIfDotAfterOffset(self):
        self.assertRaises(ValueError, start_parsing, '+10.')

    def test_CanParseMultipleOffsets(self):
        parsed = start_parsing('+10+10')
        self.assertEqual(parsed.line_range.start_line, None)
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [10, 10])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_CanParseSearchForward(self):
        parsed = start_parsing('/foo/')
        self.assertEqual(parsed.line_range.start_line, '/foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_SearchForwardClearsPreviousReferences(self):
        parsed = start_parsing('./foo/')
        self.assertEqual(parsed.line_range.start_line, '/foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_SearchForwardClearsPreviousReferencesWithOffsets(self):
        parsed = start_parsing('.+10/foo/')
        self.assertEqual(parsed.line_range.start_line, '/foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_CanParseSearchBackward(self):
        parsed = start_parsing('?foo?')
        self.assertEqual(parsed.line_range.start_line, '?foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_SearchBackwardClearsPreviousReferences(self):
        parsed = start_parsing('.?foo?')
        self.assertEqual(parsed.line_range.start_line, '?foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_SearchBackwardClearsPreviousReferencesWithOffsets(self):
        parsed = start_parsing('.+10?foo?')
        self.assertEqual(parsed.line_range.start_line, '?foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_CanParseSearchForwardWithOffset(self):
        parsed = start_parsing('/foo/+10')
        self.assertEqual(parsed.line_range.start_line, '/foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_CanParseSearchForwardWithOffsets(self):
        parsed = start_parsing('/foo/+10+10+10')
        self.assertEqual(parsed.line_range.start_line, '/foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [10, 10, 10])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_CanParseSearchBacwardWithOffset(self):
        parsed = start_parsing('?foo?+10')
        self.assertEqual(parsed.line_range.start_line, '?foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_CanParseSearchBacwardWithOffsets(self):
        parsed = start_parsing('?foo?+10+10+10')
        self.assertEqual(parsed.line_range.start_line, '?foo')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [10, 10, 10])
        self.assertEqual(parsed.line_range.end_offset, [])
        self.assertEqual(parsed.line_range.must_recompute_start_line, False)

    def test_CanParseDollarOnItsOwn(self):
        parsed = start_parsing('$')
        self.assertEqual(parsed.line_range.start_line, '$')

    def test_CanParseDollarWithCompany(self):
        parsed = start_parsing('0,$')
        self.assertEqual(parsed.line_range.start_line, '0')
        self.assertEqual(parsed.line_range.end_line, '$')

    def test_FailsIfDollarOffset(self):
        self.assertRaises(ValueError, start_parsing, '$+10')

    def test_FailsIfPrecededByAnything(self):
        self.assertRaises(ValueError, start_parsing, '.$')
        self.assertRaises(ValueError, start_parsing, '/foo/$')
        self.assertRaises(ValueError, start_parsing, '100$')

    def test_CanParseLoneComma(self):
        parsed = start_parsing(',')
        self.assertTrue(parsed.line_range.right_hand_side)

    def test_CanParseDotComma(self):
        parsed = start_parsing('.,')
        self.assertEqual(parsed.line_range.start_line, '.')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertTrue(parsed.line_range.right_hand_side)

    def test_CanParseCommaDot(self):
        parsed = start_parsing(',.')
        self.assertTrue(parsed.line_range.right_hand_side)
        self.assertEqual(parsed.line_range.start_line, None)
        self.assertEqual(parsed.line_range.end_line, '.')

    def test_CanParseLoneSmicolon(self):
        parsed = start_parsing(';')
        self.assertTrue(parsed.line_range.right_hand_side)
        self.assertTrue(parsed.line_range.must_recompute_start_line)

    def test_CanParseDotSmicolon(self):
        parsed = start_parsing('.;')
        self.assertEqual(parsed.line_range.start_line, '.')
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertTrue(parsed.line_range.right_hand_side)
        self.assertTrue(parsed.line_range.must_recompute_start_line)

    def test_CanParseSmicolonDot(self):
        parsed = start_parsing(';.')
        self.assertTrue(parsed.line_range.right_hand_side)
        self.assertEqual(parsed.line_range.start_line, None)
        self.assertEqual(parsed.line_range.end_line, '.')
        self.assertTrue(parsed.line_range.must_recompute_start_line)

    def test_CanParseCommaOffset(self):
        parsed = start_parsing(',+10')
        self.assertTrue(parsed.line_range.right_hand_side)
        self.assertEqual(parsed.line_range.start_line, None)
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.end_offset, [10])

    def test_CanParseSemicolonOffset(self):
        parsed = start_parsing(';+10')
        self.assertTrue(parsed.line_range.right_hand_side)
        self.assertEqual(parsed.line_range.start_line, None)
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.end_offset, [10])
        self.assertTrue(parsed.line_range.must_recompute_start_line)

    def test_CanParseOffsetCommaOffset(self):
        parsed = start_parsing('+10,+10')
        self.assertTrue(parsed.line_range.right_hand_side)
        self.assertEqual(parsed.line_range.start_line, None)
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [10])

    def test_CanParseSemicolonOffset(self):
        parsed = start_parsing('+10;+10')
        self.assertTrue(parsed.line_range.right_hand_side)
        self.assertEqual(parsed.line_range.start_line, None)
        self.assertEqual(parsed.line_range.end_line, None)
        self.assertEqual(parsed.line_range.start_offset, [10])
        self.assertEqual(parsed.line_range.end_offset, [10])
        self.assertTrue(parsed.line_range.must_recompute_start_line)

    def test_CanParseNumber(self):
        parsed = start_parsing('10')
        self.assertEqual(parsed.line_range.start_line, '10')

    def test_CanParseNumberRightHandSide(self):
        parsed = start_parsing(',10')
        self.assertEqual(parsed.line_range.start_line, None)
        self.assertEqual(parsed.line_range.end_line, '10')

    def test_FailsIfDotDigits(self):
        self.assertRaises(ValueError, start_parsing, '.10')


class parse_line_ref_TokenComma_Tests(unittest.TestCase):
    def test_CanParseLongSequence(self):
        # Vim allows this.
        parsed = start_parsing('1,2,3,4')
        self.assertEqual(parsed.line_range.start_line, '3')
        self.assertEqual(parsed.line_range.end_line, '4')


class parse_line_ref_ParseSubstituteCommand(unittest.TestCase):
    def test_CanParseItOnItsOwn(self):
        parsed = start_parsing('substitute')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseAlias(self):
        parsed = start_parsing('s')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSimpleRange(self):
        parsed = start_parsing('4s')
        self.assertEqual(parsed.line_range.start_line, '4')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithStartAndEndLines(self):
        parsed = start_parsing('4,5s')
        self.assertEqual(parsed.line_range.start_line, '4')
        self.assertEqual(parsed.line_range.end_line, '5')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchForward(self):
        parsed = start_parsing('/foo/s')
        self.assertEqual(parsed.line_range.start_line, '/foo')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchBackward(self):
        parsed = start_parsing('?foo?s')
        self.assertEqual(parsed.line_range.start_line, '?foo')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithSearchBackwardAndSearchForward(self):
        parsed = start_parsing('?foo?,/bar/s')
        self.assertEqual(parsed.line_range.start_line, '?foo')
        self.assertEqual(parsed.line_range.end_line, '/bar')
        self.assertEqual(parsed.command.content, 'substitute')

    def test_CanParseWithZeroAndDollar(self):
        parsed = start_parsing('0,$s')
        self.assertEqual(parsed.line_range.start_line, '0')
        self.assertEqual(parsed.line_range.end_line, '$')
        self.assertEqual(parsed.command.content, 'substitute')