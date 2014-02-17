"""
check for common build errors
"""

import json
import os
import sys


_this_dir = os.path.dirname(__file__)
_parent = os.path.realpath(os.path.join(_this_dir, '..'))


def check_messages():
    _messages = os.path.realpath(os.path.join(_parent, 'messages.json'))
    _messages_dir = os.path.realpath(os.path.join(_parent, 'messages'))

    msg_paths = None
    try:
        with open(_messages, 'r') as f:
            msg_paths = json.load(f)
    except Exception as e:
        print('syntax error in messages.json')
        print('=' * 80)
        print(e)
        print('=' * 80)
        sys.exit(1)

    def exists(path):
        if os.path.exists(os.path.join(_parent, path)):
            return True

    # is there a file for each message?
    for (_, rel_path) in msg_paths.items():
        if not exists(rel_path):
            print('message file not found: {0}'.format(rel_path))
            sys.exit(1)


if __name__ == '__main__':
    check_messages()
