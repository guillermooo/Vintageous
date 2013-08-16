import re

EOF = -1

COMMA = ','
SEMICOLON = ';'
LINE_REF_SEPARATORS = (COMMA, SEMICOLON)

default_range_info = dict(left_ref=None,
                          left_offset=None,
                          left_search_offsets=[],
                          separator=None,
                          right_ref=None,
                          right_offset=None,
                          right_search_offsets=[],
                          text_range='')


class ParserBase(object):
    def __init__(self, source):
        self.c = ''
        self.source = source
        self.result = default_range_info.copy()
        self.n = -1
        self.consume()

    def consume(self):
        if self.c == EOF:
            raise SyntaxError("End of file reached.")
        if self.n == -1 and not self.source:
            self.c = EOF
            return
        else:
            self.n += 1
            if self.n >= len(self.source):
                self.c = EOF
                return
            self.c = self.source[self.n]


class VimParser(ParserBase):
    STATE_NEUTRAL = 0
    STATE_SEARCH_OFFSET = 1

    def __init__(self, *args, **kwargs):
        self.state = VimParser.STATE_NEUTRAL
        self.current_side = 'left'
        ParserBase.__init__(self, *args, **kwargs)

    def parse_full_range(self):
        # todo: make sure that parse_range throws error for unknown tokens
        self.parse_range()
        sep = self.match_one(',;')
        if sep:
            if not self.result[self.current_side + '_offset'] and not self.result[self.current_side + '_ref']:
                self.result[self.current_side + '_ref'] = '.'
            self.consume()
            self.result['separator'] = sep
            self.current_side = 'right'
            self.parse_range()

        if self.c != EOF and not (self.c.isalpha() or self.c in '&!'):
            raise SyntaxError("E492 Not an editor command.")

        return self.result

    def parse_range(self):
        if self.c == EOF:
            return self.result
        line_ref = self.consume_if_in(list('.%$'))
        if line_ref:
            self.result[self.current_side + "_ref"] = line_ref
        while self.c != EOF:
            if self.c == "'":
                self.consume()
                if self.c != EOF and not (self.c.isalpha() or self.c in ("<", ">")):
                    raise SyntaxError("E492 Not an editor command.")
                self.result[self.current_side + "_ref"] = "'%s" % self.c
                self.consume()
            elif self.c in ".$%%'" and not self.result[self.current_side + "_ref"]:
                if (self.result[self.current_side + "_search_offsets"] or
                    self.result[self.current_side + "_offset"]):
                        raise SyntaxError("E492 Not an editor command.")
            elif self.c.startswith(tuple("01234567890+-")):
                offset = self.match_offset()
                self.result[self.current_side + '_offset'] = offset
            elif self.c.startswith(tuple('/?')):
                self.state = VimParser.STATE_SEARCH_OFFSET
                search_offests = self.match_search_based_offsets()
                self.result[self.current_side + "_search_offsets"] = search_offests
                self.state = VimParser.STATE_NEUTRAL
            elif self.c not in ':,;&!' and not self.c.isalpha():
                raise SyntaxError("E492 Not an editor command.")
            else:
                break

            if (self.result[self.current_side + "_ref"] == '%' and
                (self.result[self.current_side + "_offset"] or
                 self.result[self.current_side + "_search_offsets"])):
                    raise SyntaxError("E492 Not an editor command.")

        end = max(0, min(self.n, len(self.source)))
        self.result['text_range'] = self.source[:end]
        return self.result

    def consume_if_in(self, items):
        rv = None
        if self.c in items:
            rv = self.c
            self.consume()
        return rv

    def match_search_based_offsets(self):
        offsets = []
        while self.c != EOF and self.c.startswith(tuple('/?')):
            new_offset = []
            new_offset.append(self.c)
            search = self.match_one_search_offset()
            new_offset.append(search)
            # numeric_offset = self.consume_while_match('^[0-9+-]') or '0'
            numeric_offset = self.match_offset()
            new_offset.append(numeric_offset)
            offsets.append(new_offset)
        return offsets

    def match_one_search_offset(self):
        search_kind = self.c
        rv = ''
        self.consume()
        while self.c != EOF and self.c != search_kind:
            if self.c == '\\':
                self.consume()
                if self.c != EOF:
                    rv += self.c
                    self.consume()
            else:
                rv += self.c
                self.consume()
        if self.c == search_kind:
            self.consume()
        return rv

    def match_offset(self):
        offsets = []
        sign = 1
        is_num_or_sign = re.compile('^[0-9+-]')
        while self.c != EOF and is_num_or_sign.match(self.c):
            if self.c in '+-':
                signs = self.consume_while_match('^[+-]')
                if self.state == VimParser.STATE_NEUTRAL and len(signs) > 1 and not self.result[self.current_side + '_ref']:
                    self.result[self.current_side + '_ref'] = '.'
                if self.c != EOF and self.c.isdigit():
                    if self.state == VimParser.STATE_NEUTRAL and not self.result[self.current_side + '_ref']:
                        self.result[self.current_side + '_ref'] = '.'
                    sign = -1 if signs[-1] == '-' else 1
                    signs = signs[:-1] if signs else []
                subtotal = 0
                for item in signs:
                    subtotal += 1 if item == '+' else -1
                offsets.append(subtotal)
            elif self.c.isdigit():
                nr = self.consume_while_match('^[0-9]')
                offsets.append(sign * int(nr))
                sign = 1
            else:
                break

        return sum(offsets)
        # self.result[self.current_side + '_offset'] = sum(offsets)

    def match_one(self, seq):
        if self.c != EOF and self.c in seq:
            return self.c


    def consume_while_match(self, regex):
        rv = ''
        r = re.compile(regex)
        while self.c != EOF and r.match(self.c):
            rv += self.c
            self.consume()
        return rv


