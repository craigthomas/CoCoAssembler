"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.operands import UnknownOperand, InherentOperand, ImmediateOperand, \
    OperandType, IndexedOperand, RelativeOperand, ExtendedIndexedOperand, \
    Operand, ExtendedOperand, PseudoOperand, SpecialOperand, DirectOperand, \
    BadInstructionOperand
from cocoasm.instruction import Instruction, Mode
from cocoasm.values import NumericValue, AddressValue, ValueType
from cocoasm.exceptions import OperandTypeError

# C L A S S E S ###############################################################


class TestBaseOperand(unittest.TestCase):
    """
    A test class for the base Operand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_base_operand_create_from_str_returns_relative(self):
        instruction = Instruction(mnemonic="BEQ", mode=Mode(rel=0x27, rel_sz=2), is_short_branch=True)
        operand = Operand.create_from_str("$1F", instruction)
        self.assertTrue(operand.is_relative())

    def test_base_operand_create_from_str_returns_inherent(self):
        instruction = Instruction(mnemonic="SWI3", mode=Mode(inh=0x113F, inh_sz=2))
        operand = Operand.create_from_str("", instruction)
        self.assertTrue(operand.is_inherent())

    def test_base_operand_create_from_str_returns_immediate(self):
        instruction = Instruction(mnemonic="ORCC", mode=Mode(imm=0x1A, imm_sz=2))
        operand = Operand.create_from_str("#$01", instruction)
        self.assertTrue(operand.is_immediate())

    def test_base_operand_create_from_str_returns_extended_indexed(self):
        instruction = Instruction(mnemonic="ROL", mode=Mode(ind=0x69, ind_sz=2))
        operand = Operand.create_from_str("[$2000]", instruction)
        self.assertTrue(operand.is_extended_indexed())

    def test_base_operand_create_from_str_returns_indexed(self):
        instruction = Instruction(mnemonic="ROL", mode=Mode(ind=0x69, ind_sz=2))
        operand = Operand.create_from_str(",X+", instruction)
        self.assertTrue(operand.is_indexed())

    def test_base_operand_create_from_str_returns_expression(self):
        instruction = Instruction(mnemonic="ROL", mode=Mode(ind=0x69, ind_sz=2))
        operand = Operand.create_from_str("VAL+1", instruction)
        self.assertTrue(operand.value.is_expression())

    def test_base_operand_create_from_str_returns_unknown(self):
        instruction = Instruction(mnemonic="ROL", mode=Mode(ind=0x69, ind_sz=2))
        operand = Operand.create_from_str("VAL", instruction)
        self.assertTrue(operand.is_unknown())

    def test_base_operand_create_from_str_raises(self):
        instruction = Instruction(mnemonic="ROL", mode=Mode(ind=0x69, ind_sz=2))
        with self.assertRaises(OperandTypeError) as context:
            Operand.create_from_str(",blah,", instruction)
        self.assertEqual("[,blah,] unknown operand type", str(context.exception))

    def test_base_resolve_symbols_returns_self_if_not_symbol(self):
        instruction = Instruction(mnemonic="SUBA", mode=Mode(ext=0xB0, ext_sz=3))
        operand = ExtendedOperand("$FFFF", instruction)
        result = operand.resolve_symbols({})
        self.assertEqual(OperandType.EXTENDED, result.type)
        self.assertEqual("FFFF", result.value.hex())

    def test_base_resolve_symbols_returns_direct_symbol(self):
        symbol_table = {
            "BLAH": NumericValue("$FF")
        }
        instruction = Instruction(mnemonic="SUBA", mode=Mode(ext=0xB0, ext_sz=3))
        operand = UnknownOperand("BLAH", instruction)
        result = operand.resolve_symbols(symbol_table=symbol_table)
        self.assertEqual(OperandType.DIRECT, result.type)
        self.assertEqual("FF", result.value.hex())

    def test_base_resolve_symbols_returns_extended_symbol(self):
        symbol_table = {
            "BLAH": NumericValue("$FFFF")
        }
        instruction = Instruction(mnemonic="SUBA", mode=Mode(ext=0xB0, ext_sz=3))
        operand = UnknownOperand("BLAH", instruction)
        result = operand.resolve_symbols(symbol_table=symbol_table)
        self.assertEqual(OperandType.EXTENDED, result.type)
        self.assertEqual("FFFF", result.value.hex())

    def test_base_resolve_symbols_returns_extended_for_address_value(self):
        symbol_table = {
            "BLAH": AddressValue(2)
        }
        instruction = Instruction(mnemonic="SUBA", mode=Mode(ext=0xB0, ext_sz=3))
        operand = UnknownOperand("BLAH", instruction)
        result = operand.resolve_symbols(symbol_table=symbol_table)
        self.assertEqual(OperandType.EXTENDED, result.type)
        self.assertEqual(2, result.value.int)

    def test_base_resolve_symbols_returns_self_for_address_value(self):
        symbol_table = {
            "BLAH": AddressValue(2)
        }
        instruction = Instruction(mnemonic="SUBA", mode=Mode(ext=0xB0, ext_sz=3), is_short_branch=True)
        operand = RelativeOperand("BLAH", instruction)
        result = operand.resolve_symbols(symbol_table=symbol_table)
        self.assertEqual(OperandType.RELATIVE, result.type)
        self.assertEqual(2, result.value.int)


class TestBadInstructionOperand(unittest.TestCase):
    """
    A test class for the BadInstructionOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_bad_instruction_operand_translate_returns_empty_code_package(self):
        result = BadInstructionOperand("$FF", None)
        code_pkg = result.translate()
        self.assertTrue(code_pkg.op_code.is_none())
        self.assertTrue(code_pkg.address.is_none())
        self.assertTrue(code_pkg.post_byte.is_none())
        self.assertTrue(code_pkg.additional.is_none())
        self.assertEqual(code_pkg.size, 0)
        self.assertFalse(code_pkg.additional_needs_resolution)

    def test_bad_instruction_operand_instantiates_to_strings(self):
        result = BadInstructionOperand("string", None)
        self.assertEqual(result.operand_string, "string")
        self.assertEqual(result.original_operand, "string")


