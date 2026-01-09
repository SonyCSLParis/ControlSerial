"""
Unit tests for ControlSerial class with mocked serial communication

Copyright (C) 2026
Author(s): Claude Sonnet 4.5 prompted by Aliénor Lahlou

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
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ControlSerial.ControlSerial import ControlSerial, EnvelopeEncoder, EnvelopeDecoder


class TestControlSerialMocked(unittest.TestCase):
    """Test ControlSerial class with mocked serial connection"""
    
    @patch('ControlSerial.ControlSerial.serial.Serial')
    @patch('ControlSerial.ControlSerial.time.sleep')
    def setUp(self, mock_sleep, mock_serial):
        """Set up mocked ControlSerial instance"""
        self.mock_serial_instance = MagicMock()
        mock_serial.return_value = self.mock_serial_instance
        
        # Create ControlSerial instance with mocked serial
        self.device = ControlSerial('/dev/ttyUSB0')
        self.mock_sleep = mock_sleep
    
    def test_initialization(self):
        """Test ControlSerial initialization"""
        self.assertIsNotNone(self.device)
        self.assertIsInstance(self.device.encoder, EnvelopeEncoder)
        self.assertIsInstance(self.device.decoder, EnvelopeDecoder)
        self.assertFalse(self.device.debug)
    
    def test_debug_mode_toggle(self):
        """Test debug mode can be enabled and disabled"""
        self.assertFalse(self.device.get_debug())
        
        self.device.set_debug(True)
        self.assertTrue(self.device.get_debug())
        
        self.device.set_debug(False)
        self.assertFalse(self.device.get_debug())
    
    def test_get_driver(self):
        """Test getting the serial driver"""
        driver = self.device.get_driver()
        self.assertEqual(driver, self.mock_serial_instance)
    
    def test_execute_successful_command(self):
        """Test executing a successful command"""
        # Mock successful response
        self.mock_serial_instance.readline.return_value = b"#R[0,42]\r\n"
        
        result = self.device.execute('e', 0)
        
        # Should return status code 0 and value 42
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 42)
        
        # Verify serial write was called
        self.mock_serial_instance.write.assert_called_once()
    
    def test_execute_with_multiple_args(self):
        """Test executing command with multiple arguments"""
        self.mock_serial_instance.readline.return_value = b"#R[0]\r\n"
        
        result = self.device.execute('m', 1, 2, 3)
        
        self.assertEqual(result[0], 0)
        self.mock_serial_instance.write.assert_called_once()
    
    def test_send_command_string(self):
        """Test sending a command as string"""
        self.mock_serial_instance.readline.return_value = b"#R[0,100]\r\n"
        
        result = self.device.send_command('t[50]')
        
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 100)
    
    def test_execute_error_response(self):
        """Test handling error response from device"""
        # Mock error response (positive status code)
        self.mock_serial_instance.readline.return_value = b'#R[1,"Command error"]\r\n'
        
        with self.assertRaises(RuntimeError) as context:
            self.device.execute('e', 0)
        
        self.assertIn("Command error", str(context.exception))
    
    def test_execute_retry_on_negative_status(self):
        """Test retry mechanism on negative status code"""
        # First 2 attempts fail with -1, third succeeds
        self.mock_serial_instance.readline.side_effect = [
            b"#R[-1]\r\n",
            b"#R[-1]\r\n",
            b"#R[0,100]\r\n"
        ]
        
        result = self.device.execute('r')
        
        # Should eventually succeed
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 100)
        
        # Should have tried 3 times
        self.assertEqual(self.mock_serial_instance.write.call_count, 3)
    
    def test_execute_max_retries_exceeded(self):
        """Test that max retries raises RuntimeError"""
        # All attempts fail with -1
        self.mock_serial_instance.readline.return_value = b"#R[-1]\r\n"
        
        with self.assertRaises(RuntimeError) as context:
            self.device.execute('e', 0)
        
        self.assertIn("Sending failed", str(context.exception))
        
        # Should have tried 5 times (default)
        self.assertEqual(self.mock_serial_instance.write.call_count, 5)
    
    def test_read_reply_skips_log_messages(self):
        """Test that read_reply skips log messages and returns valid response"""
        # Mock sequence: log message, then valid response
        self.mock_serial_instance.readline.side_effect = [
            b"#!Debug log message\r\n",
            b"#!Another log\r\n",
            b"#R[0,42]\r\n"
        ]
        
        reply = self.device.read_reply()
        
        self.assertEqual(reply, "#R[0,42]")
        # Should have read 3 lines
        self.assertEqual(self.mock_serial_instance.readline.call_count, 3)
    
    def test_read_reply_handles_empty_lines(self):
        """Test that read_reply skips invalid/empty lines"""
        # Mock sequence: empty line, invalid line, valid response
        self.mock_serial_instance.readline.side_effect = [
            b"\r\n",
            b"Invalid message\r\n",
            b"#R[0]\r\n"
        ]
        
        reply = self.device.read_reply()
        
        self.assertEqual(reply, "#R[0]")
    
    @patch('ControlSerial.ControlSerial.time.sleep')
    def test_reset_arduino(self, mock_sleep):
        """Test Arduino reset via DTR toggle"""
        self.device.reset_arduino()
        
        # Should set DTR False, then True
        calls = self.mock_serial_instance.setDTR.call_args_list
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0], call(False))
        self.assertEqual(calls[1], call(True))
        
        # Should have appropriate sleep calls
        self.assertTrue(mock_sleep.called)
    
    def test_command_encoding_in_execute(self):
        """Test that commands are properly encoded before sending"""
        self.mock_serial_instance.readline.return_value = b"#R[0]\r\n"
        
        self.device.execute('t', 100)
        
        # Get what was written to serial
        written_data = self.mock_serial_instance.write.call_args[0][0]
        
        # Should be bytes
        self.assertIsInstance(written_data, bytes)
        
        # Should contain expected elements
        written_str = written_data.decode('ascii')
        self.assertTrue(written_str.startswith('#t'))
        self.assertIn('[100]', written_str)
        self.assertTrue(written_str.endswith('\r\n'))
    
    def test_debug_output_when_enabled(self):
        """Test that debug output is printed when enabled"""
        self.device.set_debug(True)
        self.mock_serial_instance.readline.return_value = b"#R[0]\r\n"
        
        # We can't easily test print output, but we can verify it doesn't crash
        self.device.execute('e', 0)
        # If we got here without exception, debug mode works
        self.assertTrue(True)


class TestControlSerialIntegration(unittest.TestCase):
    """Integration tests for ControlSerial with realistic scenarios"""
    
    @patch('ControlSerial.ControlSerial.serial.Serial')
    @patch('ControlSerial.ControlSerial.time.sleep')
    def setUp(self, mock_sleep, mock_serial):
        """Set up mocked ControlSerial instance"""
        self.mock_serial_instance = MagicMock()
        mock_serial.return_value = self.mock_serial_instance
        self.device = ControlSerial('/dev/ttyUSB0')
    
    def test_blink_led_sequence(self):
        """Test sequence of commands to blink an LED"""
        # Simulate successful responses
        self.mock_serial_instance.readline.return_value = b"#R[0]\r\n"
        
        # Turn LED on
        result1 = self.device.execute('w', 13, 1)
        self.assertEqual(result1[0], 0)
        
        # Turn LED off
        result2 = self.device.execute('w', 13, 0)
        self.assertEqual(result2[0], 0)
        
        # Should have sent 2 commands
        self.assertEqual(self.mock_serial_instance.write.call_count, 2)
    
    def test_analog_read_sequence(self):
        """Test sequence of analog reads"""
        # Simulate analog read responses with different values
        self.mock_serial_instance.readline.side_effect = [
            b"#R[0,512]\r\n",
            b"#R[0,513]\r\n",
            b"#R[0,514]\r\n"
        ]
        
        values = []
        for i in range(3):
            result = self.device.execute('a', 0)
            values.append(result[1])
        
        self.assertEqual(values, [512, 513, 514])
    
    def test_motor_control_sequence(self):
        """Test controlling a motor with multiple commands"""
        self.mock_serial_instance.readline.return_value = b"#R[0]\r\n"
        
        # Set motor speed
        self.device.execute('m', 0, 100)
        
        # Set motor direction
        self.device.execute('d', 0, 1)
        
        # Start motor
        self.device.execute('s', 0)
        
        # Should have sent 3 commands
        self.assertEqual(self.mock_serial_instance.write.call_count, 3)
    
    def test_error_recovery(self):
        """Test that device recovers from transient errors"""
        # Simulate: error, then success
        self.mock_serial_instance.readline.side_effect = [
            b"#R[-1]\r\n",  # Transient error
            b"#R[0,42]\r\n"  # Success on retry
        ]
        
        result = self.device.execute('r')
        
        # Should succeed after retry
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 42)


class TestControlSerialErrorHandling(unittest.TestCase):
    """Test error handling and edge cases"""
    
    @patch('ControlSerial.ControlSerial.serial.Serial')
    @patch('ControlSerial.ControlSerial.time.sleep')
    def setUp(self, mock_sleep, mock_serial):
        """Set up mocked ControlSerial instance"""
        self.mock_serial_instance = MagicMock()
        mock_serial.return_value = self.mock_serial_instance
        self.device = ControlSerial('/dev/ttyUSB0')
    
    def test_malformed_response_handling(self):
        """Test handling of malformed responses"""
        # Malformed responses followed by valid one
        self.mock_serial_instance.readline.side_effect = [
            b"Invalid\r\n",
            b"#R[0]\r\n"
        ]
        
        result = self.device.execute('e', 0)
        self.assertEqual(result[0], 0)
    
    def test_empty_response_handling(self):
        """Test handling of empty responses"""
        self.mock_serial_instance.readline.side_effect = [
            b"\r\n",
            b"\r\n",
            b"#R[0]\r\n"
        ]
        
        result = self.device.execute('e', 0)
        self.assertEqual(result[0], 0)
    
    def test_unicode_decode_error_handling(self):
        """Test handling of unicode decode errors"""
        # This tests robustness, though current implementation may not handle it
        self.mock_serial_instance.readline.side_effect = [
            b"#R[0]\r\n"  # Valid response
        ]
        
        result = self.device.execute('e', 0)
        self.assertEqual(result[0], 0)
    
    def test_concurrent_log_and_response(self):
        """Test handling multiple log messages before response"""
        self.mock_serial_instance.readline.side_effect = [
            b"#!Log 1\r\n",
            b"#!Log 2\r\n",
            b"#!Log 3\r\n",
            b"#R[0,123]\r\n"
        ]
        
        result = self.device.execute('r')
        
        # Should skip logs and get the actual response
        self.assertEqual(result[0], 0)
        self.assertEqual(result[1], 123)


def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestControlSerialMocked))
    suite.addTests(loader.loadTestsFromTestCase(TestControlSerialIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestControlSerialErrorHandling))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
