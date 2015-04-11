from .state import EOF
from .tokens import TokenEof
from .tokens_base import TOKEN_COMMAND_GLOBAL
from .tokens_base import TokenOfCommand
from .parser import parse_command_line
from Vintageous import ex


@ex.command('global', 'g')
class TokenCommandGlobal(TokenOfCommand):
    def __init__(self, params, *args, **kwargs):
        super().__init__(params,
                         TOKEN_COMMAND_GLOBAL,
                         'global', *args, **kwargs)
        self.addressable = True
        self.target_command = 'ex_global'

    @property
    def pattern(self):
        return self.params['pattern']

    @property
    def subcommand(self):
        return self.params['subcommand']


def scan_command_global(state):
    params = {
        'pattern': None,
        'subcommand': parse_command_line('print').command
    }

    c = state.consume()

    bang = c == '!'
    sep = c if not bang else c.consume()
    # TODO: we're probably missing legal separators.
    assert c in '!:?/\\&$', 'bad separator'

    state.ignore()

    while True:
        c = state.consume()

        if c == EOF:
            raise ValueError('unexpected EOF in: ' + state.source)

        if c == sep:
            state.backup()
            params['pattern'] = state.emit()
            state.consume()
            state.ignore()
            break

    command = state.match(r'.*$').group(0).strip()
    command = parse_command_line(command).command or params['subcommand']
    params['subcommand'] = command

    return None, [TokenCommandGlobal(params, forced=bang), TokenEof()]
