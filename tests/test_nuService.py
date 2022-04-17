import unittest

class TestnuService(unittest.TestCase):
    def test_current_savings(self, current_savings=123):
        t=type(current_savings)
        self.assertEqual(t,int)