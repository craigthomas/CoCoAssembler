"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.operands import UnknownOperand, InherentOperand, ImmediateOperand, \
    OperandType
from cocoasm.instruction import Instruction, Mode

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


class TestImmediateOperand(unittest.TestCase):
    """
    A test class for the InherentOperand class.
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

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
