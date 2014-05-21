from Vintageous.vi.utils import get_logger

import sublime

import os


class DotFile(object):
    def __init__(self, path):
        self.path = path
        self.logger = get_logger()

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
                        self.logger.info('[DotFile] running: {0} {1}'.format(cmd, args))
                        sublime.active_window().run_command(cmd, args)
        except FileNotFoundError:
            pass

    def parse(self, line):
        self.logger.info('[DotFile] parsing line: {0}'.format(line))
        if line.startswith((':map ')):
            line = line[len(':map '):]
            return ('ex_map', {'cmd': line.rstrip()})

        if line.startswith((':omap ')):
            line = line[len(':omap '):]
            return ('ex_omap', {'cmd': line.rstrip()})

        if line.startswith((':vmap ')):
            line = line[len(':vmap '):]
            return ('ex_vmap', {'cmd': line.rstrip()})
