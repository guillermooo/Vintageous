import sublime
import sublime_plugin

from Vintageous.state import State
from Vintageous.vi.utils import IrreversibleTextCommand


class ViCommandMixin(object):
    '''
    Provides functionality needed by most vim commands.

    Intended to be used with TextCommand and WindowCommand classes.
    '''

    @property
    def _view(self):
        '''
        Returns the view that should receive any actions.
        '''
        view = None
        try:
            view = self.view
        except AttributeError:
            try:
                view = self.window.active_view()
            except AttributeError:
                raise AttributeError(
                    'ViCommandMixin must be used with a TextCommand or a WindowCommand class')
        return view

    @property
    def _window(self):
        '''
        Returns the view that should receive any actions.
        '''
        window = None
        try:
            window = self.window
        except AttributeError:
            try:
                window = self.view.window()
            except AttributeError:
                raise AttributeError(
                    'ViCommandMixin must be used with a TextCommand or a WindowCommand class')
        return window

    @property
    def state(self):
        return State(self._view)

    def save_sel(self):
        """
        Saves the current .sel() for later reference.
        """
        self.old_sel = tuple(self._view.sel())

    def is_equal_to_old_sel(self, new_sel):
        try:
            return (tuple((s.a, s.b) for s in self.old_sel) ==
                    tuple((s.a, s.b) for s in tuple(self._view.sel())))
        except AttributeError:
            raise AttributeError('have you forgotten to call .save_sel()?')

    def has_sel_changed(self):
        """
        `True` is the current selection is different to .old_sel as recorded
        by .save_sel().
        """
        return not self.is_equal_to_old_sel(self._view.sel())

    def enter_normal_mode(self, mode):
        """
        Calls the command to enter normal mode.

        @mode: The mode the state was in before calling this method.
        """
        self._window.run_command('_enter_normal_mode', {'mode': mode})

    def enter_insert_mode(self, mode):
        """
        Calls the command to enter normal mode.

        @mode: The mode the state was in before calling this method.
        """
        self._window.run_command('_enter_insert_mode', {'mode': mode})

    def set_xpos(self, state):
        try:
            xpos = self._view.rowcol(self._view.sel()[0].b)[1]
        except Exception as e:
            print(e)
            raise ValueError('could not set xpos')

        state.xpos = xpos

    def outline_target(self):
        sels = list(self._view.sel())
        sublime.set_timeout(
                lambda: self._view.erase_regions('vi_yy_target'), 350)
        self._view.add_regions('vi_yy_target', sels, 'comment', '', sublime.DRAW_NO_FILL)


class ViTextCommandBase(sublime_plugin.TextCommand, ViCommandMixin):
    """
    Base class form motion and action commands.

    Not all commands need to derive from this base class, but it's
    recommended they do if there isn't any good reason they shouldn't.
    """

    # Yank config data is controlled through class attributes. ===============
    _can_yank = False
    _synthetize_new_line_at_eof = False
    _yanks_linewise = False
    _populates_small_delete_register = False
    #=========================================================================

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# Due to MRO in Python subclasses, IrreversibleTextCommand must come first so
# that the modified .run_() method is found first.
class ViMotionCommand(IrreversibleTextCommand, ViTextCommandBase):
    """
    Motions should bypass the undo stack.
    """
    pass


class ViWindowCommandBase(sublime_plugin.WindowCommand, ViCommandMixin):
    """
    Base class form some window commands.

    Not all window commands need to derive from this base class, but it's
    recommended they do if there isn't any good reason they shouldn't.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
