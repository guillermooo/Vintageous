import sublime
import sublime_plugin

from Vintageous.vi.constants import regions_transformer
from Vintageous.vi.constants import MODE_VISUAL, MODE_NORMAL, _MODE_INTERNAL_NORMAL
from Vintageous.state import VintageState, IrreversibleTextCommand
from Vintageous.vi import utils


class ViMoveToHardBol(sublime_plugin.TextCommand):
    def run(self, edit, extend=False):
        sels = list(self.view.sel())
        self.view.sel().clear()

        new_sels = []
        for s in sels:
            hard_bol = self.view.line(s.b).begin()
            if s.a < s.b and (self.view.line(s.a) != self.view.line(s.b)) and self.view.full_line(hard_bol - 1).b == hard_bol:
                hard_bol += 1
            a, b = (hard_bol, hard_bol) if not extend else (s.a, hard_bol)
            # Avoid ending up with a en empty selection while on visual mode.

            if extend and s.a == hard_bol:
                b = b + 1
            new_sels.append(sublime.Region(a, b))

        for s in new_sels:
            self.view.sel().add(s)

# FIXME: Only find exact char counts. Vim ignores the command when the count is larger than the
# number of instances of the sought character.
class ViFindInLineInclusive(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, character=None, mode=None, count=1):
        def f(view, s):
            offset = s.b + 1 - view.line(s.b).a
            a, eol = s.b + 1, view.line(s.b).b
            final_offset = -1

            try:
                for i in range(count):
                    line_text = view.substr(sublime.Region(a, eol))
                    match_in_line = line_text.index(character)

                    final_offset = offset + match_in_line

                    a = view.line(s.a).a + final_offset + 1
                    offset += match_in_line + 1
            except ValueError:
                pass

            if final_offset > -1:
                pt = view.line(s.b).a + final_offset

                state = VintageState(view)
                if state.mode == MODE_VISUAL or mode == _MODE_INTERNAL_NORMAL:
                    return sublime.Region(s.a, pt + 1)

                return sublime.Region(pt, pt)

            return s

        # TODO: Give feedback to the user that the search failed?
        if character is None:
            return
        else:
            state = VintageState(self.view)
            state.last_character_search = character

        regions_transformer(self.view, f)


# FIXME: Only find exact char counts. Vim ignores the command when the count is larger than the
# number of instances of the sought character.
class ViReverseFindInLineInclusive(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, character=None, mode=None, count=1):
        def f(view, s):
            line_text = view.substr(sublime.Region(view.line(s.b).a, s.b))
            offset = 0
            a, b = view.line(s.b).a, s.b
            final_offset = -1

            try:
                for i in range(count):
                    line_text = view.substr(sublime.Region(a, b))
                    match_in_line = line_text.rindex(character)

                    final_offset = match_in_line

                    b = view.line(s.a).a + final_offset
            except ValueError:
                pass

            if final_offset > -1:
                pt = view.line(s.b).a + final_offset

                state = VintageState(view)
                if state.mode == MODE_VISUAL or mode == _MODE_INTERNAL_NORMAL:
                    return sublime.Region(s.a, pt)

                return sublime.Region(pt, pt)

            return s

        regions_transformer(self.view, f)


class ViFindInLineExclusive(sublime_plugin.TextCommand):
    """Contrary to *f*, *t* does not look past the caret's position, so if ``character`` is under
       the caret, nothing happens.
    """
    def run(self, edit, extend=False, character=None, mode=None, count=1):
        def f(view, s):
            offset = s.b + 1 - view.line(s.b).a
            a, eol = s.b + 1, view.line(s.b).b
            final_offset = -1

            try:
                for i in range(count):
                    line_text = view.substr(sublime.Region(a, eol))
                    match_in_line = line_text.index(character)

                    final_offset = offset + match_in_line

                    a = view.line(s.a).a + final_offset + 1
                    offset += match_in_line + 1
            except ValueError:
                pass

            if final_offset > -1:
                pt = view.line(s.b).a + final_offset

                state = VintageState(view)
                if state.mode == MODE_VISUAL or mode == _MODE_INTERNAL_NORMAL:
                    return sublime.Region(s.a, pt)

                return sublime.Region(pt - 1, pt - 1)

            return s

        # TODO: Give feedback to the user that the search failed?
        if character is None:
            return
        else:
            state = VintageState(self.view)
            state.last_character_search = character

        regions_transformer(self.view, f)


