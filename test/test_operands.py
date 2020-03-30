"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.operands import UnknownOperand, InherentOperand, ImmediateOperand, \
    OperandType, IndexedOperand, RelativeOperand
from cocoasm.instruction import Instruction, Mode
from cocoasm.values import NumericValue

# C L A S S E S ###############################################################


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
        self.assertTrue(result.is_type(OperandType.UNKNOWN))

    def test_unknown_string_correct(self):
        result = UnknownOperand("blah", self.fcc_instruction)
        self.assertEqual("blah", result.operand_string)

    def test_unknown_value_correct(self):
        result = UnknownOperand("$FF", self.instruction)
        self.assertEqual("FF", result.value.hex())


class TestRelativeOperand(unittest.TestCase):
    """
    A test class for the RelativeOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="BEQ", mode=Mode(rel=0x3A, rel_sz=1), is_short_branch=True)

    def test_relative_type_correct(self):
        result = RelativeOperand("$FF", self.instruction)
        self.assertTrue(result.is_type(OperandType.RELATIVE))

    def test_relative_raises_if_instruction_not_branch(self):
        instruction = Instruction(mnemonic="BEQ", mode=Mode(rel=0x3A, rel_sz=1))
        with self.assertRaises(ValueError) as context:
            RelativeOperand("$FF", instruction)
        self.assertEqual("[BEQ] is not a branch instruction", str(context.exception))


class TestInherentOperand(unittest.TestCase):
    """
    A test class for the InherentOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_inherent_type_correct(self):
        result = InherentOperand(None, None)
        self.assertTrue(result.is_type(OperandType.INHERENT))

    def test_inherent_string_correct(self):
        result = InherentOperand(None, None)
        self.assertEqual("", result.operand_string)

    def test_inherent_raises_with_value(self):
        with self.assertRaises(ValueError) as context:
            InherentOperand("$FF", None)
        self.assertEqual("[$FF] is not an inherent value", str(context.exception))

    def test_inherent_raises_with_value_passthrough(self):
        value = NumericValue("$FF")
        with self.assertRaises(ValueError) as context:
            InherentOperand(None, None, value=value)
        self.assertEqual("[$FF] is not an inherent value", str(context.exception))

    def test_inherent_raises_with_bad_instruction_on_translate(self):
        instruction = Instruction(mnemonic="STX", mode=Mode(imm=0xAF, imm_sz=1))
        with self.assertRaises(ValueError) as context:
            result = InherentOperand(None, instruction)
            result.translate()
        self.assertEqual("Instruction [STX] requires an operand", str(context.exception))


