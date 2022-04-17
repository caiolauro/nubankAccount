import unittest

class TestnuService(unittest.TestCase):
    def test_current_savings(self, current_savings=123):
        self.assertIsNot(type(current_savings),float)