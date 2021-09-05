"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.statement import Statement
from cocoasm.values import NumericValue, AddressValue
from cocoasm.exceptions import ParseError

# C L A S S E S ###############################################################


class TestStatement(unittest.TestCase):
    """
    A test class for the base Statement class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.statement = Statement("    JMP $FFEE ; simple statement")

    def test_set_address_sets_and_returns_address(self):
        result = self.statement.set_address(0xFFEE)
        self.assertEqual("FFEE", self.statement.code_pkg.address.hex())
        self.assertEqual(0xFFEE, result)

    def test_set_address_does_not_set_already_set_address(self):
        self.statement.code_pkg.address = NumericValue("$FFFF")
        result = self.statement.set_address(0xFFEE)
        self.assertEqual("FFFF", self.statement.code_pkg.address.hex())
        self.assertEqual(0xFFFF, result)

    def test_get_include_filename_returns_none_when_not_include(self):
        result = self.statement.get_include_filename()
        self.assertIsNone(result)

    def test_get_include_filename_returns_filename(self):
        statement = Statement("    INCLUDE testfile.asm ; include statement")
        self.assertEqual("testfile.asm", statement.get_include_filename())

    def test_parse_returns_empty_line_with_blank_line(self):
        statement = Statement("")
        self.assertTrue(statement.is_empty)

    def test_parse_returns_comment_only_with_comment_line(self):
        statement = Statement("; comment only")
        self.assertFalse(statement.is_empty)
        self.assertTrue(statement.is_comment_only)
        self.assertEqual("comment only", statement.comment)

    def test_parse_line_raises_with_bad_mnemonic(self):
        with self.assertRaises(ParseError) as context:
            Statement("    FOO $FFEE ; non-existent mnemonic")
        self.assertEqual("'[FOO] invalid mnemonic'", str(context.exception))

    def test_parse_full_line_correct(self):
        statement = Statement("LABEL JMP $FFFF ; comment")
        self.assertFalse(statement.is_empty)
        self.assertFalse(statement.is_comment_only)
        self.assertEqual("LABEL", statement.label)
        self.assertEqual("JMP", statement.mnemonic)
        self.assertEqual("$FFFF", statement.operand.operand_string)
        self.assertEqual("comment", statement.comment)

    def test_parse_FCC_correct(self):
        statement = Statement("LABEL FCC 'TEST' ; comment")
        self.assertFalse(statement.is_empty)
        self.assertFalse(statement.is_comment_only)
        self.assertEqual("LABEL", statement.label)
        self.assertEqual("FCC", statement.mnemonic)
        self.assertEqual("'TEST'", statement.operand.operand_string)
        self.assertEqual("comment", statement.comment)

    def test_parse_failure(self):
        with self.assertRaises(ParseError) as context:
            Statement("failure_to_parse")
        self.assertEqual(
            "failure_to_parse",
            str(context.exception.statement)
        )

    def test_str_correct(self):
        statement = Statement("LABEL JMP $FFFF ; comment")
        statement.set_address(0x0000)
        self.assertEqual(
            "$0000                 LABEL   JMP $FFFF                          ; comment                                 ",
            str(statement)
        )

    def test_fix_addresses_correct_for_valuetype_address(self):
        statement1 = Statement("START LDA #$00  ; load zero into A")
        statement1.set_address(0xFFEE)
        statement2 = Statement("      JMP START ; jump to start ")
        statement2.operand.value = AddressValue(0)
        statements = [statement1, statement2]
        statement2.fix_addresses(statements, 1)
        self.assertEqual("FFEE", statement2.code_pkg.additional.hex())

    def test_fix_addresses_correct_for_forward_branches(self):
        statement1 = Statement("START BRA DONE  ; branch to done")
        statement2 = Statement("      CLRA      ; clear A")
        statement3 = Statement("      CLRA      ; clear A")
        statement4 = Statement("      CLRA      ; clear A")
        statement5 = Statement("DONE  JSR $FFEE ; jump to subroutine")
        statement1.code_pkg.additional = AddressValue(4)
        statement1.code_pkg.size = 2
        statement2.code_pkg.size = 1
        statement3.code_pkg.size = 1
        statement4.code_pkg.size = 1
        statement5.code_pkg.size = 2
        statements = [statement1, statement2, statement3, statement4, statement5]
        statement1.fix_addresses(statements, 0)
        self.assertEqual("03", statement1.code_pkg.additional.hex())

    def test_fix_addresses_correct_for_reverse_branches(self):
        statement1 = Statement("START JSR $FFEE ; jump to subroutine")
        statement2 = Statement("      CLRA      ; clear A")
        statement3 = Statement("      CLRA      ; clear A")
        statement4 = Statement("      CLRA      ; clear A")
        statement5 = Statement("DONE  BRA START ; jump to start")
        statement1.code_pkg.size = 2
        statement2.code_pkg.size = 1
        statement3.code_pkg.size = 1
        statement4.code_pkg.size = 1
        statement5.code_pkg.size = 2
        statement5.code_pkg.additional = AddressValue(0)
        statements = [statement1, statement2, statement3, statement4, statement5]
        statement5.fix_addresses(statements, 4)
        self.assertEqual("F9", statement5.code_pkg.additional.hex())

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
