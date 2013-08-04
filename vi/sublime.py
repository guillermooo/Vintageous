# An assortment of utilities.

from contextlib import contextmanager


@contextmanager
def restoring_sels(view):
    old_sels = list(view.sel())
    yield
    view.sel().clear()
    for s in old_sels:
        # XXX: If the buffer has changed in the meantime, this won't work well.
        view.sel().add(s)


def has_dirty_buffers(window):
    for v in window.views():
        if v.is_dirty():
            return True
