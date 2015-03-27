
# keep these items ordered by value
TOKEN_EOF = -1
TOKEN_UNKNOWN = 0
TOKEN_DOT = 1
TOKEN_DOLLAR = 2
TOKEN_SEARCH_FORWARD = 3
TOKEN_SEARCH_BACKWARD = 4
TOKEN_COMMA = 5
TOKEN_SEMICOLON = 6
TOKEN_OFFSET = 7
TOKEN_PERCENT = 8
TOKEN_DIGITS = 9
TOKEN_MARK = 10

TOKEN_COMMAND_UNKNOWN = 0
TOKEN_COMMAND_SUBSTITUTE = 1
TOKEN_COMMAND_ONLY = 2
TOKEN_COMMAND_REGISTERS = 3
TOKEN_COMMAND_WRITE = 4
TOKEN_COMMAND_GOTO = 5
TOKEN_COMMAND_BUFFERS = 6
TOKEN_COMMAND_ABBREVIATE = 7
TOKEN_COMMAND_VSPLIT = 8


class Token(object):
    def __init__(self, token_type, content):
        self.token_type = token_type
        self.content = content

    def __str__(self):
        return str(self.content)

    def __repr__(self):
        return '<[{0}]({1})>'.format(self.__class__.__name__, self.content)

    def __eq__(self, other):
        if not isinstance(other, Token):
            return False
        return (other.content == self.content and
                other.token_type == self.token_type)


class TokenOfRange(Token):
    pass


class TokenOfCommand(Token):
    def __init__(self, params, *args, forced=False, **kwargs):
        self.params = params or {}
        self.forced = forced
        # Accepts a range?
        self.addressable = False
        self.target_command = None
        super().__init__(*args, **kwargs)

    def __eq__(self, other):
        return super().__eq__(other) and other.params == self.params

    def to_command_data(self):
        return self.target_command, self.params

    def __str__(self):
        return '{0} {1}'.format(self.content, self.params)

