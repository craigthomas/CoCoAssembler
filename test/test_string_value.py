"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.values import StringValue

# C L A S S E S ###############################################################


class TestNumericValue(unittest.TestCase):
    """
    A test class for the StringValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_parse_string_works_correctly(self):
        result = StringValue('"test string"')
        self.assertEqual("test string", result.get_ascii_str())

    def test_parse_string_raises_exception_on_mismatched_delimiters(self):
        with self.assertRaises(ValueError) as context:
            StringValue('"test string')
        self.assertEqual("string must begin and end with same delimiter", str(context.exception))

    def test_get_hex_str_works_correctly(self):
        result = StringValue('"abc"')
        self.assertEqual("616263", result.get_hex_str())

    def test_str_works_correctly(self):
        result = StringValue('"abc"')
        self.assertEqual("616263", str(result))

    def test_get_hex_length_works_correctly(self):
        result = StringValue('"abc"')
        self.assertEqual(6, result.get_hex_length())

    def test_get_hex_byte_size_works_correctly(self):
        result = StringValue('"abc"')
        self.assertEqual(3, result.get_hex_byte_size())

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
