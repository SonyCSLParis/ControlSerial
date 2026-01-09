#!/usr/bin/env python
"""
Test runner for ControlSerial test suite

This script runs all tests in the ControlSerial test suite and provides
a summary of the results.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py -v           # Verbose output
    python run_tests.py --help       # Show help
"""

import sys
import os
import unittest
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tests.test_encoder_decoder import (
    TestEnvelopeEncoder,
    TestEnvelopeDecoder,
    TestEncoderDecoderIntegration,
    TestEncoderEdgeCases,
    TestDecoderEdgeCases
)

from tests.test_control_serial import (
    TestControlSerialMocked,
    TestControlSerialIntegration,
    TestControlSerialErrorHandling
)


def run_all_tests(verbosity=2):
    """
    Run all test suites
    
    Args:
        verbosity: Level of output detail (0=quiet, 1=normal, 2=verbose)
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes from encoder_decoder tests
    print("\n" + "="*70)
    print("Running EnvelopeEncoder and EnvelopeDecoder Tests")
    print("="*70)
    suite.addTests(loader.loadTestsFromTestCase(TestEnvelopeEncoder))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvelopeDecoder))
    suite.addTests(loader.loadTestsFromTestCase(TestEncoderDecoderIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEncoderEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestDecoderEdgeCases))
    
    # Add all test classes from control_serial tests
    print("\n" + "="*70)
    print("Running ControlSerial Tests (with mocked serial)")
    print("="*70)
    suite.addTests(loader.loadTestsFromTestCase(TestControlSerialMocked))
    suite.addTests(loader.loadTestsFromTestCase(TestControlSerialIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestControlSerialErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed.")
    
    print("="*70)
    
    return result.wasSuccessful()


def run_specific_test_class(test_class_name, verbosity=2):
    """
    Run a specific test class
    
    Args:
        test_class_name: Name of the test class to run
        verbosity: Level of output detail
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # Map test class names to classes
    test_classes = {
        'TestEnvelopeEncoder': TestEnvelopeEncoder,
        'TestEnvelopeDecoder': TestEnvelopeDecoder,
        'TestEncoderDecoderIntegration': TestEncoderDecoderIntegration,
        'TestEncoderEdgeCases': TestEncoderEdgeCases,
        'TestDecoderEdgeCases': TestDecoderEdgeCases,
        'TestControlSerialMocked': TestControlSerialMocked,
        'TestControlSerialIntegration': TestControlSerialIntegration,
        'TestControlSerialErrorHandling': TestControlSerialErrorHandling
    }
    
    if test_class_name not in test_classes:
        print(f"Error: Unknown test class '{test_class_name}'")
        print(f"Available test classes: {', '.join(test_classes.keys())}")
        return False
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(test_classes[test_class_name])
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(
        description='Run ControlSerial test suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests with verbose output
  python run_tests.py -v 1               # Run with normal verbosity
  python run_tests.py -q                 # Run quietly
  python run_tests.py -t TestEnvelopeEncoder  # Run specific test class
        """
    )
    
    parser.add_argument(
        '-v', '--verbosity',
        type=int,
        choices=[0, 1, 2],
        default=2,
        help='Verbosity level: 0=quiet, 1=normal, 2=verbose (default: 2)'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode (same as -v 0)'
    )
    
    parser.add_argument(
        '-t', '--test-class',
        type=str,
        help='Run only a specific test class'
    )
    
    args = parser.parse_args()
    
    # Set verbosity
    verbosity = 0 if args.quiet else args.verbosity
    
    # Run tests
    try:
        if args.test_class:
            success = run_specific_test_class(args.test_class, verbosity)
        else:
            success = run_all_tests(verbosity)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nTest run interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nError running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
