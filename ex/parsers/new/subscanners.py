from .scanner_command_only import scan_command_only
from .scanner_command_register import scan_command_register
from .scanner_command_substitute import scan_command_substitute
from .scanner_command_write import scan_command_write
from .scanner_command_buffers import scan_command_buffers
from .scanner_command_abbreviate import scan_command_abbreviate


# TODO: compile regexes.
patterns = {
    r's(?:ubstitute)?(?=[%&:/=]|$)': scan_command_substitute,
    r'on(?:ly)?(?=!$|$)': scan_command_only,
    r'reg(?:isters)?(?=\s+[a-z0-9]+$|$)': scan_command_register,
    r'w(?:rite)?(?=(?:!?(?:\+\+|>>| |$)))': scan_command_write,
    r'(?:ls|files|buffers)!?': scan_command_buffers,
    r'(?:ab(?:breviate)?)': scan_command_abbreviate,
}
