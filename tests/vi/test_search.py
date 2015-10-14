from Vintageous.tests import first_sel
from Vintageous.tests import ViewTest

from Vintageous.vi.search import find_wrapping


class Test_find_wrapping(ViewTest):
    def testCanWrapAroundBuffer(self):
        self.write('''xxx
aaa aaa xxx aaa
''')
        self.clear_sel()
        self.add_sel(a=15, b=15)

        # 15 is after the second xxx
        match = find_wrapping(self.view, 'xxx', 15, self.view.size())
        self.assertEqual(match, self.R(0, 3))

    def testFailsIfSearchStringNotPresent(self):
        self.write('''xxx
aaa aaa xxx aaa
''')
        self.clear_sel()
        self.add_sel(a=15, b=15)

        # 15 is after the second xxx
        match = find_wrapping(self.view, 'yyy', 15, self.view.size())
        self.assertEqual(match, None)

    def testCanFindNextOccurrence(self):
        self.write('''xxx
aaa aaa xxx aaa
''')
        self.clear_sel()
        self.add_sel(a=4, b=4)

        # 4 is the beginning of the second line
        match = find_wrapping(self.view, 'xxx', 4, self.view.size())
        self.assertEqual(match, self.R(12, 15))