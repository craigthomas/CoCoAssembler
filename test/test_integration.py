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

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
