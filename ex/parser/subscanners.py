'''
Centralizes all subscanners for ex commands.
'''

from collections import OrderedDict

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
from .scanner_command_write_and_quit_all import scan_command_write_and_quit_all
from .scanner_command_write_and_quit_command import scan_command_write_and_quit_command
from .scanner_command_yank import scan_command_yank


patterns = OrderedDict()

# TODO: compile regexes. ??
# IMPORTANT: Order matters.
patterns[r'!(?=.+)'] = scan_command_shell_out
patterns[r'&&?'] = scan_command_double_ampersand
patterns[r'ab(?:breviate)?'] = scan_command_abbreviate
patterns[r'bro(?:wse)?'] = scan_command_browse
patterns[r'co(?:py)?'] = scan_command_copy
patterns[r'cq(?:uit)?'] = scan_command_cquit
patterns[r'd(?:elete)?'] = scan_command_delete
patterns[r'exi(?:t)?'] = scan_command_exit
patterns[r'f(?:ile)?'] = scan_command_file
patterns[r'g(?:lobal)?(?=[^ ])'] = scan_command_global
patterns[r'(?:ls|files|buffers)!?'] = scan_command_buffers
patterns[r'vs(?:plit)?'] = scan_command_vsplit
patterns[r'x(?:it)?$'] = scan_command_exit
patterns[r'^cd(?=[^d]|$)'] = scan_command_cd_command
patterns[r'^cdd'] = scan_command_cdd_command
patterns[r'e(?:dit)?(?= |$)?'] = scan_command_edit
patterns[r'let\s'] = scan_command_let
patterns[r'm(?:ove)?(?=[^a]|$)'] = scan_command_move
patterns[r'map'] = scan_command_map
patterns[r'new'] = scan_command_new
patterns[r'nm(?:ap)?'] = scan_command_nmap
patterns[r'nun(?:map)?'] = scan_command_nunmap
patterns[r'om(?:ap)?'] = scan_command_omap
patterns[r'on(?:ly)?(?=!$|$)'] = scan_command_only
patterns[r'ounm(?:ap)?'] = scan_command_ounmap
patterns[r'p(?:rint)?$'] = scan_command_print
patterns[r'pwd?$'] = scan_command_print_working_dir
patterns[r'q(?!a)(?:uit)?'] = scan_command_quit_command
patterns[r'qa(?:ll)?'] = scan_command_quit_all_command
patterns[r'r(?!eg)(?:ead)?'] = scan_command_read_shell_out
patterns[r'reg(?:isters)?(?=\s+[a-z0-9]+$|$)'] = scan_command_register
patterns[r's(?:ubstitute)?(?=[%&:/=]|$)'] = scan_command_substitute
patterns[r'se(?:t)?(?=$|\s)'] = scan_command_set
patterns[r'setl(?:ocal)?'] = scan_command_set_local
patterns[r'sh(?:ell)?'] = scan_command_shell
patterns[r'tabfir(?:st)?'] = scan_command_tab_first_command
patterns[r'tabl(?:ast)?'] = scan_command_tab_last_command
patterns[r'tabn(?:ext)?'] = scan_command_tab_next_command
patterns[r'tabo(?:nly)?'] = scan_command_tab_only_command
patterns[r'tabp(?:revious)?'] = scan_command_tab_prev_command
patterns[r'tabr(?:ewind)?'] = scan_command_tab_first_command
patterns[r'una(?:bbreviate)?'] = scan_command_unabbreviate
patterns[r'unm(?:ap)?'] = scan_command_unmap
patterns[r'unvsplit$'] = scan_command_unvsplit
patterns[r'vm(?:ap)?'] = scan_command_vmap
patterns[r'vu(?:nmap)?'] = scan_command_vunmap
patterns[r'w(?:rite)?(?=(?:!?(?:\+\+|>>| |$)))'] = scan_command_write
patterns[r'wqa(?:ll)?'] = scan_command_write_and_quit_all
patterns[r'xa(?:ll)?'] = scan_command_write_and_quit_all
patterns[r'wa(?:ll)?'] = scan_command_write_all
patterns[r'wq(?=[^a-zA-Z]|$)?'] = scan_command_write_and_quit_command
patterns[r'y(?:ank)?'] = scan_command_yank
