from Vintageous import PluginLogger

import sublime

import os


_logger = PluginLogger(__name__)


class DotFile(object):
    def __init__(self, path):
        self.path = path

    @staticmethod
    def from_user():
        path = os.path.join(sublime.packages_path(), 'User', '.vintageousrc')
        return DotFile(path)

    def run(self):
        try:
            with open(self.path, 'r') as f:
                for line in f:
                    cmd, args = self.parse(line)
                    if cmd:
                        _logger.info('[DotFile] running: {0} {1}'.format(cmd, args))
                        sublime.active_window().run_command(cmd, args)
        except FileNotFoundError:
            pass

    def parse(self, line):
        try:
            _logger.info('[DotFile] parsing line: {0}'.format(line))
            if line.startswith((':map ')):
                line = line[1:]
                return ('ex_map', {'command_line': line.rstrip()})

            if line.startswith((':omap ')):
                line = line[len(':omap '):]
                return ('ex_omap', {'cmd': line.rstrip()})

            if line.startswith((':vmap ')):
                line = line[len(':vmap '):]
                return ('ex_vmap', {'cmd': line.rstrip()})

            if line.startswith((':let ')):
                line = line[1:]
                return ('ex_let', {'command_line': line.strip()})
        except Exception:
            print('Vintageous: bad config in dotfile: "%s"' % line.rstrip())
            _logger.debug('bad config inf dotfile: "%s"', line.rstrip())

        return None, None
