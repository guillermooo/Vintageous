'''
Scanner state.
'''
import re

from .tokens import Token


EOF = '__EOF__'


class ScannerState(object):
    def __init__(self, source):
        # the string to be scanned
        self.source = source
        # current scan position
        self.position = 0
        # most recent scan start
        self.start = 0

    def consume(self):
        '''
        Consumes one character from `source`.
        '''
        if self.position >= len(self.source):
            return EOF
        rv = self.source[self.position]
        self.position += 1
        return rv

    def backup(self):
        '''
        Backs up scanner position by 1 character.
        '''
        self.position -= 1

    def ignore(self):
        '''
        Discards the current span of characters that would normally be
        `.emit()`ted.
        '''
        self.start = self.position

    def emit(self):
        '''
        Returns the `source` substring spanning from [`start`, `position`).

        Also advances `start`.
        '''
        content = self.source[self.start:self.position]
        self.ignore()
        return content

    def skip(self, character):
        '''
        Consumes @character while it matches.
        '''
        while True:
            c = self.consume()
            if c == EOF or c != character:
                break

        if c != EOF:
            self.backup()

    def skip_run(self, characters):
        '''
        Skips @characters while there's a match.
        '''
        while True:
            c = self.consume()
            if c == EOF or c not in characters:
                break

        if c != EOF:
            self.backup()

    def expect(self, item, on_error=None):
        '''
        Requires @item to match at the current `position`.

        Raises a ValueError if @item does not match.

        @item
          A character.

        @on_error
          A function that returns an error. The error returned overrides
          the default ValueError.
        '''
        c = self.consume()
        if c != item:
            if on_error:
                raise on_error()
            raise ValueError('expected {0}, got {1} instead'.format(item, c))
        return c

    def expect_match(self, pattern, on_error=None):
        '''
        Requires @item to match at the current `position`.

        Raises a ValueError if @item does not match.

        @pattern
          A regular expression.

        @on_error
          A function that returns an error. The error returned overrides the
          default ValueError.
        '''
        m = re.compile(pattern).match(self.source, self.position)
        if m:
            self.position += m.end() - m.start()
            return m
        if not on_error:
            raise ValueError('expected match with {0}, at {1}'.format(pattern, self.source[self.position:]))
        raise on_error()

    def peek(self, item):
        '''
        Returns `True` if @item matches at the current position.

        @item
          A string.
        '''
        return self.source[self.position:self.position + len(item)] == item

    def match(self, pattern):
        '''
        Returns the match obtained by searching @pattern.

        The current `position` will advance as many characters as the match's
        length.

        @pattern
          A regular expression.
        '''
        m = re.compile(pattern).match(self.source, self.position)
        if m:
            self.position += m.end() - m.start()
            return m
        return
