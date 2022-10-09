"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.values import NumericValue, StringValue, NoneValue, SymbolValue, \
    AddressValue, Value, ExpressionValue, ExplicitAddressingMode, LeftRightValue, \
    MultiByteValue, MultiWordValue
from cocoasm.instruction import Instruction, Mode
from cocoasm.exceptions import ValueTypeError

# C L A S S E S ###############################################################


class TestValue(unittest.TestCase):
    """
    A test class for the base Value class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="ABX", mode=Mode(inh=0x3A, inh_sz=1))
        self.fcc_instruction = Instruction(mnemonic="FCC", is_pseudo=True, is_string_define=True)

    def test_value_get_symbol_no_symbol_table_raises(self):
        with self.assertRaises(ValueError) as context:
            Value.get_symbol("blah", {})
        self.assertEqual("[blah] not in symbol table", str(context.exception))

    def test_value_create_from_str_numeric_correct(self):
        result = Value.create_from_str("$DEAD", self.instruction)
        self.assertTrue(result.is_numeric())
        self.assertEqual("DEAD", result.hex())

    def test_value_create_from_str_string_correct(self):
        result = Value.create_from_str("'$DEAD'", self.fcc_instruction)
        self.assertTrue(result.is_string())
        self.assertEqual("$DEAD", result.ascii())

    def test_value_create_from_str_symbol_correct(self):
        result = Value.create_from_str("symbol", self.instruction)
        self.assertTrue(result.is_symbol())

    def test_value_create_from_str_raises_on_bad_string_value(self):
        with self.assertRaises(ValueTypeError) as context:
            Value.create_from_str("'bad string", self.fcc_instruction)
        self.assertEqual("['bad string] is an invalid value", str(context.exception))

    def test_value_create_from_str_raises_on_bad_value(self):
        with self.assertRaises(ValueTypeError) as context:
            Value.create_from_str("invalid!", self.instruction)
        self.assertEqual("[invalid!] is an invalid value", str(context.exception))

    def test_value_high_value_zero_when_length_less_than_two(self):
        result = NumericValue("$0123", size_hint=1)
        self.assertEqual(result.high_byte(), 0x00)

    def test_value_high_value_correct_when_length_is_two(self):
        result = NumericValue("$0123")
        self.assertEqual(result.high_byte(), 0x01)

    def test_value_low_value_zero_when_length_zero(self):
        result = NumericValue("$0123", size_hint=0)
        self.assertEqual(result.low_byte(), 0x00)

    def test_value_low_value_correct_when_length_less_or_equal_to_two(self):
        result = NumericValue("$23")
        self.assertEqual(result.low_byte(), 0x23)

    def test_value_low_value_correct(self):
        result = NumericValue("$1223")
        self.assertEqual(result.low_byte(), 0x23)

    def test_create_from_byte_raises_on_empty_byte(self):
        with self.assertRaises(ValueTypeError) as context:
            Value.create_from_byte(b"")
        self.assertEqual("No byte available for reading", str(context.exception))

    def test_create_from_byte_works_correctly(self):
        result = Value.create_from_byte(b"\xDE\xAD")
        self.assertEqual(result.int, 0xDEAD)

    def test_create_from_string_character_literal_works_correctly(self):
        result = Value.create_from_str("'A")
        self.assertEqual(65, result.int)

    def test_create_from_string_8_bit_immediate_instruction_size_correct(self):
        instruction = Instruction(mnemonic="ZZZ", mode=Mode(imm=0xDE, imm_sz=2))
        result = Value.create_from_str("$01", instruction)
        self.assertEqual(2, result.size_hint)

    def test_create_from_string_16_bit_immediate_instruction_size_correct(self):
        instruction = Instruction(mnemonic="ZZZ", mode=Mode(imm=0xDE, imm_sz=2), is_16_bit=True)
        result = Value.create_from_str("$01", instruction)
        self.assertEqual(4, result.size_hint)

    def test_create_from_string_8_bit_immediate_instruction_size_correct_string_literal(self):
        instruction = Instruction(mnemonic="ZZZ", mode=Mode(imm=0xDE, imm_sz=2))
        result = Value.create_from_str("#'A", instruction)
        self.assertEqual(65, result.int)
        self.assertEqual(2, result.size_hint)

    def test_create_from_string_16_bit_immediate_instruction_size_correct_string_literal(self):
        instruction = Instruction(mnemonic="ZZZ", mode=Mode(imm=0xDE, imm_sz=2), is_16_bit=True)
        result = Value.create_from_str("#'A", instruction)
        self.assertEqual(65, result.int)
        self.assertEqual(4, result.size_hint)


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

    def test_numeric_recognizes_valid_integer_string(self):
        result = NumericValue("1234")
        self.assertEqual(1234, result.int)

    def test_numeric_recognizes_valid_integer(self):
        result = NumericValue(1234)
        self.assertEqual(1234, result.int)

    def test_numeric_raises_exception_on_long_strings(self):
        with self.assertRaises(ValueTypeError) as context:
            NumericValue("$DEADBEEF")
        self.assertEqual("hex value length cannot exceed 4 characters", str(context.exception))

    def test_numeric_raises_exception_on_large_integer_string(self):
        with self.assertRaises(ValueTypeError) as context:
            NumericValue("65536")
        self.assertEqual("integer value cannot exceed 65535", str(context.exception))

    def test_numeric_raises_exception_on_large_integer(self):
        with self.assertRaises(ValueTypeError) as context:
            NumericValue(65536)
        self.assertEqual("integer value cannot exceed 65535", str(context.exception))

    def test_numeric_raises_exception_on_invalid_strings(self):
        with self.assertRaises(ValueTypeError) as context:
            NumericValue("this is not a valid string")
        self.assertEqual(
            "[this is not a valid string] is not valid integer, character literal, or hex value",
            str(context.exception)
        )

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

    def test_numeric_hex_correctly_handles_size_hint_on_constructor(self):
        result = NumericValue("$DEAD", size_hint=6)
        self.assertEqual("00DEAD", result.hex())

    def test_numeric_str_correct(self):
        result = NumericValue("57005")
        self.assertEqual("DEAD", str(result))

    def test_numeric_is_type_correct(self):
        result = NumericValue("57005")
        self.assertTrue(result.is_numeric())

    def test_numeric_hex_len_is_correct(self):
        result = NumericValue("$01")
        self.assertEqual(2, result.hex_len())

    def test_numeric_from_character_literal_word_character_is_correct(self):
        for char_val in range(65, 91):
            result = NumericValue("'{}".format(chr(char_val)))
            self.assertEqual(char_val, result.int)

        for char_val in range(97, 123):
            result = NumericValue("'{}".format(chr(char_val)))
            self.assertEqual(char_val, result.int)

    def test_numeric_from_character_literal_punctuation_is_correct(self):
        for char_val in range(33, 64):
            result = NumericValue("'{}".format(chr(char_val)))
            self.assertEqual(char_val, result.int)

    def test_numeric_from_character_literal_raises_on_invalid_character_literal(self):
        with self.assertRaises(ValueTypeError) as context:
            NumericValue("'~")
        self.assertEqual("['~] is not valid integer, character literal, or hex value", str(context.exception))

    def test_numeric_from_binary_string_is_correct(self):
        result = NumericValue("%10101010")
        self.assertEqual(170, result.int)

    def test_numeric_from_16_bit_binary_string_is_correct(self):
        result = NumericValue("%1010101010101010")
        self.assertEqual(43690, result.int)

    def test_numeric_from_binary_string_throws_exception_when_too_long(self):
        with self.assertRaises(ValueTypeError) as context:
            NumericValue("%10101010101010101")
        self.assertEqual("binary pattern 10101010101010101 must be 8 or 16 bits long", str(context.exception))

    def test_numeric_is_4_bit_zero_value(self):
        result = NumericValue("0")
        self.assertTrue(result.is_4_bit())

    def test_numeric_is_4_bit_max_positive(self):
        result = NumericValue("15")
        self.assertEqual(15, result.int)
        self.assertTrue(result.is_4_bit())

    def test_numeric_is_4_bit_max_negative(self):
        result = NumericValue("-16")
        self.assertTrue(result.is_4_bit())

    def test_numeric_raises_when_negative_too_large(self):
        with self.assertRaises(ValueTypeError):
            NumericValue("-1000000")

    def test_numeric_is_8_bit_correct(self):
        result = NumericValue("127")
        self.assertTrue(result.is_8_bit())
        self.assertFalse(result.is_16_bit())

    def test_numeric_is_16_bit_correct(self):
        result = NumericValue("256")
        self.assertFalse(result.is_8_bit())
        self.assertTrue(result.is_16_bit())

    def test_numeric_negative_string_value_is_negative(self):
        result = NumericValue("-1")
        self.assertTrue(result.is_negative())

    def test_numeric_negative_int_value_is_negative(self):
        result = NumericValue(-1)
        self.assertTrue(result.is_negative())

    def test_numeric_negative_value_get_negative_correct_8_bit(self):
        result = NumericValue("-1")
        self.assertEqual(0xFF, result.get_negative())

    def test_numeric_negative_string_value_get_negative_correct_8_bit(self):
        result = NumericValue("-1")
        self.assertEqual(0xFF, result.get_negative())

    def test_numeric_negative_int_value_get_negative_correct_8_bit(self):
        result = NumericValue(-1)
        self.assertEqual(0xFF, result.get_negative())

    def test_numeric_negative_string_value_get_negative_correct_16_bit(self):
        result = NumericValue("-258")
        self.assertEqual(0xFEFE, result.get_negative())

    def test_numeric_negative_int_value_get_negative_correct_16_bit(self):
        result = NumericValue(-258)
        self.assertEqual(0xFEFE, result.get_negative())


class TestMultiByteValue(unittest.TestCase):
    """
    A test class for the MultiByteValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_multi_byte_raises_on_no_delimiter(self):
        with self.assertRaises(ValueTypeError) as context:
            MultiByteValue('$DE')
        self.assertEqual("multi-byte declarations must have a comma in them", str(context.exception))

    def test_multi_byte_no_values_correct(self):
        result = MultiByteValue(",")
        self.assertEqual("", result.hex())
        self.assertEqual(0, result.hex_len())

    def test_multi_byte_single_value_correct(self):
        result = MultiByteValue("$DE,")
        self.assertEqual("DE", result.hex())
        self.assertEqual(2, result.hex_len())

    def test_multi_byte_many_values_correct(self):
        result = MultiByteValue("$DE,$AD,$BE,$EF")
        self.assertEqual("DEADBEEF", result.hex())
        self.assertEqual(8, result.hex_len())

    def test_multi_byte_8_bit_correct(self):
        result = MultiByteValue("$DE,$AD,$BE,$EF")
        self.assertFalse(result.is_8_bit())

    def test_multi_byte_16_bit_correct(self):
        result = MultiByteValue("$DE,$AD,$BE,$EF")
        self.assertFalse(result.is_16_bit())


