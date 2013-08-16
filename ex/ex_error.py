"""
This module lists error codes and error display messages along with
utilities to handle them.
"""

import sublime


ERR_UNKNOWN_COMMAND = 492 # Command can't take arguments.
ERR_TRAILING_CHARS = 488 # Unknown command.
ERR_NO_BANG_ALLOWED = 477 # Command doesn't allow !.
ERR_INVALID_RANGE = 16 # Invalid range.
ERR_INVALID_ADDRESS = 14 # Invalid range.
ERR_NO_RANGE_ALLOWED = 481 # Command can't take a range.
ERR_UNSAVED_CHANGES = 37 # The buffer has been modified but not saved.
ERR_ADDRESS_REQUIRED = 14 # Command needs an address.
ERR_OTHER_BUFFER_HAS_CHANGES = 445 # :only, for example, may trigger this
ERR_CANT_MOVE_LINES_ONTO_THEMSELVES = 134
ERR_CANT_FIND_DIR_IN_CDPATH = 344


ERR_MESSAGES = {
    ERR_TRAILING_CHARS: 'Traling characters.',
    ERR_UNKNOWN_COMMAND: 'Not an editor command.',
    ERR_NO_BANG_ALLOWED: 'No ! allowed.',
    ERR_INVALID_RANGE: 'Invalid range.',
    ERR_INVALID_ADDRESS: 'Invalid address.',
    ERR_NO_RANGE_ALLOWED: 'No range allowed.',
    ERR_UNSAVED_CHANGES: 'There are unsaved changes.',
    ERR_ADDRESS_REQUIRED: 'Invalid address.',
    ERR_OTHER_BUFFER_HAS_CHANGES: "Other buffer contains changes.",
    ERR_CANT_MOVE_LINES_ONTO_THEMSELVES: "Move lines into themselves.",
    ERR_CANT_FIND_DIR_IN_CDPATH: "Can't fin directory in 'cdpath'.",
}


def get_error_message(error_code):
    return ERR_MESSAGES.get(error_code, '')


def display_error(error_code, arg='', log=False):
    err_fmt = "Vintageous: E%d %s"
    if arg:
        err_fmt += " (%s)" % arg
    msg = get_error_message(error_code)
    sublime.status_message(err_fmt % (error_code, msg))


def handle_not_implemented():
    sublime.status_message('Vintageous: Not implemented')
