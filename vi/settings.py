import sublime

import collections
import json

vi_user_setting = collections.namedtuple('vi_editor_setting', 'scope values default parser action noable')

WINDOW_SETTINGS = [
    'last_buffer_search',
    '_cmdline_cd',
]


SCOPE_WINDOW = 1
SCOPE_VIEW = 2
SCOPE_VI_VIEW = 3
SCOPE_VI_WINDOW = 4


def set_generic_view_setting(view, name, value, opt, globally=False):
    if opt.scope == SCOPE_VI_VIEW:
        name = 'vintageous_' + name
    if not opt.parser:
        if not globally or (opt.scope not in (SCOPE_VI_VIEW, SCOPE_VI_WINDOW)):
            view.settings().set(name, value)
        else:
            prefs = sublime.load_settings('Preferences.sublime-settings')
            prefs.set(name, value)
            sublime.save_settings('Preferences.sublime-settings')
        return
    else:
        if not globally or (opt.scope not in (SCOPE_VI_VIEW, SCOPE_VI_WINDOW)):
            view.settings().set(name, opt.parser(value))
        else:
            prefs = sublime.load_settings('Preferences.sublime-settings')
            prefs.set(name, opt.parser(value))
            sublime.save_settings('Preferences.sublime-settings')
        return
    raise ValueError("Vintageous: bad option value")


def set_minimap(view, name, value, opt, globally=False):
    # TODO: Ensure the minimap gets hidden when so desired.
    view.window().run_command('toggle_minimap')


def opt_bool_parser(value):
    if value.lower() in ('false', 'true', '0', '1', 'yes', 'no'):
        if value.lower() in ('true', '1', 'yes'):
            return True
        return False


def opt_rulers_parser(value):
    try:
        converted = json.loads(value)
        if isinstance(converted, list):
            return converted
        else:
            raise ValueError
    except ValueError:
        raise
    except TypeError:
        raise ValueError


VI_OPTIONS = {
    # TODO: BUG - unrelated to this code: D,p,u,redo doesn't do what we want.
    'hlsearch': vi_user_setting(scope=SCOPE_VI_VIEW, values=(True, False, '0', '1'), default=True, parser=opt_bool_parser, action=set_generic_view_setting, noable=True),
    'magic': vi_user_setting(scope=SCOPE_VI_VIEW, values=(True, False, '0', '1'), default=True, parser=opt_bool_parser, action=set_generic_view_setting, noable=True),
    'ignorecase': vi_user_setting(scope=SCOPE_VI_VIEW, values=(True, False, '0', '1'), default=False, parser=opt_bool_parser, action=set_generic_view_setting, noable=True),
    'incsearch': vi_user_setting(scope=SCOPE_VI_VIEW, values=(True, False, '0', '1'), default=True, parser=opt_bool_parser, action=set_generic_view_setting, noable=True),
    'autoindent': vi_user_setting(scope=SCOPE_VI_VIEW, values=(True, False, '0', '1'), default=True, parser=None, action=set_generic_view_setting, noable=False),
    'showminimap': vi_user_setting(scope=SCOPE_WINDOW, values=(True, False, '0', '1'), default=True, parser=None, action=set_minimap, noable=True),
    'rulers': vi_user_setting(scope=SCOPE_VIEW, values=None, default=[], parser=opt_rulers_parser, action=set_generic_view_setting, noable=False),
}


# For completions.
def iter_settings(prefix=''):
    if prefix.startswith('no'):
        for item in (x for (x, y) in VI_OPTIONS.items() if y.noable):
            if ('no' + item).startswith(prefix):
                yield 'no' + item
    else:
        for k in sorted(VI_OPTIONS.keys()):
            if (prefix == '') or k.startswith(prefix):
                yield k


def set_local(view, name, value):
    try:
        opt = VI_OPTIONS[name]
        if not value and opt.noable:
            opt.action(view, name, '1', opt)
            return
        opt.action(view, name, value, opt)
    except KeyError as e:
        if name.startswith('no'):
            try:
                opt = VI_OPTIONS[name[2:]]
                if opt.noable:
                    opt.action(view, name[2:], '0', opt)
                return
            except KeyError:
                pass
        raise


def set_global(view, name, value):
    try:
        opt = VI_OPTIONS[name]
        if not value and opt.noable:
            opt.action(view, name, '1', opt, globally=True)
            return
        opt.action(view, name, value, opt, globally=True)
    except KeyError as e:
        if name.startswith('no'):
            try:
                opt = VI_OPTIONS[name[2:]]
                if opt.noable:
                    opt.action(view, name[2:], '0', opt, globally=True)
                return
            except KeyError:
                pass
        raise


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
