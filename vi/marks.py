import sublime

# store: window, view, rowcol

_MARKS = {}

class Marks(object):
    def __init__(self, state=None):
        self.state = state

    def __get__(self, instance, owner):
        if not instance:
            return self
        return Marks(instance)

    def add(self, name, view):
        # TODO: support multiple selections
        win, view, rowcol = view.window(), view, view.rowcol(view.sel()[0].b)
        _MARKS[name] = win, view, rowcol

    def get_as_encoded_address(self, name):
        win, view, rowcol = _MARKS.get(name, (None,) * 3)
        if win:
            rowcol_part = ':'.join(str(i) for i in rowcol)
            fname = view.file_name()
            if not fname:
                return None

            # Marks set in the same view as the current one are returned as regions. Marks in other
            # views are returned as encoded addresses that Sublime Text understands.
            if view and view.view_id == self.state.view.view_id:
                return sublime.Region(view.text_point(*rowcol))
            else:
                return "{0}:{1}".format(fname, rowcol_part)
