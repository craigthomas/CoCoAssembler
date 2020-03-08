"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.value import Value

# C L A S S E S ###############################################################


class TestInstructionBundle(unittest.TestCase):
    """
    A test class for the InstructionBundle class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_parse_input_recognizes_valid_hex(self):
        result = Value("$DEAD")
        self.assertEqual("DEAD", result.get_hex_str())

    def test_parse_input_recognizes_valid_integer(self):
        result = Value("1234")
        self.assertEqual(1234, result.get_integer())

    def test_parse_input_raises_exception_on_long_strings(self):
        with self.assertRaises(ValueError) as context:
            Value("$DEADBEEF")
        self.assertEqual("hex value length cannot exceed 4 characters", str(context.exception))

    def test_parse_input_raises_exception_on_large_integer(self):
        with self.assertRaises(ValueError) as context:
            Value("65536")
        self.assertEqual("integer value cannot exceed 65535", str(context.exception))

    def test_parse_input_raises_exception_on_invalid_strings(self):
        with self.assertRaises(ValueError) as context:
            Value("this is not a valid string")
        self.assertEqual("supplied value is neither integer or hex value", str(context.exception))

    def test_get_hex_length_correctly_calculated(self):
        result = Value("$DEAD")
        self.assertEqual(4, result.get_hex_length())

    def test_get_hex_byte_size_correctly_calculated(self):
        result = Value("$DEAD")
        self.assertEqual(2, result.get_hex_byte_size())

    def test_integer_value_correctly_calculated(self):
        result = Value("$DEAD")
        self.assertEqual(57005, result.get_integer())

    def test_hex_value_correctly_calculated(self):
        result = Value("57005")
        self.assertEqual("DEAD", result.get_hex_str())

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
