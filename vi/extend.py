"""This module provides basic extensibility hooks for external plugins.
"""

from Vintageous.vi.constants import INPUT_FOR_ACTIONS

class PluginManager(object):
    """Collects information from external plugins and manages it.
    """
    def __init__(self):
        self.actions = {}
        # See vi/constants.py (digraphs).
        self.composite_commands = {}
        # See vi/constants.py (INPUT_FOR_MOTIONS)
        self.motion_input_parsers = {}
        # See vi/constants.py (INPUT_FOR_ACTIONS)
        self.action_input_parsers = {}

    # Must be used as a decorator.
    def register_action(self, f):
        self.actions[f.__name__] = f
        return f

    def register_composite_command(self, cc):
        self.composite_commands.update(cc)

    def register_motion_input_parser(self, ip):
        self.motion_input_parsers.update(ip)

    def register_action_input_parser(self, ip):
        INPUT_FOR_ACTIONS.update(ip)
        # self.action_input_parsers.update(ip)

# def plugin_loaded():
#     global plugin_manager
#     plugin_manager = PluginManager()
