"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.values import NumericValue, StringValue, ValueType

# C L A S S E S ###############################################################


class TestNumericValue(unittest.TestCase):
    """
    A test class for the NumericValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_numeric_recognizes_valid_hex(self):
        result = NumericValue("$DEAD")
        self.assertEqual("DEAD", result.hex())

    def test_numeric_recognizes_valid_integer(self):
        result = NumericValue("1234")
        self.assertEqual(1234, result.int())

    def test_numeric_raises_exception_on_long_strings(self):
        with self.assertRaises(ValueError) as context:
            NumericValue("$DEADBEEF")
        self.assertEqual("hex value length cannot exceed 4 characters", str(context.exception))

    def test_numeric_raises_exception_on_large_integer(self):
        with self.assertRaises(ValueError) as context:
            NumericValue("65536")
        self.assertEqual("integer value cannot exceed 65535", str(context.exception))

    def test_numeric_raises_exception_on_invalid_strings(self):
        with self.assertRaises(ValueError) as context:
            NumericValue("this is not a valid string")
        self.assertEqual("[this is not a valid string] is neither integer or hex value", str(context.exception))

    def test_numeric_hex_len_correctly_calculated(self):
        result = NumericValue("$DEAD")
        self.assertEqual(4, result.hex_len())

    def test_numeric_byte_len_correctly_calculated(self):
        result = NumericValue("$DEAD")
        self.assertEqual(2, result.byte_len())

    def test_numeric_int_correctly_calculated(self):
        result = NumericValue("$DEAD")
        self.assertEqual(57005, result.int())

    def test_numeric_hex_correctly_calculated(self):
        result = NumericValue("57005")
        self.assertEqual("DEAD", result.hex())

    def test_numeric_str_correct(self):
        result = NumericValue("57005")
        self.assertEqual("DEAD", str(result))

    def test_numeric_is_type_correct(self):
        result = NumericValue("57005")
        self.assertTrue(result.is_type(ValueType.NUMERIC))


class TestStringValue(unittest.TestCase):
    """
    A test class for the StringValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_string_ascii_works_correctly(self):
        result = StringValue('"test string"')
        self.assertEqual("test string", result.ascii())

    def test_string_raises_exception_on_mismatched_delimiters(self):
        with self.assertRaises(ValueError) as context:
            StringValue('"test string')
        self.assertEqual("string must begin and end with same delimiter", str(context.exception))

    def test_string_hex_works_correctly(self):
        result = StringValue('"abc"')
        self.assertEqual("616263", result.hex())

    def test_string_str_works_correctly(self):
        result = StringValue('"abc"')
        self.assertEqual("616263", str(result))

    def test_string_hex_len_works_correctly(self):
        result = StringValue('"abc"')
        self.assertEqual(6, result.hex_len())

    def test_string_byte_len_works_correctly(self):
        result = StringValue('"abc"')
        self.assertEqual(3, result.byte_len())

    def test_string_is_type_correct(self):
        result = StringValue('"abc"')
        self.assertTrue(result.is_type(ValueType.STRING))


# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
