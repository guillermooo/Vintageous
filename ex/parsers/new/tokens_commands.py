from .tokens_base import Token


TOKEN_COMMAND_UNKNOWN = 0
TOKEN_COMMAND_SUBSTITUTE = 1
TOKEN_COMMAND_ONLY = 1
TOKEN_COMMAND_REGISTERS = 2


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


class TokenCommandOnly(TokenOfCommand):
    def __init__(self, *args, **kwargs):
        super().__init__({},
                        TOKEN_COMMAND_ONLY,
                        'only', *args, **kwargs)
        self.target_command = 'ex_only'


class TokenCommandRegisters(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                        TOKEN_COMMAND_REGISTERS,
                        'registers', *args, **kwargs)
        self.target_command = 'ex_list_registers'


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


class TokenCommandWrite(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                        TOKEN_COMMAND_SUBSTITUTE,
                        'write', *args, **kwargs)
        self.addressable = True
        self.target_command = 'ex_write_file'
