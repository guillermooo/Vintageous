_jump_list = []
_jump_list_index = -1
_current_latest = 1


class JumpList(object):
    def __init__(self, state):
        self.state = state

    def add(self, data):
        # data: [filename, line, column, length]
        # FIXME: This is probably very slow; use a different data structure (???).
        _jump_list.insert(0, data)

        if len(_jump_list) > 100:
            _jump_list.pop()

    def reset(self):
        _jump_list_index = -1
        _jump_list = []

    @property
    def previous(self):
        try:
            idx = _jump_list_index
            next_index = idx + 1
            if next_index > 100:
                next_index = 100
            next_index = min(len(_jump_list) - 1, next_index)
            _jump_list_index = next_index
            return _jump_list[next_index]
        except (IndexError, KeyError) as e:
            return None

    @property
    def next(self):
        try:
            idx = _jump_list_index
            next_index = idx - 1
            if next_index < 0:
                next_index = 0
            next_index = min(len(_jump_list) - 1, next_index)
            _jump_list_index = next_index
            return _jump_list[next_index]
        except (IndexError, KeyError) as e:
            return None

    @property
    def latest(self):
        global _current_latest
        try:
            i = 1 if (_current_latest == 0) else 0
            _current_latest = min(len(_jump_list) - 1, i)
            return _jump_list[_current_latest]
        except (IndexError, KeyError) as e:
            return None
