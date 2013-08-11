import collections

vi_user_setting = collections.namedtuple('vi_editor_setting', 'scope values default parser')

WINDOW_SETTINGS = [
    'last_buffer_search',
    '_cmdline_cd',
]


SCOPE_WINDOW = 1
SCOPE_VIEW = 2


VI_OPTIONS = {
    # TODO: BUG - unrelated to this code: D,p,u,redo doesn't do what we want.
    'hlsearch': vi_user_setting(scope=SCOPE_VIEW, values=(True, False), default=True, parser=None),
    'incsearch': vi_user_setting(scope=SCOPE_VIEW, values=(True, False), default=True, parser=None),
    'autoindent': vi_user_setting(scope=SCOPE_VIEW, values=(True, False), default=True, parser=None),
}


def get_option(view, name):
    # TODO: Should probably return global, local values.
    option_data = VI_OPTIONS[name]
    if option_data.scope == SCOPE_WINDOW:
        value = view.window().settings().get('vintageous_' + name)
    else:
        value = view.settings().get('vintageous_' + name)

    return value if (value in option_data.values) else option_data.default


class SublimeSettings(object):
    """ Helper class for accessing settings values from views """

    def __init__(self, view=None):
        self.view = view

    def __get__(self, instance, owner):
        if instance is not None:
            return SublimeSettings(instance.v)
        return SublimeSettings()

    def __getitem__(self, key):
        return self.view.settings().get(key)

    def __setitem__(self, key, value):
        self.view.settings().set(key, value)


class VintageSettings(object):
    """ Helper class for accessing settings related to Vintage. """

    def __init__(self, view=None):
        self.view = view

        if view is not None and not isinstance(self.view.settings().get('vintage'), dict):
            self.view.settings().set('vintage', dict())

        if view is not None and view.window() is not None and not isinstance(self.view.window().settings().get('vintage'), dict):
            self.view.window().settings().set('vintage', dict())

    def __get__(self, instance, owner):
        if instance is not None:
            return VintageSettings(instance.v)
        return VintageSettings()

    def __getitem__(self, key):

        # Vi editor options.
        if key in VI_OPTIONS:
            return get_option(self.view, key)

        # Vintageous settings.
        try:
            if key not in WINDOW_SETTINGS:
                value = self.view.settings().get('vintage').get(key)
            else:
                value = self.view.window().settings().get('vintage').get(key)
        except (KeyError, AttributeError):
            value = None
        return value

    def __setitem__(self, key, value):
        if key not in WINDOW_SETTINGS:
            setts, target = self.view.settings().get('vintage'), self.view
        else:
            setts, target = self.view.window().settings().get('vintage'), self.view.window()

        setts[key] = value
        target.settings().set('vintage', setts)


# TODO: Make this a descriptor; avoid instantiation.
class SettingsManager(object):
    view = SublimeSettings()
    vi = VintageSettings()

    def __init__(self, view):
        self.v = view
