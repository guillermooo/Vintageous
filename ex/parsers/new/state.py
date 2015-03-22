import re

from .tokens import Token

EOF = '__EOF__'


class State(object):
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.start = 0

    def consume(self):
        if self.position >= len(self.source):
            return EOF
        rv = self.source[self.position]
        self.position += 1
        return rv

    def backup(self):
        self.position -= 1

    def ignore(self):
        self.start = self.position

    def emit(self):
        content = self.source[self.start:self.position]
        self.ignore()
        return content

    def skip(self, item):
        while True:
            c = self.consume()
            if c == EOF or c != item:
                break

        if c != EOF:
            self.backup()

    def skip_run(self, items):
        while True:
            c = self.consume()
            if c == EOF or c not in items:
                break

        if c != EOF:
            self.backup()

    def expect(self, item):
        c = self.consume()
        if c != item:
           raise ValueError('expected {0}, got {1} instead'.format(item, c))
        return c

    def expect_match(self, pattern, on_error=None):
        m = re.compile(pattern).match(self.source, self.position)
        if m:
            self.position += m.end() - m.start()
            return m
        if not on_error:
            raise ValueError('expected match with {0}, at {1}'.format(pattern, self.source[self.position:]))
        raise on_error()

    def peek(self, item):
        return self.source[self.position:self.position + len(item)] == item

    def match(self, pattern):
        m = re.compile(pattern).match(self.source, self.position)
        if m:
            self.position += m.end() - m.start()
            return m
        return