class TestUnknownOperand(unittest.TestCase):
    """
    A test class for the UnknownOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="ABX", mode=Mode(inh=0x3A, inh_sz=1))
        self.fcc_instruction = Instruction(mnemonic="FCC", is_pseudo=True, is_string_define=True)

    def test_unknown_type_correct(self):
        result = UnknownOperand("blah", self.instruction)
        self.assertTrue(result.is_unknown())

    def test_unknown_string_correct(self):
        result = UnknownOperand("blah", self.fcc_instruction)
        self.assertEqual("blah", result.operand_string)

    def test_unknown_value_correct(self):
        result = UnknownOperand("$FF", self.instruction)
        self.assertEqual("FF", result.value.hex())

    def test_unknown_translate_result_correct(self):
        operand = UnknownOperand(None, self.instruction, value="FF")
        result = operand.translate()
        self.assertEqual(0, result.op_code.int)
        self.assertEqual("FF", result.additional)
        self.assertEqual(0, result.post_byte.int)
        self.assertEqual(0, result.size)

    def test_unknown_raises_on_bad_operand(self):
        with self.assertRaises(OperandTypeError) as context:
            UnknownOperand("\\bad", self.instruction)
        self.assertEqual("[\\bad] unknown operand type", str(context.exception))


class TestRelativeOperand(unittest.TestCase):
    """
    A test class for the RelativeOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="BEQ", mode=Mode(rel=0x3A, rel_sz=2), is_short_branch=True)

    def test_relative_type_correct(self):
        result = RelativeOperand("$FF", self.instruction)
        self.assertTrue(result.is_relative())

    def test_relative_raises_if_instruction_not_branch(self):
        instruction = Instruction(mnemonic="BEQ", mode=Mode(rel=0x3A, rel_sz=1))
        with self.assertRaises(OperandTypeError) as context:
            RelativeOperand("$FF", instruction)
        self.assertEqual("[BEQ] is not a branch instruction", str(context.exception))

    def test_relative_translate_correct(self):
        instruction = Instruction(mnemonic="BEQ", mode=Mode(rel=0x3A, rel_sz=1), is_short_branch=True)
        operand = RelativeOperand("$FF", instruction)
        operand.value = AddressValue(0xFFEE)
        result = operand.translate()
        self.assertEqual("3A", result.op_code.hex())
        self.assertEqual(1, result.size)
        self.assertEqual("FFEE", result.additional.hex())


