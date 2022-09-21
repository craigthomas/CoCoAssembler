"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
This file contains the main Program class for the CoCo Assembler.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.program import Program
from cocoasm.statement import Statement
from cocoasm.exceptions import TranslationError
from cocoasm.values import NumericValue

from mock import MagicMock, patch, mock_open

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

    def test_print_empty_symbol_table_corect(self):
        program = Program()
        self.assertEqual([], program.get_symbol_table())

    def test_print_symbol_table_corect(self):
        statement = Statement("POLCAT EQU $FFEE")
        program = Program()
        program.save_symbol(0, statement)
        symbols = program.get_symbol_table()
        self.assertEqual(["$FFEE POLCAT"], symbols)

    def test_print_statements_empty_statements_correct(self):
        program = Program()
        self.assertEqual([], program.get_statements())

    def test_print_statements_correct(self):
        statement = Statement("LABEL JMP $FFFF ; comment")
        program = Program()
        program.statements = [statement]
        statements = program.get_statements()
        expected = [
            "$                 LABEL   JMP $FFFF                          ; comment                                 ",
        ]
        self.assertEqual(expected, statements)

    def test_character_literal_regression(self):
        statements = [
            Statement("  NAM LITERAL"),
            Statement("  ORG $0600"),
            Statement("START LDA #'C"),
            Statement("  END START"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        statements = program.get_statements()
        expected = [
          "$0000                         NAM LITERAL                        ;                                         ",
          "$0600                         ORG $0600                          ;                                         ",
          "$0600 8643            START   LDA #'C                            ;                                         ",
          "$0602                         END START                          ;                                         ",
        ]
        self.assertEqual(expected, statements)

    def test_binary_string_regression(self):
        statements = [
            Statement("  NAM LITERAL"),
            Statement("  ORG $0600"),
            Statement("START LDA #%10101010"),
            Statement("  END START"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        statements = program.get_statements()
        expected = [
          "$0000                         NAM LITERAL                        ;                                         ",
          "$0600                         ORG $0600                          ;                                         ",
          "$0600 86AA            START   LDA #%10101010                     ;                                         ",
          "$0602                         END START                          ;                                         ",
        ]
        self.assertEqual(expected, statements)

    def test_translation_error_raised_on_bad_label(self):
        statement = Statement("LABEL JMP EXIT ; comment")
        program = Program()
        with self.assertRaises(TranslationError):
            program.statements = [statement]
            program.translate_statements()

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

    def test_parse_empty_source_file_returns_empty_statements(self):
        source_file_mock = MagicMock()
        source_file_mock.get_contents.return_value = []
        program = Program()
        statements = program.parse(source_file_mock)
        self.assertEqual([], statements)

    def test_parse_source_file_comments_only_returns_empty_statements(self):
        statements = [
            "; this is a comment line",
            "; this is another comment line",
        ]
        program = Program()
        self.assertEqual([], program.parse(statements))

    def test_parse_source_file_empty_lines_returns_empty_statements(self):
        statements = [
            "",
            "",
        ]
        program = Program()
        self.assertEqual([], program.parse(statements))

    def test_parse_source_file_empty_lines_and_comment_lines_only_returns_empty_statements(self):
        statements = [
            "",
            "; this is a comment line",
            "",
            "; another comment line",
        ]
        program = Program()
        self.assertEqual([], program.parse(statements))

    def test_parse_source_file_single_statement_correct(self):
        statements = [
            "    ORG $0000",
        ]
        statement = Statement("    ORG $0000")
        program = Program()
        self.assertListEqual([statement], program.parse(statements))

    def test_parse_source_file_multiple_statements_correct(self):
        statements = [
            "       ORG $0000",
            "START  LDD $FFEE ; LOAD D",
            "       END START ; END PROGRAM"
        ]
        assembled_statements = [
            Statement("       ORG $0000"),
            Statement("START  LDD $FFEE ; LOAD D"),
            Statement("       END START ; END PROGRAM"),
        ]
        program = Program()
        self.assertListEqual(assembled_statements, program.parse(statements))

    def test_process_source_file_correct(self):
        statements = [
            "            ORG     $0600",
            "BEGIN       LDA     $FF",
            "            STY     VAR,PCR",
            "VAR         FCB     0",
            "            END     BEGIN",
        ]
        assembled_statements = [
          "$0600                         ORG $0600                          ;                                         ",
          "$0600 96FF            BEGIN   LDA $FF                            ;                                         ",
          "$0602 10AF8C00                STY VAR,PCR                        ;                                         ",
          "$0606 00                VAR   FCB 0                              ;                                         ",
          "$0607                         END BEGIN                          ;                                         ",
        ]
        program = Program()
        program.process(statements)
        self.assertEqual(assembled_statements, program.get_statements())

    @patch("builtins.open", new_callable=mock_open, read_data="END         LDB     $FE       ; LOAD B")
    def test_process_mnemonics_includes_correct_files(self, _):
        statements = [
            "BEGIN       LDA     $FF       ; LOAD A",
            "            INCLUDE OTHER.ASM",
        ]
        actual_statements = [
          "$0000 96FF            BEGIN   LDA $FF                            ; LOAD A                                  ",
          "$0002 D6FE              END   LDB $FE                            ; LOAD B                                  ",
        ]
        program = Program()
        program.process(statements)
        self.assertEqual(actual_statements, program.get_statements())


# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
