import sublime
import sublime_plugin

from Vintageous.vi.constants import regions_transformer
from Vintageous.vi.constants import MODE_VISUAL, MODE_NORMAL, _MODE_INTERNAL_NORMAL
from Vintageous.vi.constants import MODE_VISUAL_LINE
from Vintageous.state import VintageState, IrreversibleTextCommand
from Vintageous.vi import utils
from Vintageous.vi.search import reverse_search


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
    def run(self, edit, mode=None, extend=False):
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
    def run(self, edit, mode=None, extend=False):
        def f(view, s):

            pattern = r'\b{0}\b'.format(query)
            flags = sublime.IGNORECASE

            if mode == _MODE_INTERNAL_NORMAL:
                match = reverse_search(view, pattern, 0, current_sel.a, flags)
            else:
                match = reverse_search(view, pattern, 0, current_sel.a, flags)

            if match:
                if mode == _MODE_INTERNAL_NORMAL:
                    return sublime.Region(s.b, match.begin())
                elif state.mode == MODE_VISUAL:
                    return sublime.Region(s.b, match.begin())
                elif state.mode == MODE_NORMAL:
                    return sublime.Region(match.begin(), match.begin())
            return s

        state = VintageState(self.view)
        # TODO: make sure we swallow any leading white space.
        query = self.view.substr(self.view.word(self.view.sel()[0].end()))
        if query:
            state.last_buffer_search = query

        current_sel = self.view.sel()[0]

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
        # Equivalent to /<CR>, which must repeat the last search.
        if s == '':
            state.user_input = state.last_buffer_search

        if s != '':
            state.last_buffer_search = s
        state.eval()

    def on_cancel(self):
        state = VintageState(self.view)
        state.reset()


class ViBufferReverseSearch(IrreversibleTextCommand):
    def run(self):
        self.view.window().show_input_panel('', '', self.on_done, None, self.on_cancel)

    def on_done(self, s):
        # FIXME: Sublime Text seems to reset settings between the .run() call above and this
        # .on_done() method. An issue has been filed about this. Awaiting response.
        state = VintageState(self.view)
        state.motion = 'vi_question_mark'

        state.user_input = s
        # Equivalent to ?<CR>, which must repeat the last search.
        if s == '':
            state.user_input = state.last_buffer_search

        if s != '':
            state.last_buffer_search = s
        state.eval()

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


class _vi_question_mark(sublime_plugin.TextCommand):
    def run(self, edit, search_string, mode=None, count=1, extend=False):
        def f(view, s):
            # FIXME: Readjust carets if we searched for '\n'.
            if mode == MODE_VISUAL:
                if s.b > found.a:
                    return sublime.Region(s.end(), found.a)

            elif mode == _MODE_INTERNAL_NORMAL:
                if s.b > found.a:
                    return sublime.Region(s.end(), found.a)

            elif mode == MODE_NORMAL:
                if s.b > found.a:
                    return sublime.Region(found.a, found.a)

            return s

        # This happens when we attempt to repeat the search and there's no search term stored yet.
        if search_string is None:
            return

        current_sel = self.view.sel()[0]
        # FIXME: What should we do here? Case-sensitive or case-insensitive search? Configurable?
        found = reverse_search(self.view, search_string, 0, current_sel.a)
        if not found:
            print("Vintageous: Pattern not found.")
            return

        for x in range(count - 1):
            found = reverse_search(self.view, search_string, 0, found.a)
            # XXX: Temporary fix until .find() gets fixed.
            if not found:
                print("Vintageous: Pattern not found.")
                return

        regions_transformer(self.view, f)


class _vi_right_brace(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            # TODO: must skip empty paragraphs.
            start = utils.next_non_white_space_char(view, s.b, white_space='\n \t')
            par_as_region = view.expand_by_class(start, sublime.CLASS_EMPTY_LINE)

            if mode == MODE_NORMAL:
                return sublime.Region(min(par_as_region.b, view.size() - 1),
                                      min(par_as_region.b, view.size() - 1))

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a, par_as_region.b + 1)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, par_as_region.b - 1)

            elif mode == MODE_VISUAL_LINE:
                if s.a <= s.b:
                    return sublime.Region(s.a, par_as_region.b + 1)
                else:
                    if par_as_region.b > s.a:
                        return sublime.Region(view.line(s.a - 1).a, par_as_region.b + 1)
                    return sublime.Region(s.a, par_as_region.b)

            return s

        regions_transformer(self.view, f)


