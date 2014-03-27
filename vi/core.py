import sublime
import sublime_plugin

from Vintageous.state import State
from Vintageous.vi.utils import IrreversibleTextCommand


class ViTextCommandBase(sublime_plugin.TextCommand):
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

    @property
    def state(self):
        return State(self.view)

    def save_sel(self):
        """
        Saves the current .sel() for later reference.
        """
        self.old_sel = tuple(self.view.sel())

    def is_equal_to_old_sel(self, new_sel):
        try:
            return (tuple((s.a, s.b) for s in self.old_sel) ==
                    tuple((s.a, s.b) for s in tuple(self.view.sel())))
        except AttributeError:
            raise AttributeError('have you forgotten to call .save_sel()?')

    def has_sel_changed(self):
        """
        `True` is the current selection is different to .old_sel as recorded
        by .save_sel().
        """
        return not self.is_equal_to_old_sel(self.view.sel())

    def enter_normal_mode(self, mode):
        """
        Calls the command to enter normal mode.

        @mode: The mode the state was in before calling this method.
        """
        self.view.window().run_command('_enter_normal_mode', {'mode': mode})

    def enter_insert_mode(self, mode):
        """
        Calls the command to enter normal mode.

        @mode: The mode the state was in before calling this method.
        """
        self.view.window().run_command('_enter_insert_mode', {'mode': mode})

    def set_xpos(self, state):
        try:
            xpos = self.view.rowcol(self.view.sel()[0].b)[1]
        except Exception as e:
            print(e)
            raise ValueError('could not set xpos')

        state.xpos = xpos

    def outline_target(self):
        sels = list(self.view.sel())
        sublime.set_timeout(lambda: self.view.erase_regions('vi_training_wheels'), 350)
        self.view.add_regions('vi_training_wheels', sels, 'comment', '', sublime.DRAW_NO_FILL)


class ViMotionCommand(ViTextCommandBase, IrreversibleTextCommand):
    """
    Motions should bypass the undo stack.
    """
    pass


class ViWindowCommandBase(sublime_plugin.WindowCommand):
    """
    Base class form some window commands.

    Not all window commands need to derive from this base class, but it's
    recommended they do if there isn't any good reason they shouldn't.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def state(self):
        return State(self.window.active_view())