class TestMultiWordValue(unittest.TestCase):
    """
    A test class for the StringValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_multi_word_raises_on_no_delimiter(self):
        with self.assertRaises(ValueTypeError) as context:
            MultiWordValue('$DEAD')
        self.assertEqual("multi-word declarations must have a comma in them", str(context.exception))

    def test_multi_word_no_values_correct(self):
        result = MultiWordValue(",")
        self.assertEqual("", result.hex())
        self.assertEqual(0, result.hex_len())

    def test_multi_word_single_value_correct(self):
        result = MultiWordValue("$DEAD,")
        self.assertEqual("DEAD", result.hex())
        self.assertEqual(4, result.hex_len())

    def test_multi_word_many_values_correct(self):
        result = MultiWordValue("$DEAD,$BEEF")
        self.assertEqual("DEADBEEF", result.hex())
        self.assertEqual(8, result.hex_len())

    def test_multi_byte_8_bit_correct(self):
        result = MultiWordValue("$DEAD,$BEEF")
        self.assertFalse(result.is_8_bit())

    def test_multi_byte_16_bit_correct(self):
        result = MultiWordValue("$DEAD,$BEEF")
        self.assertFalse(result.is_16_bit())


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
        with self.assertRaises(ValueTypeError) as context:
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
        self.assertTrue(result.is_string())

    def test_string_is_8_bit_correct(self):
        result = StringValue('"test string"')
        self.assertFalse(result.is_8_bit())

    def test_string_is_16_bit_correct(self):
        result = StringValue('"test string"')
        self.assertFalse(result.is_16_bit())


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
        self.assertTrue(result.is_none())

    def test_none_is_8_bit_correct(self):
        result = NoneValue('"test string"')
        self.assertFalse(result.is_8_bit())

    def test_none_is_16_bit_correct(self):
        result = NoneValue('"test string"')
        self.assertFalse(result.is_16_bit())


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
        with self.assertRaises(ValueTypeError) as context:
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

    def test_symbol_is_8_bit_correct(self):
        result = SymbolValue('symbol')
        self.assertFalse(result.is_8_bit())

    def test_symbol_is_16_bit_correct(self):
        result = SymbolValue('symbol')
        self.assertFalse(result.is_16_bit())


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

    def test_address_byte_len_correct(self):
        result = AddressValue('16')
        self.assertEqual(1, result.byte_len())

    def test_address_is_8_bit_correct(self):
        result = AddressValue('16')
        self.assertFalse(result.is_8_bit())

    def test_address_is_16_bit_correct(self):
        result = AddressValue('16')
        self.assertTrue(result.is_16_bit())


class TestLeftRightValue(unittest.TestCase):
    """
    A test class for the LeftRightValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_left_right_hex_correct(self):
        result = LeftRightValue('test,string')
        self.assertEqual("", result.hex())

    def test_left_right_parse_correct(self):
        result = LeftRightValue('test,string')
        self.assertEqual("test", result.left)
        self.assertEqual("string", result.right)

    def test_left_right_hex_len_correct(self):
        result = LeftRightValue('test,string')
        self.assertEqual(0, result.hex_len())

    def test_left_right_is_8_bit_correct(self):
        result = LeftRightValue('test,string')
        self.assertFalse(result.is_8_bit())

    def test_left_right_is_16_bit_correct(self):
        result = LeftRightValue('test,string')
        self.assertFalse(result.is_16_bit())


