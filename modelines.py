import sublime
import sublime_plugin

import re


MODELINE_PREFIX_TPL = "%s\\s*(st|sublime): "
DEFAULT_LINE_COMMENT = '#'
MULTIOPT_SEP = '; '
MAX_LINES_TO_CHECK = 50
LINE_LENGTH = 80
MODELINES_REG_SIZE = MAX_LINES_TO_CHECK * LINE_LENGTH


def is_modeline(prefix, line):
    return bool(re.match(prefix, line))


def gen_modelines(view):
    topRegEnd = min(MODELINES_REG_SIZE, view.size())
    candidates = view.lines(sublime.Region(0, view.full_line(topRegEnd).end()))

    # Consider modelines at the end of the buffer too.
    # There might be overlap with the top region, but it doesn't matter because
    # it means the buffer is tiny.
    pt = view.size() - MODELINES_REG_SIZE
    bottomRegStart = pt if pt > -1 else 0
    candidates += view.lines(sublime.Region(bottomRegStart, view.size()))

    prefix = build_modeline_prefix(view)
    modelines = (view.substr(c) for c in candidates if is_modeline(prefix, view.substr(c)))

    for modeline in modelines:
        yield modeline


def gen_raw_options(modelines):
    for m in modelines:
        opt = m.partition(':')[2].strip()
        if MULTIOPT_SEP in opt:
            for subopt in (s for s in opt.split(MULTIOPT_SEP)):
                yield subopt
        else:
            yield opt


def gen_modeline_options(view):
    modelines = gen_modelines(view)
    for opt in gen_raw_options(modelines):
        name, sep, value = opt.partition(' ')
        yield view.settings().set, name.rstrip(':'), value.rstrip(';')


def get_line_comment_char(view):
    commentChar = ""
    commentChar2 = ""
    try:
        for pair in view.meta_info("shellVariables", 0):
            if pair["name"] == "TM_COMMENT_START":
                commentChar = pair["value"]
            if pair["name"] == "TM_COMMENT_START_2":
                commentChar2 = pair["value"]
            if commentChar and commentChar2:
                break
    except TypeError:
        pass

    if not commentChar2:
        return re.escape(commentChar.strip())
    else:
        return "(" + re.escape(commentChar.strip()) + "|" + re.escape(commentChar2.strip()) + ")"

def build_modeline_prefix(view):
    lineComment = get_line_comment_char(view).lstrip() or DEFAULT_LINE_COMMENT
    return (MODELINE_PREFIX_TPL % lineComment)


def to_json_type(v):
    """"Convert string value to proper JSON type.
    """
    if v.lower() in ('true', 'false'):
        v = v[0].upper() + v[1:].lower()

    try:
        return eval(v, {}, {})
    except:
        raise ValueError("Could not convert to JSON type.")


class ExecuteSublimeTextModeLinesCommand(sublime_plugin.EventListener):
    """This plugin provides a feature similar to vim modelines.
    Modelines set options local to the view by declaring them in the
    source code file itself.

        Example:
        mysourcecodefile.py
        # sublime: gutter false
        # sublime: translate_tab_to_spaces true

    The top as well as the bottom of the buffer is scanned for modelines.
    MAX_LINES_TO_CHECK * LINE_LENGTH defines the size of the regions to be
    scanned.
    """
    def do_modelines(self, view):
        for setter, name, value in gen_modeline_options(view):
            if name == 'x_syntax':
                view.set_syntax_file(value)
            else:
                try:
                    setter(name, to_json_type(value))
                except ValueError as e:
                    sublime.status_message("[SublimeModelines] Bad modeline detected.")
                    print ("[SublimeModelines] Bad option detected: %s, %s" % (name, value))
                    print ("[SublimeModelines] Tip: Keys cannot be empty strings.")

    def on_load(self, view):
        self.do_modelines(view)

    def on_post_save(self, view):
        self.do_modelines(view)
