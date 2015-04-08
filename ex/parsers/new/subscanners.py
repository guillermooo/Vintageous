from .scanner_command_abbreviate import scan_command_abbreviate
from .scanner_command_browse import scan_command_browse
from .scanner_command_buffers import scan_command_buffers
from .scanner_command_cd_command import scan_command_cd_command
from .scanner_command_cdd_command import scan_command_cdd_command
from .scanner_command_copy import scan_command_copy
from .scanner_command_cquit import scan_command_cquit
from .scanner_command_delete import scan_command_delete
from .scanner_command_double_ampersand import scan_command_double_ampersand
from .scanner_command_edit import scan_command_edit
from .scanner_command_exit import scan_command_exit
from .scanner_command_file import scan_command_file
from .scanner_command_global import scan_command_global
from .scanner_command_let import scan_command_let
from .scanner_command_map import scan_command_map
from .scanner_command_move import scan_command_move
from .scanner_command_new import scan_command_new
from .scanner_command_nmap import scan_command_nmap
from .scanner_command_nunmap import scan_command_nunmap
from .scanner_command_omap import scan_command_omap
from .scanner_command_only import scan_command_only
from .scanner_command_ounmap import scan_command_ounmap
from .scanner_command_print import scan_command_print
from .scanner_command_print_working_dir import scan_command_print_working_dir
from .scanner_command_quit_all_command import scan_command_quit_all_command
from .scanner_command_quit_command import scan_command_quit_command
from .scanner_command_read_shell_out import scan_command_read_shell_out
from .scanner_command_register import scan_command_register
from .scanner_command_set import scan_command_set
from .scanner_command_set_local import scan_command_set_local
from .scanner_command_shell import scan_command_shell
from .scanner_command_shell_out import scan_command_shell_out
from .scanner_command_substitute import scan_command_substitute
from .scanner_command_tab_first_command import scan_command_tab_first_command
from .scanner_command_tab_last_command import scan_command_tab_last_command
from .scanner_command_tab_next_command import scan_command_tab_next_command
from .scanner_command_tab_only_command import scan_command_tab_only_command
from .scanner_command_tab_open_command import scan_command_tab_open_command
from .scanner_command_tab_prev_command import scan_command_tab_prev_command
from .scanner_command_unabbreviate import scan_command_unabbreviate
from .scanner_command_unmap import scan_command_unmap
from .scanner_command_unvsplit import scan_command_unvsplit
from .scanner_command_vmap import scan_command_vmap
from .scanner_command_vsplit import scan_command_vsplit
from .scanner_command_vunmap import scan_command_vunmap
from .scanner_command_write import scan_command_write
from .scanner_command_write_all import scan_command_write_all
from .scanner_command_write_and_quit_command import scan_command_write_and_quit_command
from .scanner_command_write_file import scan_command_write_file
from .scanner_command_yank import scan_command_yank


# TODO: compile regexes.
# TODO: Use ordered dict?
patterns = {
    r's(?:ubstitute)?(?=[%&:/=]|$)': scan_command_substitute,
    r'on(?:ly)?(?=!$|$)': scan_command_only,
    r'reg(?:isters)?(?=\s+[a-z0-9]+$|$)': scan_command_register,
    r'w(?:rite)?(?=(?:!?(?:\+\+|>>| |$)))': scan_command_write,
    r'(?:ls|files|buffers)!?': scan_command_buffers,
    r'(?:ab(?:breviate)?)': scan_command_abbreviate,
    r'(?:vs(?:plit)?)': scan_command_vsplit,
    r'(?:bro(?:wse)?)': scan_command_browse,
    r'^cdd': scan_command_cdd_command,
    r'^cd(?=[^d]|$)': scan_command_cd_command,
    r'(?:co(?:py)?)': scan_command_copy,
    r'(?:cq(?:uit)?)': scan_command_cquit,
    r'(?:d(?:elete)?)': scan_command_delete,
    r'&&?': scan_command_double_ampersand,
    r'e(?:dit)?(?= |$)?': scan_command_edit,
    r'(?:exi(?:t)?)': scan_command_exit,
    r'(?:x(?:it)?)': scan_command_exit,
    r'(?:f(?:ile)?)': scan_command_file,
    r'(?:g(?:lobal)?(?=[^ ]))': scan_command_global,
    r'p(?:rint)?': scan_command_print,
    r'let\s': scan_command_let,
    r'map': scan_command_map,
    r'm(?:ove)?(?=[^a]|$)': scan_command_move,
    r'new': scan_command_new,
    r'nm(?:ap)?': scan_command_nmap,
    r'nun(?:map)?': scan_command_nunmap,
    r'om(?:ap)?': scan_command_omap,
    r'ounm(?:ap)?': scan_command_ounmap,
    r'vm(?:ap)?': scan_command_vmap,
    r'vu(?:nmap)?': scan_command_vunmap,
    r'tabo(?:nly)?': scan_command_tab_only_command,
    r'tabn(?:ext)?': scan_command_tab_next_command,
    r'tabp(?:revious)?': scan_command_tab_prev_command,
    r'tabfir(?:st)?': scan_command_tab_first_command,
    r'tabr(?:ewind)?': scan_command_tab_first_command,
    r'tabl(?:ast)?': scan_command_tab_last_command,
    r'unm(?:ap)?': scan_command_unmap,
    r'q(?!a)(?:uit)?': scan_command_quit_command,
    r'qa(?:ll)?': scan_command_quit_all_command,
    r'wa(?:ll)?': scan_command_write_all,
    r'wq(?=[^a-zA-Z]|$)?': scan_command_write_and_quit_command,
    r'pwd?$': scan_command_print_working_dir,
    r'una(?:bbreviate)?': scan_command_unabbreviate,
    r'unvsplit$': scan_command_unvsplit,
    r'una(?:bbreviate)?': scan_command_unabbreviate,
    # TODO: implement other set variants.
    r'se(?:t)?(?=$|\s)': scan_command_set,
    r'setl(?:ocal)?': scan_command_set_local,
    r'y(?:ank)?': scan_command_yank,
    r'sh(?:ell)?': scan_command_shell,
    r'!(?=.+)': scan_command_shell_out,
    r'r(?:ead)?': scan_command_read_shell_out,
    r'r(?!eg)(?:ead)?': scan_command_read_shell_out,
}
