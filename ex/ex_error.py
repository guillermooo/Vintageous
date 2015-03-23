"""
This module lists error codes and error display messages along with
utilities to handle them.
"""

import sublime


ERR_FILE_EXISTS = 13
ERR_ADDRESS_REQUIRED = 14 # Command needs an address.
ERR_INVALID_ADDRESS = 14 # Invalid range.
ERR_INVALID_RANGE = 16 # Invalid range.
ERR_NO_FILE_NAME = 32 # Command can't take arguments.
ERR_UNSAVED_CHANGES = 37 # The buffer has been modified but not saved.
ERR_READONLY_FILE = 45
ERR_CANT_MOVE_LINES_ONTO_THEMSELVES = 134
ERR_CANT_WRITE_FILE = 212
ERR_CANT_FIND_DIR_IN_CDPATH = 344
ERR_OTHER_BUFFER_HAS_CHANGES = 445 # :only, for example, may trigger this
ERR_INVALID_ARGUMENT = 474
ERR_NO_BANG_ALLOWED = 477 # Command doesn't allow !.
ERR_NO_RANGE_ALLOWED = 481 # Command can't take a range.
ERR_TRAILING_CHARS = 488 # Unknown command.
ERR_UNKNOWN_COMMAND = 492 # Command can't take arguments.


ERR_MESSAGES = {
    ERR_FILE_EXISTS: 'File exists (add ! to override).',
    ERR_ADDRESS_REQUIRED: 'Invalid address.',
    ERR_INVALID_ADDRESS: 'Invalid address.',
    ERR_INVALID_RANGE: 'Invalid range.',
    ERR_NO_FILE_NAME: 'No file name.',
    ERR_UNSAVED_CHANGES: 'There are unsaved changes.',
    ERR_READONLY_FILE: "'readonly' option is set (add ! to override)",
    ERR_CANT_MOVE_LINES_ONTO_THEMSELVES: "Move lines into themselves.",
    ERR_CANT_WRITE_FILE: "Can't open file for writing.",
    ERR_CANT_FIND_DIR_IN_CDPATH: "Can't fin directory in 'cdpath'.",
    ERR_OTHER_BUFFER_HAS_CHANGES: "Other buffer contains changes.",
    ERR_INVALID_ARGUMENT: "Invalid argument.",
    ERR_NO_BANG_ALLOWED: 'No ! allowed.',
    ERR_NO_RANGE_ALLOWED: 'No range allowed.',
    ERR_TRAILING_CHARS: 'Traling characters.',
    ERR_UNKNOWN_COMMAND: 'Not an editor command.',
}


DISPLAY_STATUS = 1
DISPLAY_CONSOLE = 1 << 1
DISPLAY_ALL = DISPLAY_STATUS | DISPLAY_CONSOLE


def display_message(content, devices=DISPLAY_CONSOLE):
    content = 'Vintageous: {}'.format(content)

    if devices & DISPLAY_CONSOLE == DISPLAY_CONSOLE:
        print(content)

    if devices & DISPLAY_STATUS == DISPLAY_STATUS:
        sublime.status_message(content)


def get_error_message(error_code):
    return ERR_MESSAGES.get(error_code, '')


def display_error(error_code, arg='', log=False):
    err_fmt = "Vintageous: E%d %s"
    if arg:
        err_fmt += " (%s)" % arg
    msg = get_error_message(error_code)
    sublime.status_message(err_fmt % (error_code, msg))


def display_error2(error, devices=DISPLAY_ALL, log=False):
    assert isinstance(error, VimError), "'error' must be an instance of 'VimError'"
    display_message(str(error), devices=devices)


def handle_not_implemented(message=None, devices=DISPLAY_ALL):
    message = message if message else 'Not implemented'
    display_message(message, devices=devices)


class VimError(Exception):
    '''
    Represents e Vim error.
    '''

    def __init__(self, code, *args, **kwargs):
        self.code = code
        self.message = get_error_message(code)
        super().__init__(*args, **kwargs)

    def __str__(self):
        return 'E{0} {1}'.format(self.code, self.message)
