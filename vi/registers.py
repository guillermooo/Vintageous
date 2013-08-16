import sublime
import os

import itertools


REG_UNNAMED = '"'
REG_SMALL_DELETE = '-'
REG_BLACK_HOLE = '_'
REG_LAST_INSERTED_TEXT = '.'
REG_FILE_NAME = '%'
REG_ALT_FILE_NAME = '#'
REG_EXPRESSION = '='
REG_SYS_CLIPBOARD_1 = '*'
REG_SYS_CLIPBOARD_2 = '+'
REG_SYS_CLIPBOARD_ALL = (REG_SYS_CLIPBOARD_1, REG_SYS_CLIPBOARD_2)
REG_VALID_NAMES = tuple("{0}".format(c) for c in "abcdefghijklmnopqrstuvwxyz")
REG_VALID_NUMBERS = tuple("{0}".format(c) for c in "0123456789")
REG_SPECIAL = (REG_UNNAMED, REG_SMALL_DELETE, REG_BLACK_HOLE,
           REG_LAST_INSERTED_TEXT, REG_FILE_NAME, REG_ALT_FILE_NAME,
           REG_SYS_CLIPBOARD_1, REG_SYS_CLIPBOARD_2)
REG_ALL = REG_SPECIAL + REG_VALID_NUMBERS + REG_VALID_NAMES

# todo(guillermo): There are more.


# Registers must be available globally, so store here the data.
_REGISTER_DATA = {}


