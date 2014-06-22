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

    XXX: This doesn't always work as we expect. For example, changing
         settings to a panel created instants before does not make those
         settings visible when the panel is activated. Investigate.
         We still need this so that contexts will ignore widgets, though.
         However, the fact that they are widgets should suffice to disable
         Vim keys for them...
    """
    view.settings().set('is_vintageous_widget', True)
    return view


def is_view(view):
    """
    Returns `True` if @view is a normal view as Vintageous understands them.

    It returns `False` for views that have a `__vi_external_disable`
    setting set to `True`.
    """
    return not any((is_widget(view), is_console(view),
                    is_ignored(view), is_ignored_but_command_mode(view)))


def is_ignored(view):
    """
    Returns `True` if the view wants to be ignored by Vintageous.

    Useful for external plugins that don't want Vintageous to be active for
    specific views.
    """
    return view.settings().get('__vi_external_disable', False)


def is_ignored_but_command_mode(view):
    """
    Returns `True` if the view wants to be ignored by Vintageous.

    Useful for external plugins that don't want Vintageous to be active for
    specific views.

    .is_ignored_but_command_mode() differs from .is_ignored() in that here
    we declare that only keys should be disabled, not command mode.
    """
    return view.settings().get('__vi_external_disable_keys', False)


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
    CTRL_X = 'mode_control_x'

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
        if mode == modes.CTRL_X:
            return 'Mode ^X'
        else:
            return 'REALLY UNKNOWN'


class input_types:
    """
    Types of input parsers.
    """
    INMEDIATE    = 1
    VIA_PANEL    = 2
    AFTER_MOTION = 3


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


def get_caret_pos_at_b(region):
    """Returns the actual insertion point closest to @region.b for a visual
    region.

    For non-visual regions, the insertion point is always any of the region's
    ends, so using this function is pointless.
    """
    if region.size() == 0:
        raise TypeError('not a visual region')

    if region.a < region.b:
        return region.b - 1
    elif region.b < region.a:
        return region.b


def get_caret_pos_at_a(region):
    """Returns the actual insertion point closest to @region.a for a visual
    region.

    For non-visual regions, the insertion point is always any of the region's
    ends, so using this function is pointless.
    """
    if region.size() == 0:
        raise TypeError('not a visual region')

    if region.a < region.b:
        return region.a
    elif region.b < region.a:
        return region.a - 1


def new_inclusive_region(a, b):
    """
    Creates a region that includes the caracter at @a or @b depending on the
    new region's orientation.
    """
    if a <= b:
        return sublime.Region(a, b + 1)
    else:
        return sublime.Region(a + 1, b)


def row_at(view, pt):
    return view.rowcol(pt)[0]


def col_at(view, pt):
    return view.rowcol(pt)[1]


@contextmanager
def gluing_undo_groups(view, state):
    state.gluing_sequence = True
    view.run_command('mark_undo_groups_for_gluing')
    yield
    view.run_command('glue_marked_undo_groups')
    state.gluing_sequence = False


def blink(times=4, delay=55):
    prefs = sublime.load_settings('Preferences.sublime-settings')
    if prefs.get('vintageous_visualbell') is False:
        return

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


class IrreversibleMouseTextCommand(sublime_plugin.TextCommand):
    """ Base class.

        The undo stack will ignore commands derived from this class. This is
        useful to prevent global state management commands from shadowing
        commands performing edits to the buffer, which are the important ones
        to keep in the undo history.

        This command does not discard the 'event' parameter and so can receive
        mouse data.
    """
    def __init__(self, view):
        sublime_plugin.TextCommand.__init__(self, view)

    def run_(self, edit_token, kwargs):
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


# deprecated
def previous_white_space_char(view, pt, white_space='\t '):
    while pt >= 0 and view.substr(pt) not in white_space:
        pt -= 1
    return pt


def move_backward_while(view, pt, func):
    while (pt >= 0) and func(pt):
        pt -= 1
    return pt


def is_at_eol(view, reg):
    return view.line(reg.b).b == reg.b


def is_at_bol(view, reg):
    return view.line(reg.b).a == reg.b


def translate_char(char):
    # FIXME: What happens to keys like <home>, <up>, etc? We shouln't be
    #        able to use those in some contexts, like as arguments to f, t...
    if char.lower() in ('<enter>', '<cr>'):
        return '\n'
    elif char.lower() in ('<sp>', '<space>'):
        return ' '
    elif char.lower() == '<lt>':
        return '<'
    elif char.lower() == '<tab>':
        return '\t'
    else:
        return char


@contextmanager
def restoring_sel(view):
    regs = list(view.sel())
    view.sel().clear()
    yield
    view.sel().clear()
    view.sel().add_all(regs)


def last_sel(view):
    return get_sel(view, -1)


def second_sel(view):
    return get_sel(view, 1)


def first_sel(view):
    return get_sel(view, 0)


def get_sel(view, i=0):
    return view.sel()[i]


class directions:
    NONE = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