class TestPseudoOperand(unittest.TestCase):
    """
    A test class for the PseudoOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="PSU", mode=Mode(rel=0x3A, rel_sz=2), is_pseudo=True)

    def test_pseudo_type_correct(self):
        result = PseudoOperand("$FF", self.instruction)
        self.assertTrue(result.is_pseudo())

    def test_pseudo_raises_if_instruction_not_pseudo(self):
        instruction = Instruction(mnemonic="BEQ", mode=Mode(rel=0x3A, rel_sz=1))
        with self.assertRaises(OperandTypeError) as context:
            PseudoOperand("$FF", instruction)
        self.assertEqual("[BEQ] is not a pseudo instruction", str(context.exception))

    def test_pseudo_translate_returns_empty_code_package_on_non_defined_instruction(self):
        instruction = Instruction(mnemonic="BEQ", mode=Mode(rel=0x3A, rel_sz=1))
        with self.assertRaises(OperandTypeError) as context:
            PseudoOperand("$FF", instruction)
        self.assertEqual("[BEQ] is not a pseudo instruction", str(context.exception))

    def test_pseudo_translate_fcb(self):
        instruction = Instruction(mnemonic="FCB", is_pseudo=True)
        operand = PseudoOperand("$FF", instruction)
        code_pkg = operand.translate()
        self.assertEqual("FF", code_pkg.additional.hex())

    def test_pseudo_translate_fdb(self):
        instruction = Instruction(mnemonic="FDB", is_pseudo=True)
        operand = PseudoOperand("$FFCC", instruction)
        code_pkg = operand.translate()
        self.assertEqual("FFCC", code_pkg.additional.hex())

    def test_pseudo_translate_rmb(self):
        instruction = Instruction(mnemonic="RMB", is_pseudo=True)
        operand = PseudoOperand("$10", instruction)
        code_pkg = operand.translate()
        self.assertEqual("00000000000000000000000000000000", code_pkg.additional.hex())

    def test_pseudo_translate_org(self):
        instruction = Instruction(mnemonic="ORG", is_pseudo=True)
        operand = PseudoOperand("$FFCC", instruction)
        code_pkg = operand.translate()
        self.assertEqual("FFCC", code_pkg.address.hex())

    def test_pseudo_translate_fcc(self):
        instruction = Instruction(mnemonic="FCC", is_pseudo=True, is_string_define=True)
        operand = PseudoOperand('"hello"', instruction)
        code_pkg = operand.translate()
        self.assertEqual("68656C6C6F", code_pkg.additional.hex())


class TestSpecialOperand(unittest.TestCase):
    """
    A test class for the SpecialOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="PSHS", mode=Mode(rel=0x3A, rel_sz=2), is_special=True)

    def test_special_type_correct(self):
        result = SpecialOperand("$FF", self.instruction)
        self.assertTrue(result.is_special())

    def test_special_raises_if_instruction_not_special(self):
        instruction = Instruction(mnemonic="BEQ", mode=Mode(rel=0x3A, rel_sz=1))
        with self.assertRaises(OperandTypeError) as context:
            SpecialOperand("$FF", instruction)
        self.assertEqual("[BEQ] is not a special instruction", str(context.exception))

    def test_special_code_pkg_result_not_tfr_exg_pshs_puls(self):
        instruction = Instruction(mnemonic="BLAH", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("$FF", instruction)
        code_pkg = operand.translate()
        self.assertEqual("3A", code_pkg.op_code.hex())
        self.assertEqual(1, code_pkg.size)
        self.assertEqual("00", code_pkg.post_byte.hex())

    def test_special_pshs_raises_with_bad_register(self):
        instruction = Instruction(mnemonic="PSHS", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("not_a_register", instruction)
        with self.assertRaises(OperandTypeError) as context:
            operand.translate()
        self.assertEqual("[not_a_register] unknown register", str(context.exception))

    def test_special_pshs_raises_with_no_register(self):
        instruction = Instruction(mnemonic="PSHS", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("", instruction)
        with self.assertRaises(OperandTypeError) as context:
            operand.translate()
        self.assertEqual("one or more registers must be specified", str(context.exception))

    def test_special_pshs_correct_with_register_values(self):
        instruction = Instruction(mnemonic="PSHS", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("D", instruction)
        code_pkg = operand.translate()
        self.assertEqual("06", code_pkg.post_byte.hex())

        operand = SpecialOperand("CC", instruction)
        code_pkg = operand.translate()
        self.assertEqual("01", code_pkg.post_byte.hex())

        operand = SpecialOperand("A", instruction)
        code_pkg = operand.translate()
        self.assertEqual("02", code_pkg.post_byte.hex())

        operand = SpecialOperand("B", instruction)
        code_pkg = operand.translate()
        self.assertEqual("04", code_pkg.post_byte.hex())

        operand = SpecialOperand("DP", instruction)
        code_pkg = operand.translate()
        self.assertEqual("08", code_pkg.post_byte.hex())

        operand = SpecialOperand("X", instruction)
        code_pkg = operand.translate()
        self.assertEqual("10", code_pkg.post_byte.hex())

        operand = SpecialOperand("Y", instruction)
        code_pkg = operand.translate()
        self.assertEqual("20", code_pkg.post_byte.hex())

        operand = SpecialOperand("U", instruction)
        code_pkg = operand.translate()
        self.assertEqual("40", code_pkg.post_byte.hex())

        operand = SpecialOperand("PC", instruction)
        code_pkg = operand.translate()
        self.assertEqual("80", code_pkg.post_byte.hex())

    def test_special_pshs_correct_with_multiple_register_values(self):
        instruction = Instruction(mnemonic="PSHS", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("CC,D,X,Y", instruction)
        code_pkg = operand.translate()
        self.assertEqual("37", code_pkg.post_byte.hex())

    def test_special_exg_raises_with_one_register(self):
        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("A", instruction)
        with self.assertRaises(OperandTypeError) as context:
            operand.translate()
        self.assertEqual("[EXG] requires exactly 2 registers", str(context.exception))

    def test_special_exg_raises_with_three_registers(self):
        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("A,B,X", instruction)
        with self.assertRaises(OperandTypeError) as context:
            operand.translate()
        self.assertEqual("[EXG] requires exactly 2 registers", str(context.exception))

    def test_special_exg_raises_with_bad_register_first_reg(self):
        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("not_a_register,A", instruction)
        with self.assertRaises(OperandTypeError) as context:
            operand.translate()
        self.assertEqual("[not_a_register] unknown register", str(context.exception))

    def test_special_exg_raises_with_bad_register_second_reg(self):
        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("A,not_a_register", instruction)
        with self.assertRaises(OperandTypeError) as context:
            operand.translate()
        self.assertEqual("[not_a_register] unknown register", str(context.exception))

    def test_special_exg_raises_with_A_to_D(self):
        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("A,D", instruction)
        with self.assertRaises(OperandTypeError) as context:
            operand.translate()
        self.assertEqual("[EXG] of [A] to [D] not allowed", str(context.exception))

    def test_special_exg_works_self_to_self(self):
        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("A,A", instruction)
        result = operand.translate()
        self.assertEqual("88", result.post_byte.hex())

        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("B,B", instruction)
        result = operand.translate()
        self.assertEqual("99", result.post_byte.hex())

        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("CC,CC", instruction)
        result = operand.translate()
        self.assertEqual("AA", result.post_byte.hex())

        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("DP,DP", instruction)
        result = operand.translate()
        self.assertEqual("BB", result.post_byte.hex())

        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("D,D", instruction)
        result = operand.translate()
        self.assertEqual("00", result.post_byte.hex())

        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("X,X", instruction)
        result = operand.translate()
        self.assertEqual("11", result.post_byte.hex())

        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("Y,Y", instruction)
        result = operand.translate()
        self.assertEqual("22", result.post_byte.hex())

        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("U,U", instruction)
        result = operand.translate()
        self.assertEqual("33", result.post_byte.hex())

        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("S,S", instruction)
        result = operand.translate()
        self.assertEqual("44", result.post_byte.hex())

        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("PC,PC", instruction)
        result = operand.translate()
        self.assertEqual("55", result.post_byte.hex())

    def test_special_resolve_symbols_returns_same(self):
        instruction = Instruction(mnemonic="EXG", mode=Mode(imm=0x3A, imm_sz=1), is_special=True)
        operand = SpecialOperand("A,A", instruction)
        result = operand.resolve_symbols({})
        self.assertEqual(operand.operand_string, result.operand_string)
        self.assertEqual(operand.type, result.type)


class TestInherentOperand(unittest.TestCase):
    """
    A test class for the InherentOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="STX", mode=Mode(inh=0xAF, inh_sz=1))

    def test_inherent_type_correct(self):
        result = InherentOperand(None, self.instruction)
        self.assertTrue(result.is_inherent())

    def test_inherent_string_correct(self):
        result = InherentOperand(None, self.instruction)
        self.assertEqual("", result.operand_string)

    def test_inherent_raises_with_value(self):
        with self.assertRaises(OperandTypeError) as context:
            InherentOperand("$FF", self.instruction)
        self.assertEqual("[$FF] is not an inherent value", str(context.exception))

    def test_inherent_raises_with_value_passthrough(self):
        value = NumericValue("$FF")
        with self.assertRaises(OperandTypeError) as context:
            InherentOperand(None, self.instruction, value=value)
        self.assertEqual("[$FF] is not an inherent value", str(context.exception))

    def test_inherent_raises_with_bad_instruction_on_translate(self):
        instruction = Instruction(mnemonic="STX", mode=Mode(imm=0xAF, imm_sz=1))
        with self.assertRaises(OperandTypeError) as context:
            result = InherentOperand(None, instruction)
            result.translate()
        self.assertEqual("Instruction [STX] requires an operand", str(context.exception))

    def test_inherent_translate_result_correct(self):
        operand = InherentOperand(None, self.instruction)
        result = operand.translate()
        self.assertEqual("AF", result.op_code.hex())
        self.assertEqual(1, result.size)


class TestImmediateOperand(unittest.TestCase):
    """
    A test class for the ImmediateOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="ABX", mode=Mode(imm=0x3A, imm_sz=2))

    def test_immediate_type_correct(self):
        result = ImmediateOperand("#blah", self.instruction)
        self.assertTrue(result.is_immediate())

    def test_immediate_string_correct(self):
        result = ImmediateOperand("#blah", self.instruction)
        self.assertEqual("#blah", result.operand_string)

    def test_immediate_raises_with_bad_value(self):
        with self.assertRaises(OperandTypeError) as context:
            ImmediateOperand("blah", self.instruction)
        self.assertEqual("[blah] is not an immediate value", str(context.exception))

    def test_immediate_value_correct(self):
        result = ImmediateOperand("#$FF", self.instruction)
        self.assertEqual("FF", result.value.hex())

    def test_immediate_value_passthrough_correct(self):
        result = ImmediateOperand("#$FF", self.instruction, value="test")
        self.assertEqual("test", result.value)

    def test_immediate_raises_with_bad_instruction_on_translate(self):
        instruction = Instruction(mnemonic="STX", mode=Mode(inh=0xAF, inh_sz=1))
        with self.assertRaises(OperandTypeError) as context:
            result = ImmediateOperand("#$FF", instruction)
            result.translate()
        self.assertEqual("Instruction [STX] does not support immediate addressing", str(context.exception))

    def test_immediate_translate_result_correct(self):
        operand = ImmediateOperand("#$FF", self.instruction)
        result = operand.translate()
        self.assertEqual("3A", result.op_code.hex())
        self.assertEqual("FF", result.additional.hex())
        self.assertEqual(2, result.size)

    def test_immediate_resolve_symbols_not_symbol(self):
        operand = ImmediateOperand("#$FF", self.instruction)
        result = operand.resolve_symbols({})
        self.assertEqual(ValueType.NUMERIC, result.value.type)

    def test_immediate_resolve_symbols_correct(self):
        symbol_table = {
            "BLAH": NumericValue(2)
        }
        operand = ImmediateOperand("#BLAH", self.instruction)
        result = operand.resolve_symbols(symbol_table=symbol_table)
        self.assertEqual("02", result.value.hex())

    def test_immediate_character_literal_correct(self):
        operand = ImmediateOperand("#'A", self.instruction)
        result = operand.translate()
        self.assertEqual(0x3A, result.op_code.int)
        self.assertEqual(65, result.additional.int)

    def test_immediate_character_literal_punctuation_correct(self):
        operand = ImmediateOperand("#'>", self.instruction)
        result = operand.translate()
        self.assertEqual(0x3A, result.op_code.int)
        self.assertEqual(62, result.additional.int)


class TestIndexedOperand(unittest.TestCase):
    """
    A test class for the IndexedOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="STX", mode=Mode(ind=0xAF, ind_sz=2))

    def test_indexed_type_correct(self):
        result = IndexedOperand(",X", self.instruction)
        self.assertTrue(result.is_indexed())

    def test_indexed_string_correct(self):
        result = IndexedOperand(",X", self.instruction)
        self.assertEqual(",X", result.operand_string)

    def test_indexed_raises_with_bad_value(self):
        with self.assertRaises(OperandTypeError) as context:
            IndexedOperand(",blah,", self.instruction)
        self.assertEqual("[,blah,] is not an indexed value", str(context.exception))

    def test_indexed_raises_with_no_commas(self):
        with self.assertRaises(OperandTypeError) as context:
            IndexedOperand("blah", self.instruction)
        self.assertEqual("[blah] is not an indexed value", str(context.exception))

    def test_indexed_raises_with_instruction_that_does_not_support_indexed(self):
        instruction = Instruction(mnemonic="STX", mode=Mode(inh=0x1F, inh_sz=1))
        with self.assertRaises(OperandTypeError) as context:
            operand = IndexedOperand(",X", instruction)
            operand.translate()
        self.assertEqual("Instruction [STX] does not support indexed addressing", str(context.exception))

    def test_indexed_no_offset_correct_values(self):
        operand = IndexedOperand(",X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("84", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand(",Y", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("A4", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand(",U", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("C4", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand(",S", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("E4", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_indexed_A_offset_correct_values(self):
        operand = IndexedOperand("A,X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("86", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("A,Y", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("A6", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("A,U", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("C6", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("A,S", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("E6", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_indexed_B_offset_correct_values(self):
        operand = IndexedOperand("B,X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("85", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("B,Y", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("A5", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("B,U", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("C5", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("B,S", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("E5", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_indexed_D_offset_correct_values(self):
        operand = IndexedOperand("D,X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("8B", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("D,Y", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("AB", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("D,U", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("CB", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("D,S", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("EB", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_indexed_auto_increments_correct_values(self):
        operand = IndexedOperand(",X+", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("80", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand(",X++", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("81", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand(",-X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("82", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand(",--X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("83", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_indexed_offset_from_register_with_auto_increment_raises(self):
        with self.assertRaises(OperandTypeError) as context:
            operand = IndexedOperand("$1F,X+", self.instruction)
            operand.translate()
        self.assertEqual("[$1F,X+] invalid indexed expression", str(context.exception))

    def test_indexed_4_bit_value_correct(self):
        operand = IndexedOperand("$F,X", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("0F", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("$F,Y", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("2F", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_indexed_8_bit_value_correct(self):
        operand = IndexedOperand("$20,X", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("88", code_pkg.post_byte.hex())
        self.assertEqual("20", code_pkg.additional.hex())
        self.assertEqual(3, code_pkg.size)

    def test_indexed_16_bit_value_correct(self):
        operand = IndexedOperand("$2000,X", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("89", code_pkg.post_byte.hex())
        self.assertEqual("2000", code_pkg.additional.hex())
        self.assertEqual(4, code_pkg.size)

    def test_indexed_8_bit_value_from_pc_correct(self):
        operand = IndexedOperand("$20,PCR", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("8C", code_pkg.post_byte.hex())
        self.assertEqual("20", code_pkg.additional.hex())
        self.assertEqual(3, code_pkg.size)

    def test_indexed_16_bit_value_from_pc_correct(self):
        operand = IndexedOperand("$2000,PCR", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("8D", code_pkg.post_byte.hex())
        self.assertEqual("2000", code_pkg.additional.hex())
        self.assertEqual(4, code_pkg.size)

    def test_indexed_resolve_left_side_empty_correct(self):
        operand = IndexedOperand(",X", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("84", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_indexed_resolve_left_side_A_B_D_correct(self):
        operand = IndexedOperand("A,X", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("86", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("B,X", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("85", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = IndexedOperand("D,X", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("8B", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_indexed_resolve_left_side_not_symbol_correct(self):
        operand = IndexedOperand("$F,X", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("0F", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_indexed_resolve_left_side_symbol_correct(self):
        symbol_table = {'blah': NumericValue("$F")}
        operand = IndexedOperand("blah,X", self.instruction)
        operand = operand.resolve_symbols(symbol_table)
        code_pkg = operand.translate()
        self.assertEqual("0F", code_pkg.post_byte.hex())

    def test_indexed_translate_left_address_requires_additional_resolution(self):
        operand = IndexedOperand("$1F,X", self.instruction)
        operand.left = AddressValue(32767)
        code_pkg = operand.translate()
        self.assertTrue(code_pkg.additional_needs_resolution)


class TestExtendedIndexedOperand(unittest.TestCase):
    """
    A test class for the ExtendedIndexedOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="STX", mode=Mode(ind=0xAF, ind_sz=2))

    def test_extended_indexed_type_correct(self):
        result = ExtendedIndexedOperand("[,X]", self.instruction)
        self.assertTrue(result.is_extended_indexed())

    def test_extended_indexed_string_correct(self):
        result = ExtendedIndexedOperand("[,X]", self.instruction)
        self.assertEqual("[,X]", result.operand_string)

    def test_extended_indexed_raises_with_bad_value(self):
        with self.assertRaises(OperandTypeError) as context:
            ExtendedIndexedOperand("[,blah,]", self.instruction)
        self.assertEqual("[[,blah,]] is not an extended indexed value", str(context.exception))

    def test_extended_indexed_raises_with_no_surrounding_braces(self):
        with self.assertRaises(OperandTypeError) as context:
            ExtendedIndexedOperand("blah", self.instruction)
        self.assertEqual("[blah] is not an extended indexed value", str(context.exception))

    def test_extended_indexed_raises_with_instruction_that_does_not_support_indexed(self):
        instruction = Instruction(mnemonic="STX", mode=Mode(inh=0x1F, inh_sz=1))
        with self.assertRaises(OperandTypeError) as context:
            operand = ExtendedIndexedOperand("[,X]", instruction)
            operand.translate()
        self.assertEqual("Instruction [STX] does not support indexed addressing", str(context.exception))

    def test_extended_indexed_no_offset_correct_values(self):
        operand = ExtendedIndexedOperand("[,X]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("94", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[,Y]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("B4", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[,U]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("D4", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[,S]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("F4", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_extended_indexed_A_offset_correct_values(self):
        operand = ExtendedIndexedOperand("[A,X]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("96", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[A,Y]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("B6", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[A,U]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("D6", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[A,S]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("F6", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_extended_indexed_B_offset_correct_values(self):
        operand = ExtendedIndexedOperand("[B,X]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("95", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[B,Y]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("B5", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[B,U]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("D5", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[B,S]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("F5", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_extended_indexed_D_offset_correct_values(self):
        operand = ExtendedIndexedOperand("[D,X]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("9B", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[D,Y]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("BB", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[D,U]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("DB", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[D,S]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("FB", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_extended_indexed_auto_single_increments_not_allowed(self):
        with self.assertRaises(OperandTypeError) as context:
            operand = ExtendedIndexedOperand("[,X+]", self.instruction)
            operand.translate()
        self.assertEqual("[X+] not allowed as an extended indirect value", str(context.exception))

        with self.assertRaises(OperandTypeError) as context:
            operand = ExtendedIndexedOperand("[,-X]", self.instruction)
            operand.translate()
        self.assertEqual("[-X] not allowed as an extended indirect value", str(context.exception))

    def test_extended_indexed_auto_increments_correct_values(self):
        operand = ExtendedIndexedOperand("[,X++]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("91", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[,--X]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("93", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_extended_indexed_offset_from_register_with_auto_increment_raises(self):
        with self.assertRaises(OperandTypeError) as context:
            operand = ExtendedIndexedOperand("[$1F,X++]", self.instruction)
            operand.translate()
        self.assertEqual("[[$1F,X++]] invalid indexed expression", str(context.exception))

    def test_extended_indexed_5_bit_value_correct(self):
        operand = ExtendedIndexedOperand("[$1F,X]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("98", code_pkg.post_byte.hex())
        self.assertEqual("1F", code_pkg.additional.hex())
        self.assertEqual(3, code_pkg.size)

        operand = ExtendedIndexedOperand("[$1F,Y]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("B8", code_pkg.post_byte.hex())
        self.assertEqual("1F", code_pkg.additional.hex())
        self.assertEqual(3, code_pkg.size)

    def test_extended_indexed_8_bit_value_correct(self):
        operand = ExtendedIndexedOperand("[$20,X]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("98", code_pkg.post_byte.hex())
        self.assertEqual("20", code_pkg.additional.hex())
        self.assertEqual(3, code_pkg.size)

    def test_extended_indexed_16_bit_value_offset_correct(self):
        operand = ExtendedIndexedOperand("[$2000,X]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("99", code_pkg.post_byte.hex())
        self.assertEqual("2000", code_pkg.additional.hex())
        self.assertEqual(4, code_pkg.size)

    def test_extended_indexed_8_bit_value_from_pc_correct(self):
        operand = ExtendedIndexedOperand("[$20,PCR]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("9C", code_pkg.post_byte.hex())
        self.assertEqual("20", code_pkg.additional.hex())
        self.assertEqual(3, code_pkg.size)

    def test_extended_indexed_16_bit_value_from_pc_correct(self):
        operand = ExtendedIndexedOperand("[$2000,PCR]", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("9D", code_pkg.post_byte.hex())
        self.assertEqual("2000", code_pkg.additional.hex())
        self.assertEqual(4, code_pkg.size)

    def test_extended_indexed_16_bit_value_correct(self):
        operand = ExtendedIndexedOperand("[$2000]", self.instruction)
        operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("AF", code_pkg.op_code.hex())
        self.assertEqual("9F", code_pkg.post_byte.hex())
        self.assertEqual("2000", code_pkg.additional.hex())
        self.assertEqual(4, code_pkg.size)

    def test_extended_resolve_left_side_empty_correct(self):
        operand = ExtendedIndexedOperand("[,X]", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("94", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_extended_indexed_resolve_left_side_A_B_D_correct(self):
        operand = ExtendedIndexedOperand("[A,X]", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("96", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[B,X]", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("95", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

        operand = ExtendedIndexedOperand("[D,X]", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("9B", code_pkg.post_byte.hex())
        self.assertEqual(2, code_pkg.size)

    def test_extended_indexed_resolve_left_side_not_symbol_correct(self):
        operand = ExtendedIndexedOperand("[$1F,X]", self.instruction)
        operand = operand.resolve_symbols({})
        code_pkg = operand.translate()
        self.assertEqual("98", code_pkg.post_byte.hex())
        self.assertEqual("1F", code_pkg.additional.hex())
        self.assertEqual(3, code_pkg.size)

    def test_extended_indexed_resolve_left_side_symbol_correct(self):
        symbol_table = {'blah': NumericValue("$1F")}
        operand = ExtendedIndexedOperand("[blah,X]", self.instruction)
        operand = operand.resolve_symbols(symbol_table)
        code_pkg = operand.translate()
        self.assertEqual("98", code_pkg.post_byte.hex())
        self.assertEqual("1F", code_pkg.additional.hex())
        self.assertEqual(3, code_pkg.size)

    def test_extended_indexed_resolve_symbol_correct(self):
        symbol_table = {
            "BLAH": NumericValue(2)
        }
        operand = ExtendedIndexedOperand("[BLAH]", self.instruction)
        result = operand.resolve_symbols(symbol_table=symbol_table)
        self.assertEqual("02", result.value.hex())

    def test_extended_indirect_translate_left_address_requires_resolution(self):
        operand = ExtendedIndexedOperand("[$1F,X]", self.instruction)
        operand.left = AddressValue(32767)
        code_pkg = operand.translate()
        self.assertTrue(code_pkg.additional_needs_resolution)


class TestDirectOperand(unittest.TestCase):
    """
    A test class for the DirectOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="SUBA", mode=Mode(dir=0xB0, dir_sz=3))

    def test_direct_type_correct(self):
        result = DirectOperand("$FF", self.instruction)
        self.assertTrue(result.is_direct())
        self.assertEqual("FF", result.value.hex())

    def test_direct_value_passthrough_correct(self):
        result = DirectOperand("$FF", self.instruction, value=NumericValue("$FE"))
        self.assertTrue(result.is_direct())
        self.assertEqual("FE", result.value.hex())

    def test_direct_raises_if_value_not_direct_length(self):
        with self.assertRaises(OperandTypeError) as context:
            DirectOperand("$FFFF", self.instruction)
        self.assertEqual("[$FFFF] is not a direct value", str(context.exception))

    def test_direct_force_direct_mode_correct(self):
        result = DirectOperand("<$FF", self.instruction)
        self.assertTrue(result.is_direct())
        self.assertEqual("FF", result.value.hex())

    def test_direct_raises_on_translate_not_direct_instruction(self):
        instruction = Instruction(mnemonic="SUBA", mode=Mode(imm=0xB0, imm_sz=3))
        operand = DirectOperand("<$FF", instruction)
        with self.assertRaises(OperandTypeError) as context:
            operand.translate()
        self.assertEqual("Instruction [SUBA] does not support direct addressing", str(context.exception))

    def test_direct_translate_correct(self):
        operand = DirectOperand("<$FF", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("B0", code_pkg.op_code.hex())
        self.assertEqual("FF", code_pkg.additional.hex())
        self.assertEqual(3, code_pkg.size)


class TestExtendedOperand(unittest.TestCase):
    """
    A test class for the ExtendedOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="SUBA", mode=Mode(ext=0xB0, ext_sz=3))

    def test_extended_type_correct(self):
        result = ExtendedOperand("$FFFF", self.instruction)
        self.assertTrue(result.is_extended())

    def test_extended_translate_raises_if_instruction_not_extended(self):
        instruction = Instruction(mnemonic="SUBA", mode=Mode(rel=0x3A, rel_sz=1))
        with self.assertRaises(OperandTypeError) as context:
            operand = ExtendedOperand("$FFFF", instruction)
            operand.translate()
        self.assertEqual("Instruction [SUBA] does not support extended addressing", str(context.exception))

    def test_extended_translates_correct(self):
        operand = ExtendedOperand("$FFFF", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("B0", code_pkg.op_code.hex())
        self.assertEqual("FFFF", code_pkg.additional.hex())

    def test_extended_value_passthrough_correct(self):
        operand = ExtendedOperand("", self.instruction, value="FFFF")
        self.assertEqual("FFFF", operand.value)

    def test_extended_force_extended_mode_correct(self):
        result = ExtendedOperand(">$FFFF", self.instruction)
        self.assertTrue(result.is_extended())
        self.assertEqual("FFFF", result.value.hex())


# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
