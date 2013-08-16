import os
import subprocess
from subprocess import PIPE


def run_and_wait(view, cmd):
    term = view.settings().get('VintageousEx_osx_terminal')
    term = term or os.path.expandvars("$COLORTERM") or os.path.expandvars("$TERM")
    subprocess.Popen([
            term, '-e',
            "bash -c \"%s; read -p 'Press RETURN to exit.'\"" % cmd]).wait()


def run_and_read(view, cmd):
    out, err = subprocess.Popen([cmd], stdout=PIPE, shell=True).communicate()
    try:
        return (out or err).decode('utf-8')
    except AttributeError:
        return ''


def filter_region(view, text, command):
    shell = view.settings().get('VintageousEx_osx_shell')
    shell = shell or os.path.expandvars("$SHELL")
    p = subprocess.Popen([shell, '-c', 'echo "%s" | %s' % (text, command)],
                         stdout=subprocess.PIPE)
    return p.communicate()[0][:-1]
