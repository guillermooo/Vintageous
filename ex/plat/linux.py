import os
import subprocess


def run_and_wait(view, cmd):
    term = view.settings().get('VintageousEx_linux_terminal')
    term = term or os.path.expandvars("$COLORTERM") or os.path.expandvars("$TERM")
    subprocess.Popen([
            term, '-e',
            "bash -c \"%s; read -p 'Press RETURN to exit.'\"" % cmd]).wait()


def filter_region(view, text, command):
    shell = view.settings().get('VintageousEx_linux_shell')
    shell = shell or os.path.expandvars("$SHELL")
    p = subprocess.Popen([shell, '-c', 'echo "%s" | %s' % (text, command)],
                         stdout=subprocess.PIPE)
    return p.communicate()[0][:-1]
