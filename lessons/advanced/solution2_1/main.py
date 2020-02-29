import unittest
import advanced.solution2_1.tests.test_doc_manager as test_doc_manager

def suite():
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromTestCase(
      test_doc_manager.TestSecretary
    )
    suite.addTests(tests)
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())