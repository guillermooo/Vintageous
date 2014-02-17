import sublime
import sublime_plugin
from Vintageous.vi.sublime import is_view as sublime_is_view

from contextlib import contextmanager
import logging
import re


logging.basicConfig(level=logging.INFO)


def mark_as_widget(view):
    """
    Marks @view as a widget so we can later inspect that attribute, for
    example, when hiding panels in _vi_enter_normal_mode.

    Used prominently by '/', '?' and ':'.
    """
    view.settings().set('is_vintageous_widget', True)
    return view


def is_view(view):
    """
    Returns `True` if @view is a normal view as Vintageous understands them.

    It returns `False` for views that have a `__vi_external_disable`
    setting set to `True`.
    """
    return not any((is_widget(view), is_console(view), is_ignored(view)))


def is_ignored(view):
    """
    Returns `True` if the view wants to be ignored by Vintageous.

    Useful for external plugins that don't want Vintageous to be active for
    specific views.
    """
    return view.settings().get('__vi_external_disable', False)


def is_widget(view):
    """
    Returns `True` if the @view is any kind of widget.
    """
    setts = view.settings()
    return (setts.get('is_widget') or setts.get('is_vintageous_widget'))


def is_console(view):
    """
    Returns `True` if @view seems to be ST3's console.
    """
    # XXX: Is this reliable?
    return (getattr(view, 'settings') is None)


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
    @staticmethod
    def to_friendly_name(mode):
        # if name == COMMAND_LINE:
            # return 'INSERT'
        if mode == modes.INSERT:
            return 'INSERT'
        if mode == modes.INTERNAL_NORMAL:
            return ''
        if mode == modes.NORMAL:
            return ''
        if mode == modes.OPERATOR_PENDING:
            return ''
        if mode == modes.VISUAL:
            return 'VISUAL'
        if mode == modes.VISUAL_BLOCK:
            return 'VISUAL BLOCK'
        if mode == modes.VISUAL_LINE:
            return 'VISUAL LINE'
        if mode == modes.UNKNOWN:
            return 'UNKNOWN'
        if mode == modes.REPLACE:
            return 'REPLACE'
        if mode == modes.NORMAL_INSERT:
            return 'INSERT'
        if mode == modes.SELECT:
            return 'SELECT'
        else:
            return 'REALLY UNKNOWN'

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


class directions:
    NONE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
