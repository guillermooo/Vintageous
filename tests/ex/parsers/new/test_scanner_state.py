import unittest

from Vintageous.ex.parsers.new.state import State
from Vintageous.ex.parsers.new.state import EOF
from Vintageous.ex.parsers.new.tokens import TOKEN_UNKNOWN


class ScannerTests(unittest.TestCase):
    def testInstantiate(self):
        state = State("foo")

        self.assertEqual("foo", state.source)
        self.assertEqual(0, state.position)
        self.assertEqual(0, state.start)

    def testCanConsume(self):
        state = State("foo")
        c = state.consume()

        self.assertEqual('f', c)
        self.assertEqual(1, state.position)
        self.assertEqual(0, state.start)

    def testConsumingReachesEof(self):
        state = State("f")
        state.consume()
        eof = state.consume()

        self.assertEqual(EOF, eof)
        self.assertEqual(1, state.position)

    def testConsumingStopsAtEof(self):
        state = State("f")
        state.consume()
        a = state.consume()
        b = state.consume()
        c = state.consume()

        self.assertEqual([EOF, EOF, EOF], [a, b, c])
        self.assertEqual(1, state.position)
        self.assertEqual(0, state.start)

    def test_backup_Works(self):
        state = State("foo")
        state.consume()
        state.consume()
        state.backup()

    def test_skip_Works(self):
        state = State("aafoo")
        state.skip("a")

        self.assertEqual(2, state.position)
        self.assertEqual('f', state.consume())

    def test_skip_StopsAtEof(self):
        state = State("aa")
        state.skip("a")

        self.assertEqual(2, state.position)
        self.assertEqual(EOF, state.consume())

    def test_skip_run_Works(self):
        state = State("aafoo")
        state.skip_run("af")

        self.assertEqual(3, state.position)
        self.assertEqual('o', state.consume())

    def test_skip_run_StopsAtEof(self):
        state = State("aaf")
        state.skip_run("af")

        self.assertEqual(3, state.position)
        self.assertEqual(EOF, state.consume())

    def test_emit_Works(self):
        state = State("aabb")
        state.skip("a")

        self.assertEqual('aa', state.emit())
        self.assertEqual(2, state.position)

    def test_ignore_Works(self):
        state = State("aabb")
        state.skip("a")
        state.ignore()

        self.assertEqual(2, state.position)

    def test_expect_CanSucceed(self):
        state = State('foo')
        c = state.expect('f')
        self.assertEqual('f', c)

    def test_expect_CanFail(self):
        state = State('foo')
        self.assertRaises(ValueError, state.expect, 'x')

    def test_expect_match_CanSucceed(self):
        state = State('foo')
        c = state.expect_match('fo{2}')
        self.assertEqual('foo', c.group(0))

    def test_expect_match_CanFail(self):
        state = State('foo')
        self.assertRaises(ValueError, state.expect_match, 'x')

    def test_peek_CanSucceed(self):
        state = State('foo')
        self.assertTrue(state.peek('foo'))

    def test_peek_CanFail(self):
        state = State('foo')
        self.assertFalse(state.peek('fxo'))

    def test_match_CanSucceed(self):
        state = State('foo123')
        state.consume()
        state.consume()
        state.consume()
        self.assertTrue(state.match(r'\d{3}'))
        self.assertEqual(6, state.position)
        self.assertEqual(EOF, state.consume())

