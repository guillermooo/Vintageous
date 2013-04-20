import re

EOF = -1

class Lexer(object):
    def __init__(self):
        self.c = None # current character
        self.cursor = 0
        self.string = None

    def _reset(self):
        self.c = None
        self.cursor = 0
        self.string = None

    def consume(self):
        self.cursor += 1
        if self.cursor >= len(self.string):
            self.c = EOF
        else:
            self.c = self.string[self.cursor]

    def _do_parse(self):
        pass

    def parse(self, string):
        if not isinstance(string, basestring):
            raise TypeError("Can only parse strings.")
        self._reset()
        self.string = string
        if not string:
            self.c = EOF
        else:
            self.c = string[0]
        return self._do_parse()


class RegexToken(object):
    def __init__(self, value):
        self.regex = re.compile(value)

    def __contains__(self, value):
        return self.__eq__(value)

    def __eq__(self, other):
        return bool(self.regex.match(other))
