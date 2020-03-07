# coding: utf-8
# Copyright 2017

"""Testing."""

from unittest import TestCase, TestLoader, TestSuite

from tester import Tester


class TestTester(TestCase):

    """Blank for testing."""

    def test_start(self):
        """Pass."""
        self.assertTrue(Tester())


def suite() -> TestSuite:
    """Return a test suite for execution."""
    tests: TestSuite = TestSuite()
    loader: TestLoader = TestLoader()
    tests.addTest(loader.loadTestsFromTestCase(TestTester))
    return tests
