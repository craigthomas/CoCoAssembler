"""
Copyright (C) 2022 Craig Thomas

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


class TestProgram(unittest.TestCase):
    """
    A test class for the Program class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_nam_mnemonic_sets_name(self):
        statement = Statement("    NAM test")
        program = Program()
        program.statements = [statement]
        program.translate_statements()
        self.assertEqual("test", program.name)

    def test_nam_mnemonic_empty(self):
        program = Program()
        program.statements = []
        program.translate_statements()
        self.assertEqual(None, program.name)

    def test_org_sets_origin(self):
        statement = Statement("    ORG $1234")
        program = Program()
        program.statements = [statement]
        program.translate_statements()
        self.assertEqual("1234", program.origin.hex())

    def test_save_symbol_raises_if_redefined(self):
        statement = Statement("BLAH    JMP $FFFF")
        program = Program()
        program.symbol_table = {
            "BLAH": 1234
        }
        with self.assertRaises(TranslationError) as context:
            program.save_symbol(0, statement)
        self.assertEqual("'Label [BLAH] redefined'", str(context.exception))

    def test_save_symbol_does_nothing_if_no_label(self):
        statement = Statement("    JMP $FFFF")
        program = Program()
        program.symbol_table = {
            "BLAH": 1234
        }
        program.save_symbol(0, statement)
        self.assertEqual({"BLAH": 1234}, program.symbol_table)

    def test_save_symbol_saves_value(self):
        statement = Statement("POLCAT EQU $FFEE")
        program = Program()
        program.save_symbol(0, statement)
        self.assertEqual("FFEE", program.symbol_table["POLCAT"].hex())

    def test_save_symbol_saves_index_of_statement(self):
        statement = Statement("START   JMP $FFEE")
        program = Program()
        program.save_symbol(0x35, statement)
        self.assertEqual("35", program.symbol_table["START"].hex())

    @patch('builtins.print')
    def test_print_empty_symbol_table_corect(self, print_mock):
        program = Program()
        program.print_symbol_table()
        self.assertEqual([call("-- Symbol Table --")], print_mock.mock_calls)

    @patch('builtins.print')
    def test_print_symbol_table_corect(self, print_mock):
        statement = Statement("POLCAT EQU $FFEE")
        program = Program()
        program.save_symbol(0, statement)
        program.print_symbol_table()
        self.assertEqual([call("-- Symbol Table --"), call("$FFEE POLCAT")], print_mock.mock_calls)

    @patch('builtins.print')
    def test_print_statements_empty_statements_correct(self, print_mock):
        program = Program()
        program.print_statements()
        self.assertEqual([call("-- Assembled Statements --")], print_mock.mock_calls)

    @patch('builtins.print')
    def test_print_statements_correct(self, print_mock):
        statement = Statement("LABEL JMP $FFFF ; comment")
        program = Program()
        program.statements = [statement]
        program.print_statements()
        self.assertEqual(
            [
                call("-- Assembled Statements --"),
                call("$                 LABEL   JMP $FFFF                          ; comment                                 "),
            ],
            print_mock.mock_calls
        )

    @patch('builtins.print')
    def test_character_literal_regression(self, print_mock):
        statements = [
            Statement("  NAM LITERAL"),
            Statement("  ORG $0600"),
            Statement("START LDA #'C"),
            Statement("  END START"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        program.print_statements()
        self.assertEqual(
            [
                call("-- Assembled Statements --"),
                call("$0000                         NAM LITERAL                        ;                                         "),
                call("$0600                         ORG $0600                          ;                                         "),
                call("$0600 8643            START   LDA #'C                            ;                                         "),
                call("$0602                         END START                          ;                                         "),

            ],
            print_mock.mock_calls
        )

    @patch('builtins.print')
    def test_binary_string_regression(self, print_mock):
        statements = [
            Statement("  NAM LITERAL"),
            Statement("  ORG $0600"),
            Statement("START LDA #%10101010"),
            Statement("  END START"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        program.print_statements()
        self.assertEqual(
            [
                call("-- Assembled Statements --"),
                call("$0000                         NAM LITERAL                        ;                                         "),
                call("$0600                         ORG $0600                          ;                                         "),
                call("$0600 86AA            START   LDA #%10101010                     ;                                         "),
                call("$0602                         END START                          ;                                         "),

            ],
            print_mock.mock_calls
        )

    @patch('builtins.print')
    def test_throw_error_works_correctly(self, print_mock):
        statement = Statement("LABEL JMP $FFFF ; comment")
        program = Program()
        with self.assertRaises(SystemExit):
            program.throw_error(TranslationError("test", statement))
        self.assertEqual(
            [
                call("test"),
                call("$                 LABEL   JMP $FFFF                          ; comment                                 ")
            ],
            print_mock.mock_calls
        )

    def test_get_binary_array_empty_if_no_statements(self):
        program = Program()
        self.assertEqual([], program.get_binary_array())

    def test_get_binary_array_empty_on_comments_and_empty_lines(self):
        statement1 = Statement("")
        statement2 = Statement("; comment only")
        program = Program()
        program.statements = [statement1, statement2]
        self.assertEqual([], program.get_binary_array())

    def test_get_binary_array_op_code_only(self):
        statement1 = Statement("    JMP $FFFF")
        statement1.code_pkg.op_code = NumericValue("$FF")
        program = Program()
        program.statements = [statement1]
        self.assertEqual([0xFF], program.get_binary_array())

    def test_get_binary_array_additional_only(self):
        statement1 = Statement("    JMP $FFFF")
        statement1.code_pkg.additional = NumericValue("$FF")
        program = Program()
        program.statements = [statement1]
        self.assertEqual([0xFF], program.get_binary_array())

    def test_get_binary_array_postbyte_only(self):
        statement1 = Statement("    JMP $FFFF")
        statement1.code_pkg.post_byte = NumericValue("$FF")
        program = Program()
        program.statements = [statement1]
        self.assertEqual([0xFF], program.get_binary_array())

    def test_get_binary_array_all_correct(self):
        statement1 = Statement("    JMP $FFFF")
        statement1.code_pkg.op_code = NumericValue("$DEAD")
        statement1.code_pkg.post_byte = NumericValue("$BEEF")
        statement1.code_pkg.additional = NumericValue("$CAFE")
        program = Program()
        program.statements = [statement1]
        self.assertEqual([0xDE, 0xAD, 0xBE, 0xEF, 0xCA, 0xFE], program.get_binary_array())

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
