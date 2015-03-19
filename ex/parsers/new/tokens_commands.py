from .tokens_base import Token


TOKEN_COMMAND_UNKNOWN = 0
TOKEN_COMMAND_SUBSTITUTE = 1


class TokenOfCommand(Token):
    def __init__(self, params, *args, **kwargs):
        self.params = params or {}
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


class TokenCommandSubstitute(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                        TOKEN_COMMAND_SUBSTITUTE,
                        'substitute', *args, **kwargs)
        self.addressable = True
        self.target_command = 'ex_substitute'

    @property
    def pattern(self):
        return self.params.get('search_term')

    @property
    def replacement(self):
        return self.params.get('replacement')

    @property
    def flags(self):
        return self.params.get('flags', [])

    @property
    def count(self):
        # XXX why 0?
        return self.params.get('count', 0)
