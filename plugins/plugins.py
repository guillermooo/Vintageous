from Vintageous.vi.utils import modes


mappings = {
   modes.NORMAL: {},
   modes.OPERATOR_PENDING: {},
   modes.VISUAL: {},
   modes.VISUAL_LINE: {},
   modes.VISUAL_BLOCK: {},
   modes.SELECT: {},
}

classes = {}


def register(seq, modes, *args, **kwargs):
    """
    Registers a 'key sequence' to 'command' mapping with Vintageous.

    The registered key sequence must be known to Vintageous. The
    registered command must be a ViMotionDef or ViOperatorDef.

    The decorated class is instantiated with `*args` and `**kwargs`.

    @keys
      A list of (`mode`, `sequence`) pairs to map the decorated
      class to.
    """
    def inner(cls):
        for mode in modes:
                mappings[mode][seq] = cls(*args, **kwargs)
                classes[cls.__name__] = cls
        return cls
    return inner
