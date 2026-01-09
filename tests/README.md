# ControlSerial Test Suite

This directory contains comprehensive tests for the ControlSerial module.

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── run_tests.py                   # Main test runner
├── test_encoder_decoder.py        # Tests for EnvelopeEncoder and EnvelopeDecoder
├── test_control_serial.py         # Tests for ControlSerial class (mocked)
└── README.md                      # This file
```

## Test Coverage

### test_encoder_decoder.py

Tests for command encoding and response decoding:

- **TestEnvelopeEncoder**: Tests for command encoding
  - Command format validation
  - Opcode validation
  - Argument validation and limits
  - CRC computation
  - Counter increment and wraparound
  - Error handling for invalid inputs

- **TestEnvelopeDecoder**: Tests for response parsing
  - JSON array parsing
  - Valid/invalid message detection
  - Log message detection
  - Multiple value types (int, string, mixed)

- **TestEncoderDecoderIntegration**: Integration tests
  - Round-trip encoding/decoding
  - Command structure validation

- **TestEncoderEdgeCases**: Edge cases and boundary conditions
  - Zero arguments
  - Maximum arguments (12)
  - Special characters in strings
  - Empty strings
  - Large/negative integers

- **TestDecoderEdgeCases**: Decoder edge cases
  - Empty arrays
  - Nested structures
  - Escaped characters

### test_control_serial.py

Tests for the main ControlSerial class with mocked serial communication:

- **TestControlSerialMocked**: Basic functionality tests
  - Initialization
  - Debug mode
  - Command execution
  - Error responses
  - Retry mechanism
  - Log message handling
  - Arduino reset

- **TestControlSerialIntegration**: Realistic usage scenarios
  - LED blink sequences
  - Analog reading
  - Motor control
  - Error recovery

- **TestControlSerialErrorHandling**: Error handling tests
  - Malformed responses
  - Empty responses
  - Concurrent log messages

## Running Tests

### Run All Tests

```bash
# Using the test runner (recommended)
cd ControlSerial
python tests/run_tests.py

# Using individual test files
python tests/test_encoder_decoder.py
python tests/test_control_serial.py

# Using pytest (if installed)
pytest tests/

# Using unittest discover
python -m unittest discover -s tests -p "test_*.py"
```

### Run Specific Test Classes

```bash
python tests/run_tests.py -t TestEnvelopeEncoder
python tests/run_tests.py -t TestControlSerialMocked
```

### Verbosity Options

```bash
# Verbose output (default)
python tests/run_tests.py -v 2

# Normal output
python tests/run_tests.py -v 1

# Quiet output
python tests/run_tests.py -q
```

## Test Requirements

The tests use Python's built-in `unittest` module and `unittest.mock` for mocking serial communication. No additional test dependencies are required beyond the package's normal dependencies:

- pyserial
- crc8

Optional (for enhanced test running):
- pytest (for parallel test execution and better output)
- coverage (for test coverage reporting)

## Installing Test Dependencies

```bash
# Basic dependencies (already in setup.py)
pip install -e .

# Optional test tools
pip install pytest pytest-cov coverage
```

## Test Coverage Report

To generate a coverage report:

```bash
# Using coverage.py
coverage run -m pytest tests/
coverage report
coverage html  # Generate HTML report

# Using pytest with coverage plugin
pytest --cov=ControlSerial --cov-report=html tests/
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest tests/ -v
```

## Writing New Tests

When adding new functionality to ControlSerial, please add corresponding tests:

1. **For encoder/decoder changes**: Add tests to `test_encoder_decoder.py`
2. **For ControlSerial class changes**: Add tests to `test_control_serial.py`
3. **Use mocking**: Mock serial communication to avoid hardware dependencies
4. **Test edge cases**: Include boundary conditions and error cases
5. **Document tests**: Add docstrings explaining what each test verifies

### Example Test Template

```python
def test_new_feature(self):
    """Test description explaining what is being tested"""
    # Setup
    input_data = "test_input"
    
    # Execute
    result = self.device.some_method(input_data)
    
    # Assert
    self.assertEqual(result, expected_value)
    self.assertTrue(some_condition)
```

## Test Philosophy

These tests follow these principles:

1. **Unit tests**: Test individual components in isolation
2. **Mocking**: Use mocks to avoid hardware dependencies
3. **Fast execution**: All tests should complete quickly
4. **Deterministic**: Tests should produce consistent results
5. **Comprehensive**: Cover normal cases, edge cases, and error conditions
6. **Readable**: Clear test names and documentation

## Troubleshooting

### Import Errors

If you encounter import errors:

```bash
# Make sure ControlSerial is installed
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/ControlSerial"
```

### Serial Port Tests

The tests use mocked serial communication, so no physical Arduino or serial port is needed. If you want to test with real hardware:

1. See the `examples/` directory for hardware integration examples
2. Modify device path in examples to match your hardware
3. Use caution with hardware tests in CI/CD pipelines

## Contributing

When contributing tests:

1. Ensure all tests pass before submitting
2. Add tests for new features
3. Maintain or improve code coverage
4. Follow existing test patterns and style
5. Update this README if adding new test files

## License

These tests are part of the ControlSerial project and are licensed under GPL-3.0.

---

**Last Updated**: January 2026