class ViReverseFindInLineExclusive(sublime_plugin.TextCommand):
    """Contrary to *F*, *T* does not look past the caret's position, so if ``character`` is right
       before the caret, nothing happens.
    """
    def run(self, edit, extend=False, character=None, mode=None, count=1):
        def f(view, s):
            line_text = view.substr(sublime.Region(view.line(s.b).a, s.b))
            a, b = view.line(s.b).a, s.b
            final_offset = -1

            try:
                for i in range(count):
                    line_text = view.substr(sublime.Region(a, b))
                    match_in_line = line_text.rindex(character)

                    final_offset = match_in_line

                    b = view.line(s.a).a + final_offset
            except ValueError:
                pass

            if final_offset > -1:
                pt = view.line(s.b).a + final_offset

                state = VintageState(view)
                if state.mode == MODE_VISUAL or mode == _MODE_INTERNAL_NORMAL:
                    return sublime.Region(s.a, pt + 1)

                return sublime.Region(pt + 1, pt + 1)

            return s

        regions_transformer(self.view, f)


class ViGoToLine(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, line=None):
        line = line if line > 0 else 1
        dest = self.view.text_point(line - 1, 0)

        def f(view, s):
            if not extend:
                return sublime.Region(dest, dest)
            else:
                return sublime.Region(s.a, dest)

        regions_transformer(self.view, f)

        # FIXME: Bringing the selections into view will be undesirable in many cases. Maybe we
        # should have an optional .scroll_selections_into_view() step during command execution.
        self.view.show(self.view.sel()[0])


class ViPercent(sublime_plugin.TextCommand):
    def run(self, edit, extend=False, percent=None):
        if percent == None:
            # TODO: 'move_to brackets' isn't as useful as the Vim command. Reimplement our own.
            # TODO: Implement visual counterparts.
            self.view.run_command('move_to', {'to': 'brackets'})
            return

        row = self.view.rowcol(self.view.size())[0] * (percent / 100)

        def f(view, s):
            pt = view.text_point(row, 0)
            return sublime.Region(pt, pt)

        regions_transformer(self.view, f)

        # FIXME: Bringing the selections into view will be undesirable in many cases. Maybe we
        # should have an optional .scroll_selections_into_view() step during command execution.
        self.view.show(self.view.sel()[0])

class _vi_big_h(sublime_plugin.TextCommand):
    def run(self, edit, count=None, extend=False, mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                return sublime.Region(target, target)
            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a + 1, target)
            elif mode == MODE_VISUAL:
                new_target = utils.next_non_white_space_char(view, target)
                return sublime.Region(s.a + 1, new_target)
            else:
                return s

        r = self.view.visible_region()
        row, _ = self.view.rowcol(r.a)
        row += count + 1

        target = self.view.text_point(row, 0)
        
        regions_transformer(self.view, f)
        self.view.show(target)


