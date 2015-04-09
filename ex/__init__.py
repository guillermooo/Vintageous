
command_names = []


def register_ex_command(name, abbrev=None):
    command_names.append((name, abbrev))
    def inner_decorator(f):
        return f
    return inner_decorator
