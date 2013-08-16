import Vintageous.ex.plat as plat
import Vintageous.ex.plat.linux
import Vintageous.ex.plat.osx
import Vintageous.ex.plat.windows


def run_and_wait(view, cmd):
    if plat.HOST_PLATFORM == plat.WINDOWS:
        plat.windows.run_and_wait(view, cmd)
    elif plat.HOST_PLATFORM == plat.LINUX:
        plat.linux.run_and_wait(view, cmd)
    elif plat.HOST_PLATFORM == plat.OSX:
        plat.osx.run_and_wait(view, cmd)
    else:
        raise NotImplementedError


def run_and_read(view, cmd):
    if plat.HOST_PLATFORM == plat.WINDOWS:
        return plat.windows.run_and_read(view, cmd)
    elif plat.HOST_PLATFORM == plat.LINUX:
        return plat.linux.run_and_read(view, cmd)
    elif plat.HOST_PLATFORM == plat.OSX:
        return plat.osx.run_and_read(view, cmd)
    else:
        raise NotImplementedError


def filter_thru_shell(view, edit, regions, cmd):
    # XXX: make this a ShellFilter class instead
    if plat.HOST_PLATFORM == plat.WINDOWS:
        filter_func = plat.windows.filter_region
    elif plat.HOST_PLATFORM == plat.LINUX:
        filter_func = plat.linux.filter_region
    elif plat.HOST_PLATFORM == plat.OSX:
        filter_func = plat.osx.filter_region
    else:
        raise NotImplementedError

    for r in reversed(regions):
        rv = filter_func(view, view.substr(r), cmd)
        view.replace(edit, r, rv)
