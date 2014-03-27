class cmd_types:
    """
    Types of command.
    """
    MOTION          = 1
    ACTION          = 2
    ANY             = 3
    OTHER           = 4
    USER            = 5
    OPEN_NAME_SPACE = 6


class ViCommandDefBase(object):
    """
    Base class for all Vim commands.
    """

    _serializable = ['_inp',]

    def __init__(self):
        self.input_parser = None
        self._inp = ''

    def __getitem__(self, key):
        # XXX: For compatibility. Should be removed eventually.
        return self.__dict__[key]

    @property
    def accept_input(self):
        return False

    @property
    def inp(self):
        """
        Current input for this command.
        """
        return self._inp

    def accept(self, key):
        """
        Processes input for this command.
        """
        _name = self.__class__.__name__
        assert self.input_parser, '{0} does not provide an input parser'.format(_name)
        raise NotImplementedError(
                '{0} must implement .accept()'.format(_name))

    def reset(self):
        self._inp = ''

    def translate(self, state):
        """
        Returns the command as a valid Json object containing all necessary
        data to be run by Vintageous. This is usually the last step before
        handing the command off to ST.

        Every motion and operator must override this method.

        @state
          The current state.
        """
        raise NotImplementedError('command {0} must implement .translate()'
                                              .format(self.__class__.__name__)
                                              )

    @classmethod
    def from_json(cls, data):
        """
        Instantiates a command from a valid Json object representing one.

        @data
          Serialized command data as provided by .serialize().
        """
        instance = cls()
        instance.__dict__.update(data)
        return instance

    def serialize(self):
        """
        Returns a valid Json object representing this command in a format
        Vintageous uses internally.
        """
        data = {'name': self.__class__.__name__,
                'data': {k: v for k, v in self.__dict__.items()
                              if k in self._serializable}
                }
        return data


class ViMissingCommandDef(ViCommandDefBase):
    def translate(self):
        raise TypeError(
            'ViMissingCommandDef should not be used as a runnable command'
            )


class ViMotionDef(ViCommandDefBase):
    """
    Base class for all motions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updates_xpos = False
        self.scroll_into_view = False
        self.type = cmd_types.MOTION


class ViOperatorDef(ViCommandDefBase):
    """
    Base class for all operators.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.updates_xpos = False
        self.scroll_into_view = False
        self.motion_required = False
        self.type = cmd_types.ACTION
        self.repeatable = False