class ViBigL(sublime_plugin.TextCommand):
    def run(self, edit, count=None, extend=False, mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                return sublime.Region(target, target)
            elif mode == _MODE_INTERNAL_NORMAL:
                if s.b >= target:
                    return sublime.Region(s.a + 1, target)
                return sublime.Region(s.a, target)
            elif mode == MODE_VISUAL:
                if s.b >= target:
                    new_target = utils.next_non_white_space_char(view, target)
                    return sublime.Region(s.a + 1, new_target)
                new_target = utils.next_non_white_space_char(view, target)
                return sublime.Region(s.a, new_target + 1)
            else:
                return s

        r = self.view.visible_region()
        row, _ = self.view.rowcol(r.b)
        row -= count + 1

        # XXXX: Subtract 1 so that Sublime Text won't attempt to scroll the line into view, which
        # would be quite annoying.
        target = self.view.text_point(row - 1, 0)
        
        regions_transformer(self.view, f)
        self.view.show(target)


class ViBigM(sublime_plugin.TextCommand):
    def run(self, edit, count=None, extend=False, mode=None):
        def f(view, s):
            if mode == MODE_NORMAL:
                return sublime.Region(target, target)
            elif mode == _MODE_INTERNAL_NORMAL:
                if s.b >= target:
                    return sublime.Region(s.a + 1, target)
                return sublime.Region(s.a, target)
            elif mode == MODE_VISUAL:
                if s.b >= target:
                    new_target = utils.next_non_white_space_char(view, target)
                    return sublime.Region(s.a + 1, new_target)
                new_target = utils.next_non_white_space_char(view, target)
                return sublime.Region(s.a, new_target + 1)
            else:
                return s

        r = self.view.visible_region()
        row_a, _ = self.view.rowcol(r.a)
        row_b, _ = self.view.rowcol(r.b)
        row = ((row_a + row_b) / 2)

        target = self.view.text_point(row, 0)
        
        regions_transformer(self.view, f)
        self.view.show(target)


class ViStar(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=1, extend=False):
        def f(view, s):

            pattern = r'\b{0}\b'.format(query)
            flags = sublime.IGNORECASE

            if mode == _MODE_INTERNAL_NORMAL:
                match = view.find(pattern, view.word(s.end()).end(), flags)
            else:
                match = view.find(pattern, view.word(s).end(), flags)

            if match:
                if mode == _MODE_INTERNAL_NORMAL:
                    return sublime.Region(s.a, match.begin())
                elif state.mode == MODE_VISUAL:
                    return sublime.Region(s.a, match.begin())
                elif state.mode == MODE_NORMAL:
                    return sublime.Region(match.begin(), match.begin())
            return s

        state = VintageState(self.view)
        # TODO: make sure we swallow any leading white space.
        query = self.view.substr(self.view.word(self.view.sel()[0].end()))
        if query:
            state.last_buffer_search = query

        regions_transformer(self.view, f)


class ViOctothorp(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, count=1, extend=False):
        state = VintageState(self.view)
        def f(view, s):
            return s

        regions_transformer(self.view, f)


class ViBufferSearch(IrreversibleTextCommand):
    def run(self):
        self.view.window().show_input_panel('', '', self.on_done, None, self.on_cancel)

    def on_done(self, s):
        # FIXME: Sublime Text seems to reset settings between the .run() call above and this
        # .on_done() method. An issue has been filed about this. Awaiting response.
        state = VintageState(self.view)
        state.motion = 'vi_forward_slash'
        state.user_input = s
        state.last_buffer_search = s
        state.run()

    def on_cancel(self):
        state = VintageState(self.view)
        state.reset()


class _vi_forward_slash(sublime_plugin.TextCommand):
    def run(self, edit, search_string, mode=None, count=1, extend=False):
        def f(view, s):
            if mode == MODE_VISUAL:
                if s.b < match.a:
                    return sublime.Region(s.a, match.a)

            elif mode == _MODE_INTERNAL_NORMAL:
                if s.b < match.a:
                    return sublime.Region(s.a, match.a)

            elif mode == MODE_NORMAL:
                if s.b < match.a:
                    return sublime.Region(match.a, match.a)

            return s

        # This happens when we attempt to repeat the search and there's no search term stored yet.
        if search_string is None:
            return

        # Start searching from the current selection's end.
        # TODO: We make sure to skip at least one word so most of the time the current word doesn't
        # match the search string and we can search ahead, but this is quite sloppy.
        current_sel = self.view.sel()[0]
        current_sel = current_sel if not current_sel.empty() else self.view.word(current_sel.b)

        # FIXME: What should we do here? Case-sensitive or case-insensitive search? Configurable?
        match = self.view.find(search_string, current_sel.b)
        # XXX: Temporary fix until .find() gets fixed.
        if match.b < 0:
            return

        for x in range(count - 1):
            match = self.view.find(search_string, match.b)
            # XXX: Temporary fix until .find() gets fixed.
            if match.b < 0:
                return

        regions_transformer(self.view, f)
