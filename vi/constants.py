# TODO: This module exists solely for retrocompatibility. Delete when possible.

from Vintageous.vi.utils import modes

MODE_INSERT = modes.INSERT
MODE_NORMAL = modes.NORMAL
MODE_VISUAL = modes.VISUAL
MODE_VISUAL_LINE = modes.VISUAL_LINE
# The mode you enter when giving i a count.
MODE_NORMAL_INSERT = modes.NORMAL_INSERT
# Vintageous always runs actions based on selections. Some Vim commands,
# however, behave differently depending on whether the current mode is NORMAL
# or VISUAL. To differentiate NORMAL mode operations (involving only an
# action, or a motion plus an action) from VISUAL mode, we need to add an
# additional mode for handling selections that won't interfere with the actual
# VISUAL mode.
#
# This is _MODE_INTERNAL_NORMAL's job. We consider _MODE_INTERNAL_NORMAL a
# pseudomode, because global state's .mode property should never set to it,
# yet it's set in vi_cmd_data often.
#
# Note that for pure motions we still use plain NORMAL mode.
_MODE_INTERNAL_NORMAL = modes.INTERNAL_NORMAL
MODE_REPLACE = modes.REPLACE
MODE_SELECT = modes.SELECT
MODE_VISUAL_BLOCK = modes.VISUAL_BLOCK


def regions_transformer_reversed(view, f):
    """
    Applies ``f`` to every selection region in ``view`` and replaces the
    existing selections.
    """
    sels = reversed(list(view.sel()))

    new_sels = []
    for s in sels:
        new_sels.append(f(view, s))

    view.sel().clear()
    for ns in new_sels:
        view.sel().add(ns)
