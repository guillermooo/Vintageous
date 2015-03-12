import unittest

from Vintageous.ex.parsers.new.scanner import Scanner
from Vintageous.ex.parsers.new.state import EOF
from Vintageous.ex.parsers.new.tokens import TokenEof
from Vintageous.ex.parsers.new.tokens import TokenDot
from Vintageous.ex.parsers.new.tokens import TokenDollar
from Vintageous.ex.parsers.new.tokens import TokenComma
from Vintageous.ex.parsers.new.tokens import TokenDigits
from Vintageous.ex.parsers.new.tokens import TokenSemicolon
from Vintageous.ex.parsers.new.tokens import TokenOffset
from Vintageous.ex.parsers.new.tokens import TokenPercent
from Vintageous.ex.parsers.new.tokens import TokenSearchForward
from Vintageous.ex.parsers.new.tokens import TokenSearchBackward
from Vintageous.ex.parsers.new.tokens import TokenMark
from Vintageous.ex.parsers.new.tokens_commands import TokenCommandSubstitute


class ScannerTests(unittest.TestCase):
    def testCanInstantiate(self):
        scanner = Scanner("foo")
        self.assertEqual(scanner.state.source, 'foo')

    def testCanScanDot(self):
        scanner = Scanner(".")
        tokens = list(scanner.scan())
        self.assertEqual([TokenDot(), TokenEof()], tokens)

    def testCanScanDollar(self):
        scanner = Scanner("$")
        tokens = list(scanner.scan())
        self.assertEqual([TokenDollar(), TokenEof()], tokens)

    def testCanScanDollar(self):
        scanner = Scanner(",")
        tokens = list(scanner.scan())
        self.assertEqual([TokenComma(), TokenEof()], tokens)

    def testCanScanDollar(self):
        scanner = Scanner(";")
        tokens = list(scanner.scan())
        self.assertEqual([TokenSemicolon(), TokenEof()], tokens)

    def testCanScanForwardSearch(self):
        scanner = Scanner("/foo/")
        tokens = list(scanner.scan())
        self.assertEqual([TokenSearchForward('foo'), TokenEof()], tokens)

    def testCanScanBackwardSearch(self):
        scanner = Scanner("?foo?")
        tokens = list(scanner.scan())
        self.assertEqual([TokenSearchBackward('foo'), TokenEof()], tokens)

    def testCanScanOffset(self):
        scanner = Scanner("+100")
        tokens = list(scanner.scan())
        self.assertEqual([TokenOffset([100]), TokenEof()], tokens)

    def testCanScanOffsetWithTrailingChars(self):
        scanner = Scanner("+100,")
        tokens = list(scanner.scan())
        self.assertEqual([TokenOffset([100]), TokenComma(), TokenEof()], tokens)

    def testCanScanPercent(self):
        scanner = Scanner("%")
        tokens = list(scanner.scan())
        self.assertEqual([TokenPercent(), TokenEof()], tokens)

    def testCanScanEmptyRange(self):
        scanner = Scanner("s")
        tokens = list(scanner.scan())
        self.assertEqual([TokenCommandSubstitute(None), TokenEof()], tokens)
        self.assertEqual(1, scanner.state.position)

    def testCanScanDotOffsetSearchForward(self):
        scanner = Scanner(".+10/foobar/")
        tokens = list(scanner.scan())
        self.assertEqual([TokenDot(), TokenOffset([10]), TokenSearchForward('foobar'), TokenEof()], tokens)
        self.assertEqual(12, scanner.state.position)


class ScannerDigits(unittest.TestCase):
    def testCanScanDigits(self):
        scanner = Scanner("100")
        tokens = list(scanner.scan())
        self.assertEqual([TokenDigits('100'), TokenEof()], tokens)

    def testCanScanDigitsDot(self):
        scanner = Scanner("100.")
        tokens = list(scanner.scan())
        self.assertEqual([TokenDigits('100'), TokenDot(), TokenEof()], tokens)


class ScannerCommandNameTests(unittest.TestCase):
    def testCanInstantiate(self):
        scanner = Scanner("substitute")
        tokens = list(scanner.scan())
        self.assertEqual([TokenCommandSubstitute(params=None), TokenEof()], tokens)

    def testCanScanSubstituteParamaters(self):
        scanner = Scanner("substitute:foo:bar:")
        tokens = list(scanner.scan())
        params = {"search_term": "foo", "replacement": "bar", "flags": [], "count": 1}
        self.assertEqual([TokenCommandSubstitute(params), TokenEof()], tokens)

    def testCanScanSubstituteParamatersWithFlags(self):
        scanner = Scanner("substitute:foo:bar:r")
        tokens = list(scanner.scan())
        params = {"search_term": "foo", "replacement": "bar", "flags": ['r'], "count": 1}
        self.assertEqual([TokenCommandSubstitute(params), TokenEof()], tokens)

    def testScanCanFailIfSubstituteParamatersFlagsHaveWrongOrder(self):
        scanner = Scanner("substitute:foo:bar:r&")
        self.assertRaises(ValueError, lambda: list(scanner.scan()))

    def testCanScanSubstituteParamatersWithCount(self):
        scanner = Scanner("substitute:foo:bar: 10")
        tokens = list(scanner.scan())
        params = {"search_term": "foo", "replacement": "bar", "flags": [], "count": 10}
        self.assertEqual([TokenCommandSubstitute(params), TokenEof()], tokens)


class ScannerMarksScanner_Tests(unittest.TestCase):
    def testCanInstantiate(self):
        scanner = Scanner("'a")
        tokens = list(scanner.scan())
        self.assertEqual([TokenMark('a'), TokenEof()], tokens)
