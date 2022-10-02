"""
Copyright (C) 2013-2022 Craig Thomas

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

    def test_load_effective_address_extended_indexed_program_counter_relative_16_bit_negative(self):
        statements = [
            Statement("     ORG $0600"),
            Statement("Z    RTS   "),
            Statement("     LDA $FF"),
        ]
        statements.extend(
            [Statement("     NOP  ") for _ in range(255)]
        )
        statements.extend([
            Statement("B    LEAX [Z,PCR]"),
            Statement("     END B"),
        ])
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x39, 0x96, 0xFF, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12,
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
                          0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x12, 0x30, 0x9D,
                          0xFE, 0xFA], program.get_binary_array())

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

    def test_expression_address_multiply_correct(self):
        statements = [
            Statement("         ORG $0002"),
            Statement("VAR      STA $FE"),
            Statement("         LDD VAR*2"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x97, 0xFE, 0xFC, 0x00, 0x04], program.get_binary_array())

    def test_expression_divide_correct(self):
        statements = [
            Statement("         ORG $0002"),
            Statement("VAR      STA $FE"),
            Statement("         LDD VAR/2"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x97, 0xFE, 0xFC, 0x00, 0x01], program.get_binary_array())

    def test_indexed_expression_with_address_resolves_correct(self):
        statements = [
            Statement("       STX 1+ADDR,PCR "),
            Statement("ADDR   NOP "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x8C, 0x01, 0x12], program.get_binary_array())

    def test_extended_indexed_expression_with_address_resolves_correct(self):
        statements = [
            Statement("       STX [1+ADDR,PCR] "),
            Statement("ADDR   NOP "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xAF, 0x9C, 0x01, 0x12], program.get_binary_array())

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

    def test_negative_one_offset_in_indexed_mode(self):
        statements = [
            Statement("      STD -1,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x1F], program.get_binary_array())

    def test_negative_5_bit_offset_max_in_indexed_mode(self):
        statements = [
            Statement("      STD -16,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x10], program.get_binary_array())

    def test_positive_5_bit_offset_max_in_indexed_mode(self):
        statements = [
            Statement("      STD 15,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x0F], program.get_binary_array())

    def test_negative_8_bit_offset_in_indexed_mode(self):
        statements = [
            Statement("      STD -17,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x88, 0xEF], program.get_binary_array())

    def test_positive_8_bit_offset_in_indexed_mode(self):
        statements = [
            Statement("      STD 17,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x88, 0x11], program.get_binary_array())

    def test_negative_8_bit_offset_max_in_indexed_mode(self):
        statements = [
            Statement("      STD -128,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x88, 0x80], program.get_binary_array())

    def test_positive_8_bit_offset_max_in_indexed_mode(self):
        statements = [
            Statement("      STD 127,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x88, 0x7F], program.get_binary_array())

    def test_negative_16_bit_offset_in_indexed_mode(self):
        statements = [
            Statement("      STD -130,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x89, 0xFF, 0x7E], program.get_binary_array())

    def test_positive_16_bit_offset_in_indexed_mode(self):
        statements = [
            Statement("      STD 130,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x89, 0x00, 0x82], program.get_binary_array())

    def test_negative_16_bit_offset_max_in_indexed_mode(self):
        statements = [
            Statement("      STD -32768,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x89, 0x80, 0x00], program.get_binary_array())

    def test_positive_16_bit_offset_max_in_indexed_mode(self):
        statements = [
            Statement("      STD 32767,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x89, 0x7F, 0xFF], program.get_binary_array())

    def test_zero_offset_in_indexed_mode(self):
        statements = [
            Statement("      STD 0,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x84], program.get_binary_array())

    def test_zero_offset_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [0,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x94], program.get_binary_array())

    def test_negative_one_offset_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [-1,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        # Should default to 8-bit handling
        self.assertEqual([0xED, 0x98, 0xFF], program.get_binary_array())

    def test_negative_4_bit_offset_max_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [-16,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        # Should default to 8-bit handling
        self.assertEqual([0xED, 0x98, 0xF0], program.get_binary_array())

    def test_positive_4_bit_offset_max_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [15,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        # Should default to 8-bit handling
        self.assertEqual([0xED, 0x98, 0x0F], program.get_binary_array())

    def test_negative_8_bit_offset_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [-17,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x98, 0xEF], program.get_binary_array())

    def test_positive_8_bit_offset_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [17,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x98, 0x11], program.get_binary_array())

    def test_negative_8_bit_offset_max_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [-128,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x98, 0x80], program.get_binary_array())

    def test_positive_8_bit_offset_max_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [127,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x98, 0x7F], program.get_binary_array())

    def test_negative_16_bit_offset_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [-130,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x99, 0xFF, 0x7E], program.get_binary_array())

    def test_positive_16_bit_offset_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [130,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x99, 0x00, 0x82], program.get_binary_array())

    def test_negative_16_bit_offset_max_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [-32768,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x99, 0x80, 0x00], program.get_binary_array())

    def test_positive_16_bit_offset_max_in_extended_indexed_mode(self):
        statements = [
            Statement("      STD [32767,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xED, 0x99, 0x7F, 0xFF], program.get_binary_array())

    def test_string_in_lhs_of_indexed_expression(self):
        statements = [
            Statement("      LDA B,X")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xA6, 0x85], program.get_binary_array())

    def test_string_in_lhs_of_extended_indexed_expression(self):
        statements = [
            Statement("      LDA [B,X]")
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xA6, 0x95], program.get_binary_array())

    def test_negative_immediate_8_bit(self):
        statements = [
            Statement("         CMPB #-2"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0xC1, 0xFE], program.get_binary_array())

    def test_negative_immediate_16_bit(self):
        statements = [
            Statement("         CMPX #-258"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x8C, 0xFE, 0xFE], program.get_binary_array())

    def test_multi_byte_declaration(self):
        statements = [
            Statement("         FCB $55,$44,17"),
            Statement("         FCB $AA"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        self.assertEqual([0x55, 0x44, 0x11, 0xAA], program.get_binary_array())

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
