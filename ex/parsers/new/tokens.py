from .tokens_base import *


class TokenEof(Token):
    def __init__(self, *args, **kwargs):
        super().__init__(TOKEN_EOF, '__EOF__', *args, **kwargs)

    def to_json(self):
        raise TypeError('why would you serialize EOF?')


class TokenOfRange(Token):
    pass


class TokenOfSearch(TokenOfRange):
    pass


class TokenDollar(TokenOfRange):
    def __init__(self, *args, **kwargs):
        super().__init__(TOKEN_DOLLAR, '$', *args, **kwargs)


class TokenComma(TokenOfRange):
    def __init__(self, *args, **kwargs):
        super().__init__(TOKEN_COMMA, ',', *args, **kwargs)


class TokenSemicolon(TokenOfRange):
    def __init__(self, *args, **kwargs):
        super().__init__(TOKEN_SEMICOLON, ';', *args, **kwargs)


class TokenOffset(TokenOfRange):
    def __init__(self, *args, **kwargs):
        content = 0
        if args:
            content = args[0]
            args = args[1:]

        super().__init__(TOKEN_OFFSET, content, *args, **kwargs)

    def to_json(self):
        return {
            'token_type': self.token_type,
            'args': [self.content],
            'kwargs': {}
        }


class TokenPercent(TokenOfRange):
    def __init__(self, *args, **kwargs):
        super().__init__(TOKEN_PERCENT, '%', *args, **kwargs)


class TokenDot(TokenOfRange):
    def __init__(self, *args, **kwargs):
        super().__init__(TOKEN_DOT, '.', *args, **kwargs)


class TokenSearchForward(TokenOfSearch):
    def __init__(self, *args, **kwargs):
        content = None
        if args:
            content = args[0]
            args = args[1:]

        super().__init__(TOKEN_SEARCH_FORWARD, content, *args, **kwargs)

    def to_json(self):
        return {
            'token_type': self.token_type,
            'args': [] if self.content is None else [self.content],
            'kwargs': {}
        }


class TokenSearchBackward(TokenOfSearch):
    def __init__(self, *args, **kwargs):
        content = None
        if args:
            content = args[0]
            args = args[1:]

        super().__init__(TOKEN_SEARCH_BACKWARD, content, *args, **kwargs)

    def to_json(self):
        return {
            'token_type': self.token_type,
            'args': [] if self.content is None else [self.content],
            'kwargs': {}
        }


class TokenDigits(TokenOfRange):
    def __init__(self, *args, **kwargs):
        content = None
        if args:
            content = args[0]
            args = args[1:]

        super().__init__(TOKEN_DIGITS, content, *args, **kwargs)

    def to_json(self):
        return {
            'token_type': self.token_type,
            'args': [] if self.content is None else [self.content],
            'kwargs': {}
        }


class TokenMark(TokenOfRange):
    def __init__(self, *args, **kwargs):
        content = None
        if args:
            content = args[0]
            args = args[1:]

        super().__init__(TOKEN_MARK, content, *args, **kwargs)

    def __str__(self):
        return "'{}".format(self.content)

    def __repr__(self):
        return "<[{0}]('{1})>".format(self.__class__.__name__, self.content)

    def to_json(self):
        return {
            'token_type': self.token_type,
            'args': [] if self.content is None else [self.content],
            'kwargs': {}
        }

    @property
    def exact(self):
        return self.content and self.content.startswith('`')
