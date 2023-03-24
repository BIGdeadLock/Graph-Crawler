import unittest
import sys


if __name__ == '__main__':

    # discover all the test files in the current directory
    test_files = unittest.TestLoader().discover('.')

    # create a test suite from the discovered test files
    test_suite = unittest.TestSuite(test_files)

    # run the test suite
    result = unittest.TextTestRunner().run(test_suite)

    # Return the status code
    sys.exit(not result.wasSuccessful())