class TestImmediateOperand(unittest.TestCase):
    """
    A test class for the ImmediateOperand class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.instruction = Instruction(mnemonic="ABX", mode=Mode(inh=0x3A, inh_sz=1))

    def test_immediate_type_correct(self):
        result = ImmediateOperand("#blah", self.instruction)
        self.assertTrue(result.is_type(OperandType.IMMEDIATE))

    def test_immediate_string_correct(self):
        result = ImmediateOperand("#blah", self.instruction)
        self.assertEqual("#blah", result.operand_string)

    def test_immediate_raises_with_bad_value(self):
        with self.assertRaises(ValueError) as context:
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
        with self.assertRaises(ValueError) as context:
            result = ImmediateOperand("#$FF", instruction)
            result.translate()
        self.assertEqual("Instruction [STX] does not support immediate addressing", str(context.exception))


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
        self.assertTrue(result.is_type(OperandType.INDEXED))

    def test_indexed_string_correct(self):
        result = IndexedOperand(",X", self.instruction)
        self.assertEqual(",X", result.operand_string)

    def test_indexed_raises_with_bad_value(self):
        with self.assertRaises(ValueError) as context:
            IndexedOperand(",blah,", self.instruction)
        self.assertEqual("[,blah,] incorrect number of commas in indexed value", str(context.exception))

    def test_indexed_raises_with_no_commas(self):
        with self.assertRaises(ValueError) as context:
            IndexedOperand("blah", self.instruction)
        self.assertEqual("[blah] is not an indexed value", str(context.exception))

    def test_indexed_raises_with_instruction_that_does_not_support_indexed(self):
        instruction = Instruction(mnemonic="STX", mode=Mode(inh=0x1F, inh_sz=1))
        with self.assertRaises(ValueError) as context:
            operand = IndexedOperand(",X", instruction)
            operand.translate()
        self.assertEqual("Instruction [STX] does not support indexed addressing", str(context.exception))

    def test_indexed_no_offset_correct_values(self):
        operand = IndexedOperand(",X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("84", code_pkg.post_byte.hex())

        operand = IndexedOperand(",Y", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("A4", code_pkg.post_byte.hex())

        operand = IndexedOperand(",U", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("C4", code_pkg.post_byte.hex())

        operand = IndexedOperand(",S", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("E4", code_pkg.post_byte.hex())

    def test_indexed_A_offset_correct_values(self):
        operand = IndexedOperand("A,X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("86", code_pkg.post_byte.hex())

        operand = IndexedOperand("A,Y", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("A6", code_pkg.post_byte.hex())

        operand = IndexedOperand("A,U", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("C6", code_pkg.post_byte.hex())

        operand = IndexedOperand("A,S", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("E6", code_pkg.post_byte.hex())

    def test_indexed_B_offset_correct_values(self):
        operand = IndexedOperand("B,X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("85", code_pkg.post_byte.hex())

        operand = IndexedOperand("B,Y", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("A5", code_pkg.post_byte.hex())

        operand = IndexedOperand("B,U", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("C5", code_pkg.post_byte.hex())

        operand = IndexedOperand("B,S", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("E5", code_pkg.post_byte.hex())

    def test_indexed_D_offset_correct_values(self):
        operand = IndexedOperand("D,X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("8B", code_pkg.post_byte.hex())

        operand = IndexedOperand("D,Y", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("AB", code_pkg.post_byte.hex())

        operand = IndexedOperand("D,U", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("CB", code_pkg.post_byte.hex())

        operand = IndexedOperand("D,S", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("EB", code_pkg.post_byte.hex())

    def test_indexed_auto_increments_correct_values(self):
        operand = IndexedOperand(",X+", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("80", code_pkg.post_byte.hex())

        operand = IndexedOperand(",X++", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("81", code_pkg.post_byte.hex())

        operand = IndexedOperand(",-X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("82", code_pkg.post_byte.hex())

        operand = IndexedOperand(",--X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("83", code_pkg.post_byte.hex())

    def test_indexed_offset_from_register_with_auto_increment_raises(self):
        with self.assertRaises(ValueError) as context:
            operand = IndexedOperand("$1F,X+", self.instruction)
            operand.translate()
        self.assertEqual("[$1F,X+] invalid indexed expression", str(context.exception))

    def test_indexed_5_bit_value_correct(self):
        operand = IndexedOperand("$1F,X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("1F", code_pkg.post_byte.hex())

        operand = IndexedOperand("$1F,Y", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("3F", code_pkg.post_byte.hex())

    def test_indexed_8_bit_value_correct(self):
        operand = IndexedOperand("$20,X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("88", code_pkg.post_byte.hex())
        self.assertEqual("20", code_pkg.additional.hex())

    def test_indexed_16_bit_value_correct(self):
        operand = IndexedOperand("$2000,X", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("89", code_pkg.post_byte.hex())
        self.assertEqual("2000", code_pkg.additional.hex())

    def test_indexed_8_bit_value_from_pc_correct(self):
        operand = IndexedOperand("$20,PC", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("8C", code_pkg.post_byte.hex())
        self.assertEqual("20", code_pkg.additional.hex())

    def test_indexed_16_bit_value_from_pc_correct(self):
        operand = IndexedOperand("$2000,PC", self.instruction)
        code_pkg = operand.translate()
        self.assertEqual("8D", code_pkg.post_byte.hex())
        self.assertEqual("2000", code_pkg.additional.hex())

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
