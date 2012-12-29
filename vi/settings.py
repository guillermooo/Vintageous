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
        if view and not isinstance(self.view.settings().get('vintage'), dict):
            self.view.settings().set('vintage', dict())

    def __get__(self, instance, owner):
        if instance is not None:
            return VintageSettings(instance.v)
        return VintageSettings()

    def __getitem__(self, key):
        try:
            value = self.view.settings().get('vintage').get(key)
        except (KeyError, AttributeError):
            value = None
        return value

    def __setitem__(self, key, value):
        setts = self.view.settings().get('vintage')
        setts[key] = value
        self.view.settings().set('vintage', setts)


class SettingsManager(object):
    view = SublimeSettings()
    vi = VintageSettings()

    def __init__(self, view):
        self.v = view
