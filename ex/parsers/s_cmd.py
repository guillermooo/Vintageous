from Vintageous.ex.parsers.parsing import RegexToken
from Vintageous.ex.parsers.parsing import Lexer
from Vintageous.ex.parsers.parsing import EOF


class SubstituteLexer(Lexer):
    DELIMITER = RegexToken(r'[^a-zA-Z0-9 ]')
    WHITE_SPACE = ' \t'
    FLAG = 'giI'

    def __init__(self):
        self.delimiter = None

    def _match_white_space(self):
        while self.c != EOF and self.c in self.WHITE_SPACE:
            self.consume()

    def _match_count(self):
        buf = []
        while self.c != EOF and self.c.isdigit():
            buf.append(self.c)
            self.consume()
        return ''.join(buf)

    def _match_flags(self):
        buf = []
        while self.c != EOF and self.c in self.FLAG:
            if self.c in self.FLAG:
                buf.append(self.c)
            self.consume()
        return ''.join(buf)

    def _match_pattern(self):
        buf = []
        while self.c != EOF and self.c != self.delimiter:
            if self.c == '\\':
                buf.append(self.c)
                self.consume()
                if self.c in '\\':
                    # Don't store anything, we're escaping \.
                    self.consume()
                elif self.c == self.delimiter:
                    # Overwrite the \ we've just stored.
                    buf[-1] = self.delimiter
                    self.consume()

                if self.c == EOF:
                    break
            else:
                buf.append(self.c)
                self.consume()

        return ''.join(buf)

    def _parse_short(self):
        buf = []
        if self.c == EOF:
            return ['', ''] # no flags, no count

        if self.c.isalpha():
            buf.append(self._match_flags())
            self._match_white_space()
        else:
            buf.append('')

        if self.c != EOF and self.c.isdigit():
            buf.append(self._match_count())
            self._match_white_space()
        else:
            buf.append('')

        if self.c != EOF:
            raise SyntaxError("Trailing characters.")

        return buf

    def _parse_long(self):
        buf = []

        self.delimiter = self.c
        self.consume()

        if self.c == EOF:
            return ['', '', '', '']

        buf.append(self._match_pattern())

        if self.c != EOF:
            # We're at a separator now --we MUST be.
            self.consume()
            buf.append(self._match_pattern())
        else:
            buf.append('')

        if self.c != EOF:
            self.consume()

        if self.c != EOF and self.c in self.FLAG:
            buf.append(self._match_flags())
        else:
            buf.append('')

        if self.c != EOF:
            self._match_white_space()
            buf.append(self._match_count())
        else:
            buf.append('')

        self._match_white_space()
        if self.c != EOF:
            raise SyntaxError("Trailing characters.")

        return buf

    def _do_parse(self):
        self._match_white_space()
        if self.c != EOF and self.c in self.DELIMITER:
            return self._parse_long()
        else:
            return self._parse_short()


def split(s):
    return SubstituteLexer().parse(s)
