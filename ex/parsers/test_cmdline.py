import unittest
from Vintageous.ex.parsers import cmd_line


class ParserBase(unittest.TestCase):
    def setUp(self):
        self.parser = cmd_line.ParserBase("foo")

    def testIsInitCorrect(self):
        self.assertEqual(self.parser.source, "foo")
        self.assertEqual(self.parser.c, "f")

    def testCanConsume(self):
        rv = []
        while self.parser.c != cmd_line.EOF:
            rv.append(self.parser.c)
            self.parser.consume()
        self.assertEqual(rv, list("foo"))

    def testCanConsumeEmpty(self):
        parser = cmd_line.ParserBase('')
        self.assertEqual(parser.c, cmd_line.EOF)


class VimParser(unittest.TestCase):
    def testCanParseEmptyInput(self):
        parser = cmd_line.VimParser('')
        rv = parser.parse_range()
        self.assertEqual(rv, cmd_line.default_range_info)

    def testCanMatchMinusSignOffset(self):
        parser = cmd_line.VimParser('-')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_offset'] = -1
        expected['text_range'] = '-'
        self.assertEqual(rv, expected)

    def testCanMatchPlusSignOffset(self):
        parser = cmd_line.VimParser('+')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_offset'] = 1
        expected['text_range'] = '+'
        self.assertEqual(rv, expected)

    def testCanMatchMultiplePlusSignsOffset(self):
        parser = cmd_line.VimParser('++')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 2
        expected['text_range'] = '++'
        self.assertEqual(rv, expected)

    def testCanMatchMultipleMinusSignsOffset(self):
        parser = cmd_line.VimParser('--')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = -2
        expected['text_range'] = '--'
        self.assertEqual(rv, expected)

    def testCanMatchPositiveIntegerOffset(self):
        parser = cmd_line.VimParser('+100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 100
        expected['text_range'] = "+100"
        self.assertEqual(rv, expected)

    def testCanMatchMultipleSignsAndPositiveIntegetOffset(self):
        parser = cmd_line.VimParser('++99')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 100
        expected['text_range'] = '++99'
        self.assertEqual(rv, expected)

    def testCanMatchMultipleSignsAndNegativeIntegerOffset(self):
        parser = cmd_line.VimParser('--99')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = -100
        expected['text_range'] = '--99'
        self.assertEqual(rv, expected)

    def testCanMatchPlusSignBeforeNegativeInteger(self):
        parser = cmd_line.VimParser('+-101')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = -100
        expected['text_range'] = '+-101'
        self.assertEqual(rv, expected)

    def testCanMatchPostFixMinusSign(self):
        parser = cmd_line.VimParser('101-')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_offset'] = 100
        expected['text_range'] = '101-'
        self.assertEqual(rv, expected)

    def testCanMatchPostfixPlusSign(self):
        parser = cmd_line.VimParser('99+')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_offset'] = 100
        expected['text_range'] = '99+'
        self.assertEqual(rv, expected)

    def testCanMatchCurrentLineSymbol(self):
        parser = cmd_line.VimParser('.')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['text_range'] = '.'
        self.assertEqual(rv, expected)

    def testCanMatchLastLineSymbol(self):
        parser = cmd_line.VimParser('$')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['text_range'] = '$'
        self.assertEqual(rv, expected)

    def testCanMatchWholeBufferSymbol(self):
        parser = cmd_line.VimParser('%')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '%'
        expected['text_range'] = '%'
        self.assertEqual(rv, expected)

    def testCanMatchMarkRef(self):
        parser = cmd_line.VimParser("'a")
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = "'a"
        expected['text_range'] = "'a"
        self.assertEqual(rv, expected)

    def testCanMatchUppsercaseMarkRef(self):
        parser = cmd_line.VimParser("'A")
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = "'A"
        expected['text_range'] = "'A"
        self.assertEqual(rv, expected)

    def testMarkRefsMustBeAlpha(self):
        parser = cmd_line.VimParser("'0")
        self.assertRaises(SyntaxError, parser.parse_range)

    def testWholeBufferSymbolCannotHavePostfixOffsets(self):
        parser = cmd_line.VimParser('%100')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testWholeBufferSymbolCannotHavePrefixOffsets(self):
        parser = cmd_line.VimParser('100%')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testCurrentLineSymbolCannotHavePrefixOffsets(self):
        parser = cmd_line.VimParser('100.')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testLastLineSymbolCannotHavePrefixOffsets(self):
        parser = cmd_line.VimParser('100$')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testLastLineSymbolCanHavePostfixNoSignIntegerOffsets(self):
        parser = cmd_line.VimParser('$100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_offset'] = 100
        expected['text_range'] = '$100'
        self.assertEqual(rv, expected)

    def testLastLineSymbolCanHavePostfixSignedIntegerOffsets(self):
        parser = cmd_line.VimParser('$+100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_offset'] = 100
        expected['text_range'] = '$+100'
        self.assertEqual(rv, expected)

    def testLastLineSymbolCanHavePostfixSignOffsets(self):
        parser = cmd_line.VimParser('$+')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_offset'] = 1
        expected['text_range'] = '$+'
        self.assertEqual(rv, expected)

    def testCurrentLineSymbolCanHavePostfixNoSignIntegerOffsets(self):
        parser = cmd_line.VimParser('.100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 100
        expected['text_range'] = '.100'
        self.assertEqual(rv, expected)

    def testCurrentLineSymbolCanHavePostfixSignedIntegerOffsets(self):
        parser = cmd_line.VimParser('.+100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 100
        expected['text_range'] = '.+100'
        self.assertEqual(rv, expected)

    def testCurrentLineSymbolCanHavePostfixSignOffsets(self):
        parser = cmd_line.VimParser('.+')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 1
        expected['text_range'] = '.+'
        self.assertEqual(rv, expected)

    def testCanMatchSearchBasedOffsets(self):
        parser = cmd_line.VimParser('/foo/')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', 0]]
        expected['text_range'] = '/foo/'
        self.assertEqual(rv, expected)

    def testCanMatchReverseSearchBasedOffsets(self):
        parser = cmd_line.VimParser('?foo?')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['?', 'foo', 0]]
        expected['text_range'] = '?foo?'
        self.assertEqual(rv, expected)

    def testCanMatchReverseSearchBasedOffsetsWithPostfixOffset(self):
        parser = cmd_line.VimParser('?foo?100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['?', 'foo', 100]]
        expected['text_range'] = '?foo?100'
        self.assertEqual(rv, expected)

    def testCanMatchReverseSearchBasedOffsetsWithSignedIntegerOffset(self):
        parser = cmd_line.VimParser('?foo?-100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['?', 'foo', -100]]
        expected['text_range'] = '?foo?-100'
        self.assertEqual(rv, expected)

    def testCanMatchSearchBasedOffsetsWithPostfixOffset(self):
        parser = cmd_line.VimParser('/foo/100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', 100]]
        expected['text_range'] = '/foo/100'
        self.assertEqual(rv, expected)

    def testCanMatchSearchBasedOffsetsWithSignedIntegerOffset(self):
        parser = cmd_line.VimParser('/foo/-100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', -100]]
        expected['text_range'] = '/foo/-100'
        self.assertEqual(rv, expected)

    def testSearchBasedOffsetsCanEscapeForwardSlash(self):
        parser = cmd_line.VimParser('/foo\/-100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo/-100', 0]]
        expected['text_range'] = '/foo\/-100'
        self.assertEqual(rv, expected)

    def testSearchBasedOffsetsCanEscapeQuestionMark(self):
        parser = cmd_line.VimParser('?foo\?-100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['?', 'foo?-100', 0]]
        expected['text_range'] = '?foo\?-100'
        self.assertEqual(rv, expected)

    def testSearchBasedOffsetsCanEscapeBackSlash(self):
        parser = cmd_line.VimParser('/foo\\\\?-100')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo\\?-100', 0]]
        expected['text_range'] = '/foo\\\\?-100'
        self.assertEqual(rv, expected)

    def testSearchBasedOffsetsEscapeAnyUnknownEscapeSequence(self):
        parser = cmd_line.VimParser('/foo\\h')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'fooh', 0]]
        expected['text_range'] = '/foo\\h'
        self.assertEqual(rv, expected)

    def testCanHaveMultipleSearchBasedOffsets(self):
        parser = cmd_line.VimParser('/foo//bar/?baz?')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', 0],
                                           ['/', 'bar', 0],
                                           ['?', 'baz', 0],
                                          ]
        expected['text_range'] = '/foo//bar/?baz?'
        self.assertEqual(rv, expected)

    def testCanHaveMultipleSearchBasedOffsetsWithInterspersedNumericOffets(self):
        parser = cmd_line.VimParser('/foo/100/bar/+100--+++?baz?')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', 100],
                                           ['/', 'bar', 101],
                                           ['?', 'baz', 0],
                                          ]
        expected['text_range'] = '/foo/100/bar/+100--+++?baz?'
        self.assertEqual(rv, expected)

    def testWholeBufferSymbolCannotHavePostfixSearchBasedOffsets(self):
        parser = cmd_line.VimParser('%/foo/')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testCurrentLineSymbolCannotHavePrefixSearchBasedOffsets(self):
        parser = cmd_line.VimParser('/foo/.')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testLastLineSymbolCannotHavePrefixSearchBasedOffsets(self):
        parser = cmd_line.VimParser('/foo/$')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testWholeBufferSymbolCannotHavePrefixSearchBasedOffsets(self):
        parser = cmd_line.VimParser('/foo/%')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testCurrentLineSymbolCanHavePostfixSearchBasedOffsets(self):
        parser = cmd_line.VimParser('./foo/+10')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_search_offsets'] = [['/', 'foo', 10]]
        expected['text_range'] = './foo/+10'
        self.assertEqual(rv, expected)

    def testLastLineSymbolCanHavePostfixSearchBasedOffsets(self):
        parser = cmd_line.VimParser('$?foo?+10')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_search_offsets'] = [['?', 'foo', 10]]
        expected['text_range'] = '$?foo?+10'
        self.assertEqual(rv, expected)

    def testLastLineSymbolCanHaveMultiplePostfixSearchBasedOffsets(self):
        parser = cmd_line.VimParser('$?foo?+10/bar/100/baz/')
        rv = parser.parse_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_search_offsets'] = [['?', 'foo', 10],
                                           ['/', 'bar', 100],
                                           ['/', 'baz', 0],
                                          ]
        expected['text_range'] = '$?foo?+10/bar/100/baz/'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegers(self):
        parser = cmd_line.VimParser('100,100')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_offset'] = 100
        expected['separator'] = ','
        expected['right_offset'] = 100
        expected['text_range'] = '100,100'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersWithOffsets(self):
        parser = cmd_line.VimParser('+100++--+;++100-')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 101
        expected['separator'] = ';'
        expected['right_ref'] = '.'
        expected['right_offset'] = 100
        expected['text_range'] = '+100++--+;++100-'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_1(self):
        parser = cmd_line.VimParser('%,%')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '%'
        expected['separator'] = ','
        expected['right_ref'] = '%'
        expected['text_range'] = '%,%'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_2(self):
        parser = cmd_line.VimParser('.,%')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['separator'] = ','
        expected['right_ref'] = '%'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_2(self):
        parser = cmd_line.VimParser('%,.')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '%'
        expected['separator'] = ','
        expected['right_ref'] = '.'
        expected['text_range'] = '%,.'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_3(self):
        parser = cmd_line.VimParser('$,%')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['separator'] = ','
        expected['right_ref'] = '%'
        expected['text_range'] = '$,%'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_4(self):
        parser = cmd_line.VimParser('%,$')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '%'
        expected['separator'] = ','
        expected['right_ref'] = '$'
        expected['text_range'] = '%,$'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_5(self):
        parser = cmd_line.VimParser('$,.')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['separator'] = ','
        expected['right_ref'] = '.'
        expected['text_range'] = '$,.'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_6(self):
        parser = cmd_line.VimParser('.,$')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['separator'] = ','
        expected['right_ref'] = '$'
        expected['text_range'] = '.,$'
        self.assertEqual(rv, expected)

    def testFullRangeCanMatchCommandOnly(self):
        parser = cmd_line.VimParser('foo')
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        self.assertEqual(rv, expected)

    def testInFullRangeLineSymbolsCannotHavePrefixOffsets_1(self):
        parser = cmd_line.VimParser('100.,%')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testInFullRangeLineSymbolsCannotHavePrefixOffsets_2(self):
        parser = cmd_line.VimParser('%,100$')
        self.assertRaises(SyntaxError, parser.parse_full_range)

    def testInFullRangeLineSymbolsCannotHavePrefixOffsets_3(self):
        parser = cmd_line.VimParser('%,100.')
        self.assertRaises(SyntaxError, parser.parse_full_range)

    def testInFullRangeLineSymbolsCannotHavePrefixOffsets_4(self):
        parser = cmd_line.VimParser('100%,.')
        self.assertRaises(SyntaxError, parser.parse_full_range)

    def testComplexFullRange(self):
        parser = cmd_line.VimParser(".++9/foo\\bar/100?baz?--;'b-100?buzz\\\\\\??+10")
        rv = parser.parse_full_range()
        expected = cmd_line.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 10
        expected['left_search_offsets'] = [['/', 'foobar', 100], ['?', 'baz', -2]]
        expected['separator'] = ';'
        expected['right_ref'] = "'b"
        expected['right_offset'] = -100
        expected['right_search_offsets'] = [['?', 'buzz\\?', 10]]
        expected['text_range'] = ".++9/foo\\bar/100?baz?--;'b-100?buzz\\\\\\??+10"
        self.assertEqual(rv, expected)

    def testFullRangeMustEndInAlpha(self):
        parser = cmd_line.VimParser('100%,.(')
        self.assertRaises(SyntaxError, parser.parse_full_range)


