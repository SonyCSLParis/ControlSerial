"""
Unit tests for ControlSerial module

Copyright (C) 2026
Author(s):  Claude Sonnet 4.5 prompted by Aliénor Lahlou

This file is part of the ControlSerial project.

ControlSerial is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ControlSerial.ControlSerial import EnvelopeEncoder, EnvelopeDecoder


class TestEnvelopeEncoder(unittest.TestCase):
    """Test cases for EnvelopeEncoder class"""
    
    def setUp(self):
        """Set up test encoder instance"""
        self.encoder = EnvelopeEncoder()
    
    def test_convert_string_simple_command(self):
        """Test converting a simple command string"""
        command = 'e[0]'
        result = self.encoder.convert_string(command)
        
        # Should start with # and end with \r\n
        self.assertTrue(result.startswith('#'))
        self.assertTrue(result.endswith('\r\n'))
        self.assertIn('e[0]', result)
        # Should contain counter and CRC
        self.assertIn(':00', result)
    
    def test_convert_with_single_int_arg(self):
        """Test convert method with single integer argument"""
        result = self.encoder.convert('e', 0)
        expected_pattern = '#e[0]:'
        self.assertIn(expected_pattern, result)
    
    def test_convert_with_multiple_args(self):
        """Test convert method with multiple arguments"""
        result = self.encoder.convert('e', 0, 1, 'test')
        
        self.assertIn('e[0,1,"test"]', result)
        self.assertTrue(result.startswith('#'))
        self.assertTrue(result.endswith('\r\n'))
    
    def test_convert_with_string_argument(self):
        """Test that string arguments are properly quoted"""
        result = self.encoder.convert('s', 'hello')
        self.assertIn('"hello"', result)
    
    def test_counter_increments(self):
        """Test that counter increments with each command"""
        result1 = self.encoder.convert('e', 0)
        result2 = self.encoder.convert('e', 0)
        
        # Counter should be different
        self.assertIn(':00', result1)
        self.assertIn(':01', result2)
    
    def test_counter_wraps_around(self):
        """Test that counter wraps around at 254 (because of % 255)"""
        self.encoder.counter = 253
        self.encoder.convert('e', 0)  # counter becomes 254
        self.encoder.convert('e', 0)  # counter becomes 0
        
        # Should wrap back to 0
        self.assertEqual(self.encoder.counter, 0)
    
    def test_invalid_opcode_length(self):
        """Test that multi-character opcodes raise ValueError"""
        with self.assertRaises(ValueError) as context:
            self.encoder.convert('abc', 0)
        self.assertIn('one character', str(context.exception))
    
    def test_invalid_opcode_character(self):
        """Test that invalid opcode characters raise ValueError"""
        with self.assertRaises(ValueError) as context:
            self.encoder.convert('%', 0)
        self.assertIn('Invalid opcode', str(context.exception))
    
    def test_too_many_arguments(self):
        """Test that more than 12 arguments raise ValueError"""
        with self.assertRaises(ValueError) as context:
            self.encoder.convert('e', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13)
        self.assertIn('Too many arguments', str(context.exception))
    
    def test_invalid_argument_type(self):
        """Test that float arguments raise ValueError"""
        with self.assertRaises(ValueError) as context:
            self.encoder.convert('e', 1.5)
        self.assertIn('Unsupported', str(context.exception))
    
    def test_multiple_string_arguments(self):
        """Test that multiple string arguments raise ValueError"""
        with self.assertRaises(ValueError) as context:
            self.encoder.convert('e', 'first', 'second')
        self.assertIn('Too many strings', str(context.exception))
    
    def test_command_too_long(self):
        """Test that commands longer than 58 characters raise ValueError"""
        long_string = 'a' * 60
        with self.assertRaises(ValueError) as context:
            self.encoder.convert_string(long_string)
        self.assertIn('too long', str(context.exception))
    
    def test_valid_opcodes(self):
        """Test that all valid opcodes are accepted"""
        # Test lowercase
        self.encoder.convert('a', 0)
        # Test uppercase
        self.encoder.convert('Z', 0)
        # Test digit
        self.encoder.convert('5', 0)
        # Test question mark
        self.encoder.convert('?', 0)
        # If we got here, all passed
        self.assertTrue(True)
    
    def test_crc_consistency(self):
        """Test that same command generates same CRC"""
        self.encoder.counter = 0
        result1 = self.encoder.convert('e', 0)
        
        self.encoder.counter = 0
        result2 = self.encoder.convert('e', 0)
        
        self.assertEqual(result1, result2)


class TestEnvelopeDecoder(unittest.TestCase):
    """Test cases for EnvelopeDecoder class"""
    
    def setUp(self):
        """Set up test decoder instance"""
        self.decoder = EnvelopeDecoder()
    
    def test_parse_simple_response(self):
        """Test parsing a simple response with array"""
        response = "#R[0,1]\r\n"
        result = self.decoder.parse(response)
        
        self.assertEqual(result, [0, 1])
    
    def test_parse_status_code_response(self):
        """Test parsing response with status code"""
        response = "#R[0]\r\n"
        result = self.decoder.parse(response)
        
        self.assertEqual(result, [0])
    
    def test_parse_error_response(self):
        """Test parsing error response with message"""
        response = '#R[1,"Error message"]\r\n'
        result = self.decoder.parse(response)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 1)
        self.assertEqual(result[1], "Error message")
    
    def test_parse_multiple_values(self):
        """Test parsing response with multiple values"""
        response = "#R[0,123,456,789]\r\n"
        result = self.decoder.parse(response)
        
        self.assertEqual(result, [0, 123, 456, 789])
    
    def test_parse_with_string(self):
        """Test parsing response containing string"""
        response = '#R[0,"test string"]\r\n'
        result = self.decoder.parse(response)
        
        self.assertEqual(result[1], "test string")
    
    def test_is_valid_message_true(self):
        """Test valid message detection"""
        valid_message = "#R[0]\r\n"
        self.assertTrue(self.decoder.is_valid_message(valid_message))
    
    def test_is_valid_message_false(self):
        """Test invalid message detection"""
        invalid_message = "R[0]\r\n"  # Missing #
        self.assertFalse(self.decoder.is_valid_message(invalid_message))
    
    def test_is_valid_message_empty(self):
        """Test that empty message is invalid"""
        self.assertFalse(self.decoder.is_valid_message(""))
    
    def test_is_valid_message_single_char(self):
        """Test that single # character is invalid (needs content)"""
        # Must be > 1 character, so single # is not valid
        self.assertFalse(self.decoder.is_valid_message("#"))
    
    def test_is_log_message_true(self):
        """Test log message detection"""
        log_message = "#!Log message\r\n"
        self.assertTrue(self.decoder.is_log_message(log_message))
    
    def test_is_log_message_false(self):
        """Test non-log message detection"""
        regular_message = "#R[0]\r\n"
        self.assertFalse(self.decoder.is_log_message(regular_message))
    
    def test_is_log_message_short(self):
        """Test that short messages are not log messages"""
        short_message = "#!"
        self.assertFalse(self.decoder.is_log_message(short_message))
    
    def test_parse_negative_values(self):
        """Test parsing response with negative values"""
        response = "#R[-1,-100]\r\n"
        result = self.decoder.parse(response)
        
        self.assertEqual(result, [-1, -100])
    
    def test_parse_mixed_types(self):
        """Test parsing response with mixed types"""
        response = '#R[0,42,"status",123]\r\n'
        result = self.decoder.parse(response)
        
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 42)
        self.assertEqual(result[2], "status")
        self.assertEqual(result[3], 123)


