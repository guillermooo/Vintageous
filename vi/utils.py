import sublime
import sublime_plugin

from contextlib import contextmanager
import logging
import re


logging.basicConfig(level=logging.INFO)


def get_logger():
    v = sublime.active_window().active_view()
    level = v.settings().get('vintageous_log_level', 'ERROR')
    # logging.basicConfig(level=_str_to_log_level(level))
    logging.basicConfig(level=0)
    return logging


def get_logging_level():
    v = sublime.active_window().active_view()
    level = v.settings().get('vintageous_log_level', 'ERROR')
    return getattr(logging, level.upper(), logging.ERROR)


def get_user_defined_log_level():
    v = sublime.active_window().active_view()
    level = v.settings().get('vintageous_log_level', 'ERROR')
    return getattr(logging, level.upper(), logging.ERROR)



# Use strings because we need to pass modes as arguments in
# Default.sublime-keymap and it's more readable.
class modes:
    """
    Vim modes.
    """
    COMMAND_LINE = 'mode_command_line'
    INSERT = 'mode_insert'
    INTERNAL_NORMAL = 'mode_internal_normal'
    NORMAL = 'mode_normal'
    OPERATOR_PENDING = 'mode_operator_pending'
    VISUAL = 'mode_visual'
    VISUAL_BLOCK = 'mode_visual_block'
    VISUAL_LINE = 'mode_visual_line'
    UNKNOWN = 'mode_unknown'
    REPLACE = 'mode_replace'
    NORMAL_INSERT = 'mode_normal_insert'
    SELECT ='mode_select'


class input_types:
    """
    Types of input parsers.
    """
    INMEDIATE = 1
    VIA_PANEL = 2

class jump_directions:
    FORWARD = 1
    BACK = 0

def regions_transformer(view, f):
    sels = list(view.sel())
    new = []
    for sel in sels:
        region = f(view, sel)
        if not isinstance(region, sublime.Region):
            raise TypeError('sublime.Region required')
        new.append(region)
    view.sel().clear()
    view.sel().add_all(new)


def row_at(view, pt):
    return view.rowcol(pt)[0]


def col_at(view, pt):
    return view.rowcol(pt)[1]


def strip_command_preamble(seq):
    """
    Strips register and count data.
    """
    return re.sub(r'^(?:".)?(?:[1-9]+)?', '', seq)


@contextmanager
def gluing_undo_groups(view, state):
    state.gluing_sequence = True
    view.run_command('mark_undo_groups_for_gluing')
    yield
    view.run_command('glue_marked_undo_groups')
    state.gluing_sequence = False


def blink(times=4, delay=55):
    v = sublime.active_window().active_view()
    settings = v.settings()
    # Ensure we leave the setting as we found it.
    times = times if (times % 2) == 0 else times + 1

    def do_blink():
        nonlocal times
        if times > 0:
            settings.set('highlight_line', not settings.get('highlight_line'))
            times -= 1
            sublime.set_timeout(do_blink, delay)

    do_blink()


class IrreversibleTextCommand(sublime_plugin.TextCommand):
    """ Base class.

        The undo stack will ignore commands derived from this class. This is
        useful to prevent global state management commands from shadowing
        commands performing edits to the buffer, which are the important ones
        to keep in the undo history.
    """
    def __init__(self, view):
        sublime_plugin.TextCommand.__init__(self, view)

    def run_(self, edit_token, kwargs):
        if kwargs and 'event' in kwargs:
            del kwargs['event']

        if kwargs:
            self.run(**kwargs)
        else:
            self.run()

    def run(self, **kwargs):
        pass


def next_non_white_space_char(view, pt, white_space='\t '):
    while (view.substr(pt) in white_space) and (pt <= view.size()):
        pt += 1
    return pt


def previous_non_white_space_char(view, pt, white_space='\t \n'):
    while view.substr(pt) in white_space and pt > 0:
        pt -= 1
    return pt


def is_at_eol(view, reg):
    return view.line(reg.b).b == reg.b


def is_at_bol(view, reg):
    return view.line(reg.b).a == reg.b


def translate_char(char):
    if char.upper() == '<CR>':
        return '\n'
    elif char.upper() == '<SPACE>':
        return ' '
    else:
        return char
