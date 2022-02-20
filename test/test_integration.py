"""
Copyright (C) 2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
This file contains the main Program class for the CoCo Assembler.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.program import Program
from cocoasm.statement import Statement

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

    def test_load_effective_address_indexed_program_counter_relative_8_bit(self):
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
        self.assertEqual([0x30, 0x8C, 0x02, 0x96, 0xFF, 0x39], program.get_binary_array())

    def test_load_effective_address_indexed_program_counter_relative_16_bit(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("B    LEAX Z,PCR"),
            Statement("     LDA $FF"),
        ]
        statements.extend(
            [Statement("     NOP  ") for _ in range(255)]
        )
        statements.extend([
            Statement("Z    RTS  "),
            Statement("     END B"),
        ])
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x30, 0x8D, 0x01, 0x01, 0x96, 0xFF, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x39], program.get_binary_array())

    def test_program_counter_relative_indexed_is_16_bit(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("B    LDX Z,PCR"),
        ]
        statements.extend(
            [Statement("     NOP  ") for _ in range(255)]
        )
        statements.extend([
            Statement("Z    RTS  "),
            Statement("     END B"),
        ])
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAE, 0x8D, 0x00, 0xFF, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x39], program.get_binary_array())

    def test_load_effective_address_extended_indexed_program_counter_relative_8_bit(self):
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
        self.assertEqual([0x30, 0x9C, 0x02, 0x96, 0xFF, 0x39], program.get_binary_array())

    def test_load_effective_address_extended_indexed_program_counter_relative_16_bit(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("B    LEAX [Z,PCR]"),
            Statement("     LDA $FF"),
        ]
        statements.extend(
            [Statement("     NOP  ") for _ in range(255)]
        )
        statements.extend([
            Statement("Z    RTS  "),
            Statement("     END B"),
        ])
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x30, 0x9D, 0x01, 0x01, 0x96, 0xFF, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x39], program.get_binary_array())

    def test_load_effective_address_program_counter_relative_extended_is_16_bit(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("B    LDX [Z,PCR]"),
        ]
        statements.extend(
            [Statement("     NOP  ") for _ in range(255)]
        )
        statements.extend([
            Statement("Z    RTS  "),
            Statement("     END B"),
        ])
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAE, 0x9D, 0x00, 0xFF, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x39], program.get_binary_array())

    def test_indexed_addressing_direct_fixed_size_correct(self):
        statements = [
            Statement("     STX 1,PCR"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x8C, 0x01], program.get_binary_array())

    def test_extended_indexed_addressing_direct_fixed_size_correct(self):
        statements = [
            Statement("     STX [1,PCR]"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x9C, 0x01], program.get_binary_array())

    def test_indexed_addressing_extended_fixed_size_integer_correct(self):
        statements = [
            Statement("     STX 258,PCR"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x8D, 0x01, 0x02], program.get_binary_array())

    def test_extended_indexed_addressing_extended_fixed_size_integer_correct(self):
        statements = [
            Statement("     STX [258,PCR]"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x9D, 0x01, 0x02], program.get_binary_array())

    def test_indexed_addressing_expression_rhs_16_bit_correct(self):
        statements = [
            Statement("TEMP  EQU $0001"),
            Statement("START STX 1+TEMP,PCR"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x8D, 0x00, 0x02], program.get_binary_array())

    def test_extended_indexed_addressing_expression_rhs_16_bit_correct(self):
        statements = [
            Statement("TEMP  EQU $0001"),
            Statement("START STX [1+TEMP,PCR]"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x9D, 0x00, 0x02], program.get_binary_array())

    def test_indexed_addressing_expression_rhs_8_bit_correct(self):
        statements = [
            Statement("TEMP  EQU $01"),
            Statement("START STX 1+TEMP,PCR"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x8C, 0x02], program.get_binary_array())

    def test_extended_indexed_addressing_expression_rhs_8_bit_correct(self):
        statements = [
            Statement("TEMP  EQU $01"),
            Statement("START STX [1+TEMP,PCR]"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x9C, 0x02], program.get_binary_array())

    def test_indexed_addressing_extended_fixed_size_correct(self):
        statements = [
            Statement("     STX $0102,PCR"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x8D, 0x01, 0x02], program.get_binary_array())

    def test_extended_indexed_addressing_extended_fixed_size_correct(self):
        statements = [
            Statement("     STX [$0102,PCR]"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x9D, 0x01, 0x02], program.get_binary_array())

    def test_assembly_line_regex_with_inherent_operands(self):
        statements = [
            Statement("     RTS            ;"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x39], program.get_binary_array())

    def test_assembly_line_regex_with_at_symbols_in_operands_and_labels(self):
        statements = [
            Statement("         ORG $0100           ;"),
            Statement("START    LDA #$01            ;"),
            Statement("         LDA X@              ;"),
            Statement("X@       FCB 0               ;"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x86, 0x01, 0xB6, 0x01, 0x05, 0x00], program.get_binary_array())

    def test_explicit_direct_addressing_operand(self):
        statements = [
            Statement("         ORG $0100           ;"),
            Statement("START    LDA <$01            ;"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x96, 0x01], program.get_binary_array())

    def test_explicit_extended_addressing_operand(self):
        statements = [
            Statement("         ORG $0100           ;"),
            Statement("START    LDA >$0001            ;"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xB6, 0x00, 0x01], program.get_binary_array())

    def test_immediate_symbol_expression(self):
        statements = [
            Statement("VAR      EQU $01             ;"),
            Statement("         ORG $0100           ;"),
            Statement("         LDA #VAR+1          ;"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x86, 0x02], program.get_binary_array())

    def test_string_definition(self):
        statements = [
            Statement("         FCC \"PRESS S TO RESTART,\""),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x50, 0x52, 0x45, 0x53, 0x53, 0x20, 0x53, 0x20,
                          0x54, 0x4F, 0x20, 0x52, 0x45, 0x53, 0x54, 0x41,
                          0x52, 0x54, 0x2C], program.get_binary_array())

    def test_expression_8_bit_correct(self):
        statements = [
            Statement("VAR      EQU $02"),
            Statement("         LDA #VAR+1"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x86, 0x03], program.get_binary_array())

    def test_expression_16_bit_correct(self):
        statements = [
            Statement("VAR      EQU $002"),
            Statement("         LDD #VAR+1"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xCC, 0x00, 0x03], program.get_binary_array())

    def test_indexed_expression_with_address_resolves_correct(self):
        statements = [
            Statement("       STX 1+ADDR,PCR "),
            Statement("ADDR   NOP "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x8C, 0x04, 0x12], program.get_binary_array())

    def test_extended_indexed_expression_with_address_resolves_correct(self):
        statements = [
            Statement("       STX [1+ADDR,PCR] "),
            Statement("ADDR   NOP "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x9C, 0x04, 0x12], program.get_binary_array())

    def test_indexed_with_empty_lhs(self):
        statements = [
            Statement("      STX ,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x84], program.get_binary_array())

    def test_extended_indexed_with_empty_lhs(self):
        statements = [
            Statement("      STX [,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x94], program.get_binary_array())

    def test_explicit_direct_addressing_mode(self):
        statements = [
            Statement("      LDX <$88")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x9E, 0x88], program.get_binary_array())

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
