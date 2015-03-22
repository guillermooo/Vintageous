from .tokens_base import TokenOfCommand


TOKEN_COMMAND_UNKNOWN = 0
TOKEN_COMMAND_SUBSTITUTE = 1
TOKEN_COMMAND_ONLY = 1
TOKEN_COMMAND_REGISTERS = 2


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

    @property
    def options(self):
        return self.params['++']

    @property
    def target_file(self):
        return self.params['file_name']

    @property
    def appends(self):
        return self.params['>>']

    @property
    def command(self):
        return self.params['cmd']