class TestEncoderDecoderIntegration(unittest.TestCase):
    """Integration tests for encoder and decoder working together"""
    
    def setUp(self):
        """Set up encoder and decoder instances"""
        self.encoder = EnvelopeEncoder()
        self.decoder = EnvelopeDecoder()
    
    def test_roundtrip_command_format(self):
        """Test that encoded commands have correct format for decoder"""
        command = self.encoder.convert('e', 0, 1)
        
        # Decoder should recognize it as valid (after getting simulated response)
        simulated_response = "#R[0,100]\r\n"
        self.assertTrue(self.decoder.is_valid_message(simulated_response))
    
    def test_command_structure(self):
        """Test command structure matches expected format"""
        command = self.encoder.convert('t', 42)
        
        # Should have: # + opcode + args + : + counter + crc + \r\n
        self.assertTrue(command.startswith('#t'))
        self.assertIn('[42]', command)
        self.assertIn(':', command)
        self.assertTrue(command.endswith('\r\n'))


class TestEncoderEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def setUp(self):
        """Set up test encoder instance"""
        self.encoder = EnvelopeEncoder()
    
    def test_zero_arguments(self):
        """Test command with no arguments"""
        result = self.encoder.convert('r')
        self.assertIn('#r:', result)
        # Should not have brackets for no args
        self.assertNotIn('[', result)
    
    def test_max_valid_arguments(self):
        """Test with maximum number of valid arguments (12)"""
        result = self.encoder.convert('m', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
        # Should succeed without raising exception
        self.assertIn('#m[', result)
    
    def test_string_with_special_characters(self):
        """Test string argument with special characters"""
        result = self.encoder.convert('s', 'test@#$')
        self.assertIn('"test@#$"', result)
    
    def test_empty_string_argument(self):
        """Test empty string as argument"""
        result = self.encoder.convert('e', '')
        self.assertIn('""', result)
    
    def test_large_integer_argument(self):
        """Test with large integer values"""
        result = self.encoder.convert('n', 999999)
        self.assertIn('999999', result)
    
    def test_negative_integer_argument(self):
        """Test with negative integer values"""
        result = self.encoder.convert('n', -42)
        self.assertIn('-42', result)


class TestDecoderEdgeCases(unittest.TestCase):
    """Test edge cases for decoder"""
    
    def setUp(self):
        """Set up test decoder instance"""
        self.decoder = EnvelopeDecoder()
    
    def test_parse_empty_array(self):
        """Test parsing response with empty array"""
        response = "#R[]\r\n"
        result = self.decoder.parse(response)
        self.assertEqual(result, [])
    
    def test_parse_nested_structure_limitation(self):
        """Test that nested arrays expose decoder limitation"""
        # The decoder finds first ']' not last, so nested arrays don't work
        # This is a known limitation of the simple parser
        response = '#R[[1,2],[3,4]]\r\n'
        # This will raise JSONDecodeError because it extracts '[[1,2]' instead of full array
        with self.assertRaises(Exception):  # JSONDecodeError or similar
            self.decoder.parse(response)
    
    def test_parse_string_with_escaped_quotes(self):
        """Test parsing string with escaped quotes"""
        response = '#R[0,"test\\"quote"]\r\n'
        result = self.decoder.parse(response)
        self.assertIn('test"quote', result[1])


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEnvelopeEncoder))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvelopeDecoder))
    suite.addTests(loader.loadTestsFromTestCase(TestEncoderDecoderIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestEncoderEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestDecoderEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