class CommandLineParser(ParserBase):
    def __init__(self, source, *args, **kwargs):
        ParserBase.__init__(self, source, *args, **kwargs)
        self.range_parser = VimParser(source)
        self.result = dict(range=None, commands=[], errors=[])

    def parse_cmd_line(self):
        try:
            rng = self.range_parser.parse_full_range()
        except SyntaxError as e:
            rng = None
            self.result["errors"].append(str(e))
            return self.result

        self.result['range'] = rng
        # sync up with range parser the dumb way
        self.n = self.range_parser.n
        self.c = self.range_parser.c
        while self.c != EOF and self.c == ' ':
            self.consume()
        self.parse_commands()

        if not self.result['commands'][0]['cmd']:
            self.result['commands'][0]['cmd'] = ':'
        return self.result

    def parse_commands(self):
        name = ''
        cmd = {}
        while self.c != EOF:
            if self.c.isalpha() and '&' not in name:
                name += self.c
                self.consume()
            elif self.c == '&' and (not name or name == '&'):
                name += self.c
                self.consume()
            else:
                break

        if not name and self.c  == '!':
            name = '!'
            self.consume()

        cmd['cmd'] = name
        cmd['forced'] = self.c == '!'
        if cmd['forced']:
            self.consume()

        while self.c != EOF and self.c == ' ':
            self.consume()
        cmd['args'] = ''
        if not self.c == EOF:
            cmd['args'] = self.source[self.n:]
        self.result['commands'].append(cmd)


class AddressParser(ParserBase):
    STATE_NEUTRAL = 1
    STATE_SEARCH_OFFSET = 2

    def __init__(self, source, *args, **kwargs):
        ParserBase.__init__(self, source, *args, **kwargs)
        self.result = dict(ref=None, offset=None, search_offsets=[])
        self.state = AddressParser.STATE_NEUTRAL

    def parse(self):
        if self.c == EOF:
            return self.result
        ref = self.consume_if_in(list('.$'))
        if ref:
            self.result["ref"] = ref

        while self.c != EOF:
            if self.c in '0123456789+-':
                rv = self.match_offset()
                self.result['offset'] = rv
            elif self.c in '?/':
                rv = self.match_search_based_offsets()
                self.result['search_offsets'] = rv

        return self.result

    def match_search_based_offsets(self):
        offsets = []
        while self.c != EOF and self.c.startswith(tuple('/?')):
            new_offset = []
            new_offset.append(self.c)
            search = self.match_one_search_offset()
            new_offset.append(search)
            # numeric_offset = self.consume_while_match('^[0-9+-]') or '0'
            numeric_offset = self.match_offset()
            new_offset.append(numeric_offset)
            offsets.append(new_offset)
        return offsets

    def match_one_search_offset(self):
        search_kind = self.c
        rv = ''
        self.consume()
        while self.c != EOF and self.c != search_kind:
            if self.c == '\\':
                self.consume()
                if self.c != EOF:
                    rv += self.c
                    self.consume()
            else:
                rv += self.c
                self.consume()
        if self.c == search_kind:
            self.consume()
        return rv

    def match_offset(self):
        offsets = []
        sign = 1
        is_num_or_sign = re.compile('^[0-9+-]')
        while self.c != EOF and is_num_or_sign.match(self.c):
            if self.c in '+-':
                signs = self.consume_while_match('^[+-]')
                if self.state == AddressParser.STATE_NEUTRAL and len(signs) > 0 and not self.result['ref']:
                    self.result['ref'] = '.'
                if self.c != EOF and self.c.isdigit():
                    sign = -1 if signs[-1] == '-' else 1
                    signs = signs[:-1] if signs else []
                subtotal = 0
                for item in signs:
                    subtotal += 1 if item == '+' else -1
                offsets.append(subtotal)
            elif self.c.isdigit():
                nr = self.consume_while_match('^[0-9]')
                offsets.append(sign * int(nr))
                sign = 1
            else:
                break

        return sum(offsets)

    def match_one(self, seq):
        if self.c != EOF and self.c in seq:
            return self.c


    def consume_while_match(self, regex):
        rv = ''
        r = re.compile(regex)
        while self.c != EOF and r.match(self.c):
            rv += self.c
            self.consume()
        return rv

    def consume_if_in(self, items):
        rv = None
        if self.c in items:
            rv = self.c
            self.consume()
        return rv
