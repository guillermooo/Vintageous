import unittest

from Vintageous.ex.parser.scanner import Scanner
from Vintageous.ex.parser.scanner_command_substitute import TokenCommandSubstitute
from Vintageous.ex.parser.scanner_command_write import TokenCommandWrite
from Vintageous.ex.parser.state import EOF
from Vintageous.ex.parser.tokens import TokenComma
from Vintageous.ex.parser.tokens import TokenDigits
from Vintageous.ex.parser.tokens import TokenDollar
from Vintageous.ex.parser.tokens import TokenDot
from Vintageous.ex.parser.tokens import TokenEof
from Vintageous.ex.parser.tokens import TokenMark
from Vintageous.ex.parser.tokens import TokenOffset
from Vintageous.ex.parser.tokens import TokenPercent
from Vintageous.ex.parser.tokens import TokenSearchBackward
from Vintageous.ex.parser.tokens import TokenSearchForward
from Vintageous.ex.parser.tokens import TokenSemicolon


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


class ScannerOffsets(unittest.TestCase):
    def testCanScanNegativeOffset(self):
        scanner = Scanner(".-100")
        tokens = list(scanner.scan())
        self.assertEqual([TokenDot(), TokenOffset([-100]), TokenEof()], tokens)


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

    def testCanScanSubstituteParamaterWithRange(self):
        scanner = Scanner(r'%substitute:foo:bar: 10')
        tokens = list(scanner.scan())
        params = {"search_term": "foo", "replacement": "bar", "flags": [], "count": 10}
        self.assertEqual([TokenPercent(), TokenCommandSubstitute(params), TokenEof()], tokens)


class ScannerMarksScanner_Tests(unittest.TestCase):
    def testCanInstantiate(self):
        scanner = Scanner("'a")
        tokens = list(scanner.scan())
        self.assertEqual([TokenMark('a'), TokenEof()], tokens)


class ScannerWriteCommand_Tests(unittest.TestCase):
    def testCanInstantiate(self):
        scanner = Scanner("write")
        tokens = list(scanner.scan())
        params = {'++': '', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanInstantiateAlias(self):
        scanner = Scanner("w")
        tokens = list(scanner.scan())
        params = {'++': '', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParsePlusPlusBin(self):
        scanner = Scanner("w ++bin")
        tokens = list(scanner.scan())
        params = {'++': 'binary', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

        scanner = Scanner("w ++binary")
        tokens = list(scanner.scan())
        params = {'++': 'binary', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParsePlusPlusNobin(self):
        scanner = Scanner("w ++nobinary")
        tokens = list(scanner.scan())
        params = {'++': 'nobinary', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

        scanner = Scanner("w ++nobin")
        tokens = list(scanner.scan())
        params = {'++': 'nobinary', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParsePlusPlusFileformat(self):
        scanner = Scanner("w ++fileformat")
        tokens = list(scanner.scan())
        params = {'++': 'fileformat', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

        scanner = Scanner("w ++ff")
        tokens = list(scanner.scan())
        params = {'++': 'fileformat', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParsePlusPlusFileencoding(self):
        scanner = Scanner("w ++fileencoding")
        tokens = list(scanner.scan())
        params = {'++': 'fileencoding', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

        scanner = Scanner("w ++enc")
        tokens = list(scanner.scan())
        params = {'++': 'fileencoding', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParsePlusPlusBad(self):
        scanner = Scanner("w ++bad")
        tokens = list(scanner.scan())
        params = {'++': 'bad', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

        scanner = Scanner("w ++fileformat")
        tokens = list(scanner.scan())
        params = {'++': 'fileformat', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParsePlusPlusEdit(self):
        scanner = Scanner("w ++edit")
        tokens = list(scanner.scan())
        params = {'++': 'edit', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

        scanner = Scanner("w ++fileformat")
        tokens = list(scanner.scan())
        params = {'++': 'fileformat', 'file_name': '', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParseRedirection(self):
        scanner = Scanner("w>>")
        tokens = list(scanner.scan())
        params = {'++': '', 'file_name': '', '>>': True, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParseRedirectionFollowedByFilename(self):
        scanner = Scanner("w>>foo.txt")
        tokens = list(scanner.scan())
        params = {'++': '', 'file_name': 'foo.txt', '>>': True, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParseRedirectionFollowedByFilenameSeparated(self):
        scanner = Scanner("w>> foo.txt")
        tokens = list(scanner.scan())
        params = {'++': '', 'file_name': 'foo.txt', '>>': True, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParseCommand(self):
        scanner = Scanner("w !dostuff")
        tokens = list(scanner.scan())
        params = {'++': '', 'file_name': '', '>>': False, 'cmd': 'dostuff'}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParseCommandAbsorbsEveryThing(self):
        scanner = Scanner("w !dostuff here")
        tokens = list(scanner.scan())
        params = {'++': '', 'file_name': '', '>>': False, 'cmd': 'dostuff here'}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)

    def testCanParseCommandAndDetectFileName(self):
        scanner = Scanner("w foo.txt")
        tokens = list(scanner.scan())
        params = {'++': '', 'file_name': 'foo.txt', '>>': False, 'cmd': ''}
        self.assertEqual([TokenCommandWrite(params), TokenEof()], tokens)
