'''
Misc stuff needed for ex commands.
'''

# Used to provide completions on the ex command line.
command_names = []


def command(name, abbrev):
    """
    Registers the name of an ex command with `command_names`.

    Meant to be imported like this:

        from Vintageous import ex

        ...

        @ex.command('foo', 'f')
        class ExFooCommand(...):
            ...
    """
    command_names.append((name, abbrev))
    def inner(f):
        return f
    return inner
