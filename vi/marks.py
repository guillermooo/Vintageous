import sublime

# store: window, view, rowcol

_MARKS = {}

class Marks(object):
    def __get__(self, instance, owner):
        self.state = instance
        return self

    def add(self, name, view):
        # TODO: support multiple selections
        # TODO: Use id attribute; references might change.
        win, view, rowcol = view.window(), view, view.rowcol(view.sel()[0].b)
        _MARKS[name] = win, view, rowcol

    def get_as_encoded_address(self, name, exact=False):
        if name == "'":
            # Special case...
            return '<command _vi_double_single_quote>'

        win, view, rowcol = _MARKS.get(name, (None,) * 3)
        if win:
            if exact:
                rowcol_encoded = ':'.join(str(i) for i in rowcol)
            else:
                rowcol_encoded = ':'.join(str(i) for i in (rowcol[0], 0))
            fname = view.file_name()

            # Marks set in the same view as the current one are returned as regions. Marks in other
            # views are returned as encoded addresses that Sublime Text understands.
            if view and view.view_id == self.state.view.view_id:
                if not exact:
                    rowcol = (rowcol[0], 0)
                return sublime.Region(view.text_point(*rowcol))
            else:
                # FIXME: Remove buffers when they are closed.
                if fname:
                    return "{0}:{1}".format(fname, rowcol_encoded)
                else:
                    return "<untitled {0}>:{1}".format(view.buffer_id(), rowcol_encoded)

