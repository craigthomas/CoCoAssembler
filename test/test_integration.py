"""
Copyright (C) 2019-2021 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
This file contains the main Program class for the CoCo Assembler.
"""
# I M P O R T S ###############################################################

import unittest

from unittest.mock import patch, call

from cocoasm.program import Program
from cocoasm.statement import Statement
from cocoasm.exceptions import TranslationError
from cocoasm.values import NumericValue

# C L A S S E S ###############################################################


class TestIntegration(unittest.TestCase):
    """
    Integration tests.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_expression_addition_with_address_on_left(self):
        statements = [
            Statement("     ORG $0E00"),
            Statement("V    STX R+1"),
            Statement("R    FCB 0"),
            Statement("     FCB 0"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xBF, 0x0E, 0x04, 0x00, 0x00], program.get_binary_array())

    def test_expression_subtraction_with_address_on_left(self):
        statements = [
            Statement("     ORG $0E00"),
            Statement("V    STX R-1"),
            Statement("     FCB 0"),
            Statement("R    FCB 0"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xBF, 0x0E, 0x03, 0x00, 0x00], program.get_binary_array())

    def test_program_counter_relative_8_bit_offset_reverse(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("V    FCB 0"),
            Statement("B    LDA $FF"),
            Statement("     STY V,PCR"),
            Statement("     END B"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x00, 0x96, 0xFF, 0x10, 0xAF, 0x8C, 0xF9], program.get_binary_array())

    def test_program_counter_relative_8_bit_offset_forward(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("B    LDA $FF"),
            Statement("     STY V,PCR"),
            Statement("     INCA "),
            Statement("V    FCB 0"),
            Statement("     END B"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x96, 0xFF, 0x10, 0xAF, 0x8C, 0x01, 0x4C, 0x00], program.get_binary_array())

    def test_program_counter_relative_8_bit_offset_extended_reverse(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("V    FCB 0"),
            Statement("B    LDA $FF"),
            Statement("     STY [V,PCR]"),
            Statement("     END B"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x00, 0x96, 0xFF, 0x10, 0xAF, 0x9C, 0xF9], program.get_binary_array())

    def test_program_counter_relative_8_bit_offset_extended_forward(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("B    LDA $FF"),
            Statement("     STY [V,PCR]"),
            Statement("     INCA "),
            Statement("V    FCB 0"),
            Statement("     END B"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x96, 0xFF, 0x10, 0xAF, 0x9C, 0x01, 0x4C, 0x00], program.get_binary_array())

    def test_load_effective_address_program_counter_relative_is_16_bit(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("B    LEAX Z,PCR"),
            Statement("     LDA $FF"),
            Statement("Z    RTS  "),
            Statement("     END B"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x30, 0x8D, 0x00, 0x02, 0x96, 0xFF, 0x39], program.get_binary_array())

    def test_load_effective_address_program_counter_relative_extended_is_16_bit(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("B    LEAX [Z,PCR]"),
            Statement("     LDA $FF"),
            Statement("Z    RTS  "),
            Statement("     END B"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x30, 0x9D, 0x00, 0x02, 0x96, 0xFF, 0x39], program.get_binary_array())

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
