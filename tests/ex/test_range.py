import unittest
import re

from Vintageous.ex.ex_range import EX_RANGE
from Vintageous.ex.ex_range import new_calculate_range
from Vintageous.ex.ex_range import calculate_relative_ref
from Vintageous.ex.ex_range import calculate_address


class TestCalculateRelativeRef(unittest.TestCase):
    def StartUp(self):
        select_bof(g_test_view)

    def tearDown(self):
        select_bof(g_test_view)

    @unittest.skip('TODO: revise test')
    def testCalculateRelativeRef(self):
        values = (
            (calculate_relative_ref(g_test_view, '.'), 1),
            (calculate_relative_ref(g_test_view, '.', start_line=100), 101),
            (calculate_relative_ref(g_test_view, '$'), 538),
            (calculate_relative_ref(g_test_view, '$', start_line=100), 538),
        )

        for actual, expected in values:
            self.assertEquals(actual, expected)

    @unittest.skip('TODO: revise test')
    def testCalculateRelativeRef2(self):
        self.assertEquals(calculate_relative_ref(g_test_view, '.'), 1)
        self.assertEquals(calculate_relative_ref(g_test_view, '$'), 538)

        select_line(g_test_view, 100)
        self.assertEquals(calculate_relative_ref(g_test_view, '.'), 100)

        select_line(g_test_view, 200)
        self.assertEquals(calculate_relative_ref(g_test_view, '.'), 200)


class TestCalculatingRanges(unittest.TestCase):
    @unittest.skip('TODO: revise test')
    def testCalculateCorrectRange(self):
        values = (
            (new_calculate_range(g_test_view, '0'), [(0, 0)]),
            (new_calculate_range(g_test_view, '1'), [(1, 1)]),
            (new_calculate_range(g_test_view, '1,1'), [(1, 1)]),
            (new_calculate_range(g_test_view, '%,1'), [(1, 538)]),
            (new_calculate_range(g_test_view, '1,%'), [(1, 538)]),
            (new_calculate_range(g_test_view, '1+99,160-10'), [(100, 150)]),
            (new_calculate_range(g_test_view, '/THIRTY/+10,100'), [(40, 100)]),
        )

        select_line(g_test_view, 31)
        values += (
            (new_calculate_range(g_test_view, '10,/THIRTY/'), [(10, 31)]),
            (new_calculate_range(g_test_view, '10;/THIRTY/'), [(10, 30)]),
        )

        for actual, expected in values:
            self.assertEquals(actual, expected)

    def tearDown(self):
        select_bof(g_test_view)


class CalculateAddress(unittest.TestCase):
    def setUp(self):
        super().setUp()
        select_eof(g_test_view)

    def tearDown(self):
        select_bof(g_test_view)

    @unittest.skip('TODO: revise test')
    def testCalculateAddressCorrectly(self):
        values = (
            (dict(ref='100', offset=None, search_offsets=[]), 99),
            (dict(ref='200', offset=None, search_offsets=[]), 199),
        )

        for v, expected in values:
            self.assertEquals(calculate_address(g_test_view, v), expected)

    @unittest.skip('TODO: revise test')
    def testOutOfBoundsAddressShouldReturnNone(self):
        address = dict(ref='1000', offset=None, search_offsets=[])
        self.assertEquals(calculate_address(g_test_view, address), None)

    @unittest.skip('TODO: revise test')
    def testInvalidAddressShouldReturnNone(self):
        address = dict(ref='XXX', offset=None, search_offsets=[])
        self.assertRaises(AttributeError, calculate_address, g_test_view, address)
