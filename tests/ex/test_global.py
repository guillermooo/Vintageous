import unittest

from Vintageous.ex.parsers.g_cmd import GlobalLexer


class TestGlobalLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = GlobalLexer()

    def testCanMatchFullPattern(self):
        actual = self.lexer.parse(r'/foo/p#')
        self.assertEqual(actual, ['foo', 'p#'])

    def testCanMatchEmtpySearch(self):
        actual = self.lexer.parse(r'//p#')
        self.assertEqual(actual, ['', 'p#'])

    def testCanEscapeCharactersInSearchPattern(self):
        actual = self.lexer.parse(r'/\/foo\//p#')
        self.assertEqual(actual, ['/foo/', 'p#'])

    def testCanEscapeBackSlashes(self):
        actual = self.lexer.parse(r'/\\/p#')
        self.assertEqual(actual, ['\\', 'p#'])


if __name__ == '__main__':
    unittest.main()
