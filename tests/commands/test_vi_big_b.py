from collections import namedtuple

from Vintageous.vi.utils import modes

from Vintageous.tests import first_sel
from Vintageous.tests import second_sel
from Vintageous.tests import ViewTest


test_data = namedtuple('test_data', 'content sel params expected actual_func msg')

TESTS = (
    test_data(content='abc', sel=[[(0, 2), (0, 2)]],
              params={'mode': modes.NORMAL}, expected=[(0, 0), (0, 0)],
              actual_func=first_sel,  msg='moves to BOF from single word in file (normal mode)'),
    test_data(content='abc abc', sel=[[(0, 4), (0, 4)]],
              params={'mode': modes.NORMAL},  expected=[(0, 0), (0, 0)],
              actual_func=first_sel,  msg='moves to BOF from second word start (normal mode)'),
    test_data(content='abc a', sel=[[(0, 4), (0, 4)]],
              params={'mode': modes.NORMAL}, expected=[(0, 0), (0, 0)],
              actual_func=first_sel,  msg='moves to BOF from second word start (1-char long) (normal mode)'),

    test_data(content='abc abc', sel=[[(0, 5), (0, 5)]],
              params={'mode': modes.NORMAL, 'count': 2}, expected=[(0, 0), (0, 0)],
              actual_func=first_sel, msg='moves to BOF from second word (count 2) (normal mode)'),

    test_data(content='abc abc', sel=[[(0, 5), (0, 5)]],
              params={'mode': modes.NORMAL, 'count': 10}, expected=[(0, 0), (0, 0)],
              actual_func=first_sel, msg='moves to BOF from second word (excessive count) (normal mode)'),

    # test_data(content='abc', sel=[[(0, 2), (0, 3)]],
    #           params={'mode': modes.VISUAL}, expected=[(0, 3), (0, 0)],
    #           actual_func=first_sel, msg='moves to BOF from single word in file (visual mode)'),
    # test_data(content='abc abc', sel=[[(0, 4), (0, 5)]],
    #           params={'mode': modes.VISUAL},  expected=[(0, 5), (0, 0)],
    #           actual_func=first_sel, msg='moves to BOF from second word start (visual mode)'),
    # test_data(content='abc a', sel=[[(0, 4), (0, 5)]],
    #           params={'mode': modes.VISUAL}, expected=[(0, 5), (0, 0)],
    #           actual_func=first_sel, msg='moves to BOF from second word start (1-char long) (visual mode)'),

    # test_data(content='abc abc', sel=[[(0, 4), (0, 7)]],
    #           params={'mode': modes.VISUAL}, expected=[(0, 4), (0, 5)],
    #           actual_func=first_sel, msg='moves to word start from 1-word selection (visual mode)'),
    # test_data(content='abc abc', sel=[[(0, 0), (0, 8)]],
    #           params={'mode': modes.VISUAL}, expected=[(0, 0), (0, 5)],
    #           actual_func=first_sel, msg='moves to previous word start from multiword selection (visual mode)'),
    )


class Test_vi_b(ViewTest):
    def testAll(self):
        for (i, data) in enumerate(TESTS):
            # TODO: Perhaps we should ensure that other state is reset too?
            self.view.sel().clear()

            self.write(data.content)
            for region in data.sel:
                self.add_sel(self.R(*region))

            self.view.run_command('_vi_big_b', data.params)

            msg = "failed at test index {0}: {1}".format(i, data.msg)
            actual = data.actual_func(self.view)
            self.assertEqual(self.R(*data.expected), actual, msg)