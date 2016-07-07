import os, sys


import unittest
from datetime import datetime
from mock import patch, call, Mock


class MyTests(unittest.TestCase):
    def setUp(self):
        log_patcher = patch('utilities.nest_event_publisher._logger')
        self._mock_logger = log_patcher.start()

    def test_publish_learning_check_enabled_event_success(self):
        self.fail("Brillant!")


if __name__ == '__main__':
    from pybald.core.logs import default_debug_log

    default_debug_log()
    loader = unittest.TestLoader()
    user_tests = loader.loadTestsFromTestCase(MyTests)
    suite = unittest.TestSuite(user_tests)
    unittest.TextTestRunner(descriptions=True, verbosity=2).run(suite)