class TestCaseCommandLineParser(unittest.TestCase):
    def testCanParseCommandOnly(self):
        parser = cmd_line.CommandLineParser('foo')
        rv = parser.parse_cmd_line()
        expected_range = cmd_line.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"foo", "args":"", "forced": False}],
                errors=[]
            )
        self.assertEqual(rv, expected)

    def testCanParseWithErrors(self):
        parser = cmd_line.CommandLineParser('10$foo')
        rv = parser.parse_cmd_line()
        expected = dict(
                range=None,
                commands=[],
                errors=['E492 Not an editor command.']
            )
        self.assertEqual(rv, expected)

    def testCanParseCommandWithArgs(self):
        parser = cmd_line.CommandLineParser('foo! bar 100')
        rv = parser.parse_cmd_line()
        expected_range = cmd_line.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"foo", "args":"bar 100", "forced": True}],
                errors=[]
            )
        self.assertEqual(rv, expected)

    def testCanParseCommandWithArgsAndRange(self):
        parser = cmd_line.CommandLineParser('100foo! bar 100')
        rv = parser.parse_cmd_line()
        expected_range = cmd_line.default_range_info.copy()
        expected_range['left_offset'] = 100
        expected_range['text_range'] = '100'
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"foo", "args":"bar 100", "forced": True}],
                errors=[],
            )
        self.assertEqual(rv, expected)

    def testCanParseDoubleAmpersandCommand(self):
        parser = cmd_line.CommandLineParser('&&')
        rv = parser.parse_cmd_line()
        expected_range = cmd_line.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"&&", "args":"", "forced": False}],
                errors=[],
            )
        self.assertEqual(rv, expected)

    def testCanParseAmpersandCommand(self):
        parser = cmd_line.CommandLineParser('&')
        rv = parser.parse_cmd_line()
        expected_range = cmd_line.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"&", "args":"", "forced": False}],
                errors=[],
            )
        self.assertEqual(rv, expected)

    def testCanParseBangCommand(self):
        parser = cmd_line.CommandLineParser('!')
        rv = parser.parse_cmd_line()
        expected_range = cmd_line.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"!", "args":"", "forced": False}],
                errors=[],
            )
        self.assertEqual(rv, expected)

    def testCanParseBangCommandWithRange(self):
        parser = cmd_line.CommandLineParser('.!')
        rv = parser.parse_cmd_line()
        expected_range = cmd_line.default_range_info.copy()
        expected_range['text_range'] = '.'
        expected_range['left_ref'] = '.'
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"!", "args":"", "forced": False}],
                errors=[],
            )
        self.assertEqual(rv, expected)