class TestExpressionValue(unittest.TestCase):
    """
    A test class for the ExpressionValue class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_expression_resolve_numeric_only_addition_works_correctly(self):
        result = ExpressionValue("2+3")
        result = result.resolve(None)
        self.assertEqual(result.int, 5)

    def test_expression_resolve_numeric_only_multiplication_works_correctly(self):
        result = ExpressionValue("2*3")
        result = result.resolve(None)
        self.assertEqual(result.int, 6)

    def test_expression_resolve_numeric_only_subtraction_works_correctly(self):
        result = ExpressionValue("3-2")
        result = result.resolve(None)
        self.assertEqual(result.int, 1)

    def test_expression_resolve_numeric_only_division_works_correctly(self):
        result = ExpressionValue("4/2")
        result = result.resolve(None)
        self.assertEqual(result.int, 2)

    def test_expression_hex_returns_zero_if_not_resolved(self):
        result = ExpressionValue("2+3")
        self.assertEqual(result.hex(), "00")

    def test_expression_hex_len_returns_zero_if_not_resolved(self):
        result = ExpressionValue("2+3")
        self.assertEqual(result.hex_len(), 0)

    def test_expression_hex_returns_correct_when_resolved(self):
        result = ExpressionValue("254+1")
        result = result.resolve(None)
        self.assertEqual(result.hex(), "FF")

    def test_expression_hex_len_returns_correct_when_resolved(self):
        result = ExpressionValue("254+1")
        result = result.resolve(None)
        self.assertEqual(result.hex_len(), 2)

    def test_expression_symbol_right_resolves_correctly(self):
        symbol_table = {"VAR": NumericValue("$FE", mode=ExplicitAddressingMode.DIRECT)}
        result = ExpressionValue("1+VAR")
        result = result.resolve(symbol_table)
        self.assertEqual(result.hex(), "FF")

    def test_expression_symbol_left_resolves_correctly(self):
        symbol_table = {"VAR": NumericValue("$FE", mode=ExplicitAddressingMode.DIRECT)}
        result = ExpressionValue("VAR+1")
        result = result.resolve(symbol_table)
        self.assertEqual(result.hex(), "FF")

    def test_expression_resolve_symbol_addition_works_correctly(self):
        symbol_table = {"VAR": NumericValue("$02", mode=ExplicitAddressingMode.DIRECT)}
        result = ExpressionValue("VAR+3")
        result = result.resolve(symbol_table)
        self.assertEqual(result.int, 5)

    def test_expression_resolve_symbol_multiplication_works_correctly(self):
        symbol_table = {"VAR": NumericValue("$02", mode=ExplicitAddressingMode.DIRECT)}
        result = ExpressionValue("VAR*3")
        result = result.resolve(symbol_table)
        self.assertEqual(result.int, 6)

    def test_expression_resolve_symbol_subtraction_works_correctly(self):
        symbol_table = {"VAR": NumericValue("$03", mode=ExplicitAddressingMode.DIRECT)}
        result = ExpressionValue("VAR-2")
        result = result.resolve(symbol_table)
        self.assertEqual(result.int, 1)

    def test_expression_resolve_symbol_plus_numeric_division_works_correctly(self):
        symbol_table = {"VAR": NumericValue("$04", mode=ExplicitAddressingMode.DIRECT)}
        result = ExpressionValue("VAR/2")
        result = result.resolve(symbol_table)
        self.assertEqual(result.int, 2)

    def test_expression_raises_when_not_numeric_or_address_for_resolve(self):
        result = ExpressionValue("VAR+1")
        result.left = NoneValue()
        with self.assertRaises(ValueError) as context:
            result.resolve({})
        self.assertEqual("[VAR+1] unresolved expression", str(context.exception))

    def test_expression_left_extended_correct(self):
        result = ExpressionValue("$FFEE+1")
        self.assertTrue(result.is_extended())

    def test_expression_right_extended_correct(self):
        result = ExpressionValue("1+$FFEE")
        self.assertTrue(result.is_extended())

    def test_expression_is_8_bit_correct(self):
        result = ExpressionValue("$FFEE+1")
        self.assertFalse(result.is_8_bit())

    def test_expression_is_16_bit_correct(self):
        result = ExpressionValue("$FFEE+1")
        self.assertFalse(result.is_16_bit())


# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
