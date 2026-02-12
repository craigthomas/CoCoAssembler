"""
Copyright (C) 2026 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
This file contains the main Program class for the CoCo Assembler.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.program import Program
from cocoasm.statement import Statement
from cocoasm.exceptions import TranslationError, MacroError
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

    def test_macro_no_args_replacement_correct(self):
        statements = [
            Statement("        ORG $0600"),
            Statement("MYMACRO MACRO    "),
            Statement("        LDA #$FF "),
            Statement("        ENDM     "),
            Statement("        LDA #$00 "),
            Statement("        MYMACRO  "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        statements = program.get_statements()
        expected = [
          "$0600                         ORG $0600                          ;                                         ",
          "$0600 8600                    LDA #$00                           ;                                         ",
          "$0602 86FF                    LDA #$FF                           ;                                         ",
        ]
        self.assertEqual(expected, statements)

    def test_macro_no_args_multi_line_replacement_correct(self):
        statements = [
            Statement("        ORG $0600"),
            Statement("MYMACRO MACRO    "),
            Statement("        LDA #$FF "),
            Statement("        LDA #$FE "),
            Statement("        ENDM     "),
            Statement("        LDA #$00 "),
            Statement("        MYMACRO  "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        statements = program.get_statements()
        expected = [
          "$0600                         ORG $0600                          ;                                         ",
          "$0600 8600                    LDA #$00                           ;                                         ",
          "$0602 86FF                    LDA #$FF                           ;                                         ",
          "$0604 86FE                    LDA #$FE                           ;                                         ",
        ]
        self.assertEqual(expected, statements)

    def test_macro_embedded_symbol_expanded_correct(self):
        statements = [
            Statement("        ORG $0600"),
            Statement("MYMACRO MACRO    "),
            Statement(r"\.A    LDA #$FF "),
            Statement(r"       JMP \.A  "),
            Statement("        ENDM     "),
            Statement("        MYMACRO  "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        statements = program.get_statements()
        expected = [
          "$0600                         ORG $0600                          ;                                         ",
          "$0600 86FF           A00000   LDA #$FF                           ;                                         ",
          "$0602 7E0600                  JMP A00000                         ;                                         ",
        ]
        self.assertEqual(expected, statements)

    def test_macro_embedded_symbol_expanded_multiple_times_correct(self):
        statements = [
            Statement("        ORG $0600"),
            Statement("MYMACRO MACRO    "),
            Statement(r"\.A    LDA #$FF "),
            Statement(r"       JMP \.A  "),
            Statement("        ENDM     "),
            Statement("        MYMACRO  "),
            Statement("        MYMACRO  "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        statements = program.get_statements()
        expected = [
          "$0600                         ORG $0600                          ;                                         ",
          "$0600 86FF           A00000   LDA #$FF                           ;                                         ",
          "$0602 7E0600                  JMP A00000                         ;                                         ",
          "$0605 86FF           A00001   LDA #$FF                           ;                                         ",
          "$0607 7E0605                  JMP A00001                         ;                                         ",
        ]
        self.assertEqual(expected, statements)

    def test_macro_embedded_symbol_regression_condition_1_correct(self):
        statements = [
            Statement(r"        NAM HELLO"),
            Statement(r"LOADER  MACRO    "),
            Statement(r"        LDA \0   "),
            Statement(r"        LDB \1   "),
            Statement(r"        CMPA #$02"),
            Statement(r"        BEQ \.B  "),
            Statement(r"        LDX \2   "),
            Statement(r"\.B     LDY \3   "),
            Statement(r"        ENDM     "),
            Statement(r"        LOADER #$00,#$03,#$0000,#$FFFF"),
            Statement(r"        END      "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        statements = program.get_statements()
        expected = [
          "$0000                         NAM HELLO                          ;                                         ",
          "$0000 8600                    LDA #$00                           ;                                         ",
          "$0002 C603                    LDB #$03                           ;                                         ",
          "$0004 8102                   CMPA #$02                           ;                                         ",
          "$0006 2703                    BEQ B00000                         ;                                         ",
          "$0008 8E0000                  LDX #$0000                         ;                                         ",
          "$000B 108EFFFF       B00000   LDY #$FFFF                         ;                                         ",
          "$000F                         END                                ;                                         ",
        ]
        self.assertEqual(expected, statements)

    def test_macro_no_end_raises(self):
        statements = [
            Statement("MYMACRO MACRO"),
        ]
        program = Program()
        program.statements = statements
        with self.assertRaises(MacroError):
            program.translate_statements()

    def test_macro_redefinition_raises(self):
        statements = [
            Statement("MYMACRO MACRO"),
            Statement("        ENDM"),
            Statement("MYMACRO MACRO"),
            Statement("        ENDM"),
        ]
        program = Program()
        program.statements = statements
        with self.assertRaises(MacroError):
            program.translate_statements()

    def test_embedded_macro_raises(self):
        statements = [
            Statement("MYMACRO1 MACRO"),
            Statement("NEWMACRO MACRO"),
            Statement("         ENDM"),
            Statement("         ENDM")
        ]
        program = Program()
        program.statements = statements
        with self.assertRaises(MacroError):
            program.translate_statements()

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

    def test_end_sets_exec_address(self):
        statements = [
            Statement("  NAM EXECADDR"),
            Statement("  ORG $0600"),
            Statement("  FCB $01"),
            Statement("START LDA #$00"),
            Statement("  END START"),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        statements = program.get_statements()
        expected = [
          "$0000                         NAM EXECADDR                       ;                                         ",
          "$0600                         ORG $0600                          ;                                         ",
          "$0600 01                      FCB $01                            ;                                         ",
          "$0601 8600            START   LDA #$00                           ;                                         ",
          "$0603                         END START                          ;                                         ",
        ]
        self.assertEqual(expected, statements)
        self.assertEqual(0x0601, program.exec_address.int)

    def test_end_no_label_sets_exec_address_to_origin(self):
        statements = [
            Statement("  NAM EXECADDR"),
            Statement("  ORG $0600"),
            Statement("  FCB $01"),
            Statement("START LDA #$00"),
            Statement("  END "),
        ]
        program = Program()
        program.statements = statements
        program.translate_statements()
        statements = program.get_statements()
        expected = [
          "$0000                         NAM EXECADDR                       ;                                         ",
          "$0600                         ORG $0600                          ;                                         ",
          "$0600 01                      FCB $01                            ;                                         ",
          "$0601 8600            START   LDA #$00                           ;                                         ",
          "$0603                         END                                ;                                         ",
        ]
        self.assertEqual(expected, statements)
        self.assertEqual(0x0600, program.exec_address.int)

    def test_line_length_truncates_correctly(self):
        statements = [
            "  NAM EXECADDR",
            "  ORG $0600",
            "  FCB $01",
            "START LDA #$00",
            "  END START",
        ]
        program = Program()
        program.process(statements, line_length=35)
        statements = program.get_statements()
        expected = [
          "$0000                         NAM E",
          "$0600                         ORG $",
          "$0600 01                      FCB $",
          "$0601 8600            START   LDA #",
          "$0603                         END S",
        ]
        self.assertEqual(expected, statements)
        self.assertEqual(0x0601, program.exec_address.int)

    def test_translation_error_raised_on_bad_label(self):
        statement = Statement("LABEL JMP EXIT ; comment")
        program = Program()
        with self.assertRaises(TranslationError):
            program.statements = [statement]
            program.translate_statements()

    def test_translation_error_raised_on_short_branch_too_large_backward_branch(self):
        statements = [
            "  ORG $0600",
            "START LDA #$01",
        ]
        for x in range(400):
            statements.append("    LDA #$01")
        statements.append("  BRA START")
        program = Program()
        with self.assertRaises(TranslationError) as context:
            program.process(statements)

        the_exception = context.exception
        self.assertEqual("short relative branch cannot be less than -128 bytes", the_exception.value)

    def test_translation_error_raised_on_short_branch_too_large_forward_branch(self):
        statements = [
            "  ORG $0600",
            "START BRA THEEND",
        ]
        for x in range(400):
            statements.append("    LDA #$01")
        statements.append("THEEND  LDA #$01")
        program = Program()
        with self.assertRaises(TranslationError) as context:
            program.process(statements)

        the_exception = context.exception
        self.assertEqual("short relative branch cannot be more than 127 bytes", the_exception.value)

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