class TestAddressParser(unittest.TestCase):
    def testCanParseSymbolAddress_1(self):
        parser = cmd_line.AddressParser('.')
        rv = parser.parse()
        expected = {'ref': '.', 'search_offsets': [], 'offset': None}
        self.assertEqual(rv, expected)

    def testCanParseSymbolAddress_2(self):
        parser = cmd_line.AddressParser('$')
        rv = parser.parse()
        expected = {'ref': '$', 'search_offsets': [], 'offset': None}
        self.assertEqual(rv, expected)

    def testCanParseOffsetOnItsOwn(self):
        parser = cmd_line.AddressParser('100')
        rv = parser.parse()
        expected = {'ref': None, 'search_offsets': [], 'offset': 100}
        self.assertEqual(rv, expected)

    def testCanParseSignsOnTheirOwn(self):
        parser = cmd_line.AddressParser('++')
        rv = parser.parse()
        expected = {'ref': '.', 'search_offsets': [], 'offset': 2}
        self.assertEqual(rv, expected)

    def testCanParseSignAndNumber(self):
        parser = cmd_line.AddressParser('+1')
        rv = parser.parse()
        expected = {'ref': '.', 'search_offsets': [], 'offset': 1}
        self.assertEqual(rv, expected)

    def testCanParseSymbolAndOffset(self):
        parser = cmd_line.AddressParser('.+1')
        rv = parser.parse()
        expected = {'ref': '.', 'search_offsets': [], 'offset': 1}
        self.assertEqual(rv, expected)

    def testCanParseSearchOffset(self):
        parser = cmd_line.AddressParser('/foo bar')
        rv = parser.parse()
        expected = {'ref': None, 'search_offsets': [['/', 'foo bar', 0]], 'offset': None}
        self.assertEqual(rv, expected)

if __name__ == '__main__':
    unittest.main()