class _vi_left_brace(sublime_plugin.TextCommand):
    def run(self, edit, mode=None, extend=False):
        def f(view, s):
            # TODO: must skip empty paragraphs.
            start = utils.previous_non_white_space_char(view, s.b - 1, white_space='\n \t')
            par_as_region = view.expand_by_class(start, sublime.CLASS_EMPTY_LINE)

            if mode == MODE_NORMAL:
                return sublime.Region(par_as_region.a, par_as_region.a)

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a + 1, par_as_region.a)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, par_as_region.a)

            elif mode == MODE_VISUAL_LINE:
                if s.a <= s.b:
                    if par_as_region.a < s.a:
                        return sublime.Region(view.full_line(s.a).b, par_as_region.a)
                    return sublime.Region(s.a, par_as_region.a + 1)
                else:
                    return sublime.Region(s.a, par_as_region.a)

            return s

        regions_transformer(self.view, f)


class _vi_right_parenthesis(sublime_plugin.TextCommand):
    def find_next_sentence_end(self, r):
        sen = r
        while True:
            sen = self.view.expand_by_class(sen, sublime.CLASS_LINE_END)
            if sen.b == self.view.size() or self.view.substr(sen.b - 1) == '.':
                return sen

    def run(self, edit, mode=None, extend=False):

        def f(view, s):
            # TODO: must skip empty paragraphs.
            sen = self.find_next_sentence_end(s)

            if mode == MODE_NORMAL:
                target = min(sen.b + 1, view.size() - 1)
                return sublime.Region(target, target)

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a, sen.b + 1)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, sen.b)

            return s

        regions_transformer(self.view, f)


class _vi_left_parenthesis(sublime_plugin.TextCommand):
    def find_previous_sentence_end(self, r):
        sen = r
        while True:
            sen = self.view.expand_by_class(sen, sublime.CLASS_LINE_END)
            if sen.a <= 0 or self.view.substr(sen.begin() - 1) in ('.', '\n'):
                return sen

    def run(self, edit, mode=None, extend=False):

        def f(view, s):
            # TODO: must skip empty paragraphs.
            sen = self.find_previous_sentence_end(s)

            if mode == MODE_NORMAL:
                return sublime.Region(sen.a + 1, sen.a + 1)

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a + 1, sen.a +  1)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, sen.a + 1)

            return s

        regions_transformer(self.view, f)


class _vi_go_to_symbol(sublime_plugin.TextCommand):
    """Go to local declaration. Differs from Vim because it leverages Sublime Text's ability to
       actually locate symbols (Vim simply searches from the top of the file).
    """
    def find_symbol(self, r, globally):
        query = self.view.substr(self.view.word(r))
        fname = self.view.file_name().replace('\\', '/')

        locations = self.view.window().lookup_symbol_in_index(query)
        if not locations:
            return

        try:
            if not globally:
                location = [hit[2] for hit in locations if fname.endswith(hit[1])][0]
                return location[0] - 1, location[1] - 1
            else:
                # TODO: There might be many symbols with the same name.
                return locations[0]
        except IndexError:
            return


    def run(self, edit, mode=None, extend=False, globally=False):

        def f(view, s):
            if mode == MODE_NORMAL:
                return sublime.Region(location, location)

            elif mode == MODE_VISUAL:
                return sublime.Region(s.a + 1, location)

            elif mode == _MODE_INTERNAL_NORMAL:
                return sublime.Region(s.a, location)

            return s

        current_sel = self.view.sel()[0]
        self.view.sel().clear()
        self.view.sel().add(current_sel)

        location = self.find_symbol(current_sel, globally=globally)
        if not location:
            return

        if globally:
            # Global symbol; simply open the file.
            self.view.window().open_file(location[0] + ':' + ':'.join([str(x) for x in location[2]]), sublime.ENCODED_POSITION)
            return

        # Local symbol; select.
        location = self.view.text_point(*location)
        regions_transformer(self.view, f)
