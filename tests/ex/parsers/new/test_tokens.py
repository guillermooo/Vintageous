import unittest

from Vintageous.ex.parsers.new.tokens_base import TOKEN_DOT
from Vintageous.ex.parsers.new.tokens_base import TOKEN_DOLLAR
from Vintageous.ex.parsers.new.tokens_base import TOKEN_PERCENT
from Vintageous.ex.parsers.new.tokens_base import TOKEN_COMMA
from Vintageous.ex.parsers.new.tokens_base import TOKEN_OFFSET
from Vintageous.ex.parsers.new.tokens_base import TOKEN_SEMICOLON
from Vintageous.ex.parsers.new.tokens_base import TOKEN_SEARCH_FORWARD
from Vintageous.ex.parsers.new.tokens_base import TOKEN_SEARCH_BACKWARD
from Vintageous.ex.parsers.new.tokens_base import TOKEN_MARK
from Vintageous.ex.parsers.new.tokens_base import TOKEN_DIGITS
from Vintageous.ex.parsers.new.tokens import TokenDot
from Vintageous.ex.parsers.new.tokens import TokenDigits
from Vintageous.ex.parsers.new.tokens import TokenDollar
from Vintageous.ex.parsers.new.tokens import TokenPercent
from Vintageous.ex.parsers.new.tokens import TokenComma
from Vintageous.ex.parsers.new.tokens import TokenSemicolon
from Vintageous.ex.parsers.new.tokens import TokenMark
from Vintageous.ex.parsers.new.tokens import TokenOffset
from Vintageous.ex.parsers.new.tokens import TokenSearchForward
from Vintageous.ex.parsers.new.tokens import TokenSearchBackward

from Vintageous.tests import ViewTest



class Test_JsonSerialization_TokenDot(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenDot()
        expected = {'token_type': TOKEN_DOT, 'args': [], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_DOT, 'args': [], 'kwargs': {}}
        self.assertEqual(TokenDot(), TokenDot.from_json(data))


class Test_JsonSerialization_TokenDollar(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenDollar()
        expected = {'token_type': TOKEN_DOLLAR, 'args': [], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_DOLLAR, 'args': [], 'kwargs': {}}
        self.assertEqual(TokenDollar(), TokenDollar.from_json(data))


class Test_JsonSerialization_TokenPercent(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenPercent()
        expected = {'token_type': TOKEN_PERCENT, 'args': [], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_PERCENT, 'args': [], 'kwargs': {}}
        self.assertEqual(TokenPercent(), TokenPercent.from_json(data))


class Test_JsonSerialization_TokenComma(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenComma()
        expected = {'token_type': TOKEN_COMMA, 'args': [], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_COMMA, 'args': [], 'kwargs': {}}
        self.assertEqual(TokenComma(), TokenComma.from_json(data))


class Test_JsonSerialization_TokenSemicolon(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenSemicolon()
        expected = {'token_type': TOKEN_SEMICOLON, 'args': [], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_SEMICOLON, 'args': [], 'kwargs': {}}
        self.assertEqual(TokenSemicolon(), TokenSemicolon.from_json(data))


class Test_JsonSerialization_TokenOffet(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenOffset(10)
        expected = {'token_type': TOKEN_OFFSET, 'args': [10], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_OFFSET, 'args': [10], 'kwargs': {}}
        self.assertEqual(TokenOffset(10), TokenOffset.from_json(data))


class Test_JsonSerialization_TokenSearchForward(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenSearchForward('dog')
        expected = {'token_type': TOKEN_SEARCH_FORWARD, 'args': ['dog'], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_SEARCH_FORWARD, 'args': ['dog'], 'kwargs': {}}
        self.assertEqual(TokenSearchForward('dog'), TokenSearchForward.from_json(data))

    def testCanSerializeEmptyToken(self):
        token = TokenSearchForward()
        expected = {'token_type': TOKEN_SEARCH_FORWARD, 'args': [], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())


class Test_JsonSerialization_TokenSearchBackward(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenSearchBackward('dog')
        expected = {'token_type': TOKEN_SEARCH_BACKWARD, 'args': ['dog'], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_SEARCH_BACKWARD, 'args': ['dog'], 'kwargs': {}}
        self.assertEqual(TokenSearchBackward('dog'), TokenSearchBackward.from_json(data))

    def testCanSerializeEmptyToken(self):
        token = TokenSearchBackward()
        expected = {'token_type': TOKEN_SEARCH_BACKWARD, 'args': [], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())


class Test_JsonSerialization_TokenDigits(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenDigits(10)
        expected = {'token_type': TOKEN_DIGITS, 'args': [10], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_DIGITS, 'args': ['dog'], 'kwargs': {}}
        self.assertEqual(TokenDigits('dog'), TokenDigits.from_json(data))

    def testCanSerializeEmptyToken(self):
        token = TokenDigits()
        expected = {'token_type': TOKEN_DIGITS, 'args': [], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())


class Test_JsonSerialization_TokenMark(unittest.TestCase):
    def testCanSerialize(self):
        token = TokenMark("'a")
        expected = {'token_type': TOKEN_MARK, 'args': ["'a"], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())

    def testCanDeserialize(self):
        data = {'token_type': TOKEN_MARK, 'args': ['dog'], 'kwargs': {}}
        self.assertEqual(TokenMark('dog'), TokenMark.from_json(data))

    def testCanSerializeEmptyToken(self):
        token = TokenMark()
        expected = {'token_type': TOKEN_MARK, 'args': [], 'kwargs': {}}
        self.assertEqual(expected, token.to_json())