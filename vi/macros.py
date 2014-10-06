class MacroRegisters(dict):
    '''Crude implementation of macro registers.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if key in ('%', '#'):
            raise ValueError('invalid register key: %s' % key)
        # TODO(guillermooo): further restrict valid register names.
        # TODO(guillermooo): implement a vs A register.
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        if key in ('%', '#'):
            raise ValueError('unsupported key: %s' % key)
        # TODO(guillermooo): further restrict valid register names.
        # TODO(guillermooo): implement a vs A register.
        return super().__getitem__(key.lower())
