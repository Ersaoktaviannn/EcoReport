import unittest
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from test_app import EcoReportTestCase
from test_models import ModelsTestCase

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(EcoReportTestCase))
    suite.addTests(loader.loadTestsFromTestCase(ModelsTestCase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)