# todo(guillermooo): Subclass dict properly.
class Registers(object):
    """
    Registers hold global data mainly used by yank, delete and paste.

    This class is meant to be used a descriptor.

        class VintageState(object):
            registers = Registers()
            ...

        vstate = VintageState()
        vstate.registers["%"] # now vstate.registers has access to the
                              # current view.

    And this is how you access registers:

    Setting registers...

        vstate.registers['a'] = "foo" # => a == "foo"
        vstate.registers['A'] = "bar" # => a == "foobar"
        vstate.registers['1'] = "baz" # => 1 == "baz"
        vstate.registers[1] = "fizz"  # => 1 == "fizz"

    Retrieving registers...

        vstate.registers['a'] # => "foobar"
        vstate.registers['A'] # => "foobar" (synonyms)
    """


    # def __init__(self, view=None, settings=None):
    #     # TODO: Why do we have an __init__? We should be able to set up the class inside the
    #     # __get__ method instead.
    #     self.view = view
    #     self.settings = settings

    def __get__(self, instance, owner):
        self.view = instance.view
        self.settings = instance.settings
        return self
        # This ensures that we can easiy access the active view.
        # return Registers(instance.view, instance.settings)

    def _set_default_register(self, values):
        assert isinstance(values, list)
        # Coerce all values into strings.
        values = [str(v) for v in values]
        # todo(guillermo): could be made a decorator.
        _REGISTER_DATA[REG_UNNAMED] = values

    def _maybe_set_sys_clipboard(self, name, value):
        # We actually need to check whether the option is set to a bool; could
        # be any JSON type.
        if (name in REG_SYS_CLIPBOARD_ALL or
            self.settings.view['vintageous_use_sys_clipboard'] == True):
                # Make sure Sublime Text does the right thing in the presence of multiple
                # selections.
                if len(value) > 1:
                    self.view.run_command('copy')
                else:
                    sublime.set_clipboard(value[0])

    def set(self, name, values):
        """
        Sets an a-z or 0-9 register.

        In order to honor multiple selections in Sublime Text, we need to store register data as
        lists, one per selection. The paste command will then make the final decision about what
        to insert into the buffer when faced with unbalanced selection number / available
        register data.
        """
        # We accept integers as register names.
        name = str(name)
        assert len(str(name)) == 1, "Register names must be 1 char long."

        if name == REG_BLACK_HOLE:
            return

        assert isinstance(values, list), "Register values must be inside a list."
        # Coerce all values into strings.
        values = [str(v) for v in values]

        # Special registers and invalid registers won't be set.
        if (not (name.isalpha() or name.isdigit() or
                 name.isupper() or name == REG_UNNAMED or
                 name == REG_SYS_CLIPBOARD_1 or
                 name == REG_EXPRESSION or
                 name == REG_SMALL_DELETE)):
                    # Vim fails silently.
                    # raise Exception("Can only set a-z and 0-9 registers.")
                    return None

        _REGISTER_DATA[name] = values

        if not name in (REG_EXPRESSION,):
            self._set_default_register(values)
            self._maybe_set_sys_clipboard(name, values)

    def append_to(self, name, suffixes):
        """
        Appends to an a-z register. `name` must be a capital in A-Z.
        """
        assert len(name) == 1, "Register names must be 1 char long."
        assert name in "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "Can only append to A-Z registers."

        existing_values = _REGISTER_DATA.get(name.lower(), '')
        new_values = itertools.zip_longest(existing_values, suffixes, fillvalue='')
        new_values = [(prefix + suffix) for (prefix, suffix) in new_values]
        _REGISTER_DATA[name.lower()] = new_values
        self._set_default_register(new_values)
        self._maybe_set_sys_clipboard(name, new_values)

    def get(self, name=REG_UNNAMED):
        # We accept integers or strings a register names.
        name = str(name)
        assert len(str(name)) == 1, "Register names must be 1 char long."

        # Did we request a special register?
        if name == REG_BLACK_HOLE:
            return
        elif name == REG_FILE_NAME:
            try:
                return [self.view.file_name()]
            except AttributeError:
                return ''
        elif name in REG_SYS_CLIPBOARD_ALL:
            return [sublime.get_clipboard()]
        elif name not in (REG_UNNAMED, REG_SMALL_DELETE) and name in REG_SPECIAL:
            return
        # Special case lumped among these --user always wants the sys
        # clipboard.
        elif name == REG_UNNAMED and self.settings.view['vintageous_use_sys_clipboard'] == True:
            return [sublime.get_clipboard()]

        # If the expression register holds a value and we're requesting the unnamed register,
        # return the expression register and clear it aftwerwards.
        elif name == REG_UNNAMED and _REGISTER_DATA.get(REG_EXPRESSION, ''):
            value = _REGISTER_DATA[REG_EXPRESSION]
            _REGISTER_DATA[REG_EXPRESSION] = ''
            return value

        # We requested an [a-z0-9"] register.
        try:
            # In Vim, "A and "a seem to be synonyms, so accept either.
            return _REGISTER_DATA[name.lower()]
        except KeyError:
            # sublime.status_message("Vintage.Next: E353 Nothing in register %s", name)
            pass

    def yank(self, vi_cmd_data):
        # Populate registers if we have to.
        if vi_cmd_data['can_yank']:
            if vi_cmd_data['register']:
                self[vi_cmd_data['register']] = self.get_selected_text(vi_cmd_data)
            else:
                self[REG_UNNAMED] = self.get_selected_text(vi_cmd_data)

        # # XXX: Small register delete. Improve this implementation.
        if vi_cmd_data['populates_small_delete_register']:
            is_same_line = lambda r: self.view.line(r.begin()) == self.view.line(r.end() - 1)
            if all(is_same_line(x) for x in list(self.view.sel())):
                self[REG_SMALL_DELETE] = self.get_selected_text(vi_cmd_data)

    def get_selected_text(self, vi_cmd_data):
        """Inspect settings and populate registers as needed.
        """
        fragments = [self.view.substr(r) for r in list(self.view.sel())]

        # Add new line at EOF, but don't add too many new lines.
        if vi_cmd_data['synthetize_new_line_at_eof'] and not vi_cmd_data['yanks_linewise']:
            if (not fragments[-1].endswith('\n') and
                # XXX: It appears regions can end beyond the buffer's EOF (?).
                self.view.sel()[-1].b >= self.view.size()):
                    fragments[-1] += '\n'

        if fragments and vi_cmd_data['yanks_linewise']:
            for i, f in enumerate(fragments):
                # When should we add a newline character?
                #  * always except when we have a non-\n-only string followed by a newline char.
                if (not f.endswith('\n')) or (f == '\n') or f.endswith('\n\n'):
                    fragments[i] = f + '\n'
        return fragments

    def to_dict(self):
        # XXX: Stopgap solution until we sublass from dict
        return {name: self.get(name) for name in REG_ALL}

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        try:
            if key.isupper():
                self.append_to(key, value)
            else:
                self.set(key, value)
        except AttributeError:
            self.set(key, value)
