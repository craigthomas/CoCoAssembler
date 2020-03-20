"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.values import NumericValue, StringValue, NoneValue, SymbolValue, \
    AddressValue, ValueType, Value


# C L A S S E S ###############################################################


class TestValue(unittest.TestCase):
    """
    A test class for the base Value class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_value_create_from_str_numeric_correct(self):
        result = Value.create_from_str("$DEAD", "")
        self.assertTrue(result.is_type(ValueType.NUMERIC))
        self.assertEqual("DEAD", result.hex())

    def test_value_create_from_str_string_correct(self):
        result = Value.create_from_str("'$DEAD'", "FCC")
        self.assertTrue(result.is_type(ValueType.STRING))
        self.assertEqual("$DEAD", result.ascii())

    def test_value_create_from_str_symbol_correct(self):
        result = Value.create_from_str("symbol", "")
        self.assertTrue(result.is_type(ValueType.SYMBOL))

    def test_value_create_from_str_raises_on_bad_value(self):
        with self.assertRaises(ValueError) as context:
            Value.create_from_str("invalid!", "")
        self.assertEqual("[invalid!] is an invalid value", str(context.exception))


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
        self.assertEqual(1234, result.int)

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
        self.assertEqual(57005, result.int)

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


class TestNoneValue(unittest.TestCase):
    """
    A test class for the NoneValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_none_ascii_works_correctly(self):
        result = NoneValue('"test string"')
        self.assertEqual("", result.ascii())

    def test_none_hex_works_correctly(self):
        result = NoneValue('"abc"')
        self.assertEqual("", result.hex())

    def test_none_str_works_correctly(self):
        result = NoneValue('"abc"')
        self.assertEqual("", str(result))

    def test_none_hex_len_works_correctly(self):
        result = NoneValue('"abc"')
        self.assertEqual(0, result.hex_len())

    def test_none_byte_len_works_correctly(self):
        result = NoneValue('"abc"')
        self.assertEqual(0, result.byte_len())

    def test_none_is_type_correct(self):
        result = NoneValue('"abc"')
        self.assertTrue(result.is_type(ValueType.NONE))


class TestSymbolValue(unittest.TestCase):
    """
    A test class for the SymbolValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_symbol_raises_exception_on_invalid_strings(self):
        with self.assertRaises(ValueError) as context:
            SymbolValue("invalid!")
        self.assertEqual("[invalid!] is not a valid symbol", str(context.exception))

    def test_symbol_ascii_works_correctly(self):
        result = SymbolValue('symbol')
        self.assertEqual("symbol", result.ascii())

    def test_symbol_hex_empty_when_not_resolved(self):
        result = SymbolValue('symbol')
        self.assertFalse(result.resolved)
        self.assertEqual("", result.hex())

    def test_symbol_hex_correct_when_resolved(self):
        result = SymbolValue('symbol')
        result.resolved = True
        result.value = NumericValue("$AB")
        self.assertEqual("AB", result.hex())

    def test_symbol_str_empty_when_not_resolved(self):
        result = SymbolValue('symbol')
        self.assertFalse(result.resolved)
        self.assertEqual("", str(result))

    def test_symbol_str_correct_when_resolved(self):
        result = SymbolValue('symbol')
        result.resolved = True
        result.value = NumericValue("$AB")
        self.assertEqual("AB", str(result))

    def test_symbol_hex_len_zero_when_not_resolved(self):
        result = SymbolValue('symbol')
        self.assertFalse(result.resolved)
        self.assertEqual(0, result.hex_len())

    def test_symbol_hex_len_correct_when_resolved(self):
        result = SymbolValue('symbol')
        result.resolved = True
        result.value = NumericValue("$AB")
        self.assertEqual(2, result.hex_len())

    def test_symbol_byte_len_zero_when_not_resolved(self):
        result = SymbolValue('symbol')
        self.assertFalse(result.resolved)
        self.assertEqual(0, result.byte_len())

    def test_symbol_byte_len_correct_when_resolved(self):
        result = SymbolValue('symbol')
        result.resolved = True
        result.value = NumericValue("$AB")
        self.assertEqual(1, result.byte_len())


class TestAddressValue(unittest.TestCase):
    """
    A test class for the AddressValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_address_ascii_works_correctly(self):
        result = AddressValue('11')
        self.assertEqual("11", result.ascii())

    def test_address_hex_correct(self):
        result = AddressValue('16')
        self.assertEqual("10", result.hex())

    def test_address_str_correct(self):
        result = AddressValue('16')
        self.assertEqual("10", str(result))

    def test_address_hex_len_correct(self):
        result = AddressValue('16')
        self.assertEqual(2, result.hex_len())

    def test_symbol_byte_len_correct(self):
        result = AddressValue('16')
        self.assertEqual(1, result.byte_len())

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
