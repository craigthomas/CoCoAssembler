"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
This file contains the main Program class for the CoCo Assembler.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.program import Program
from cocoasm.statement import Statement

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


# M A I N #####################################################################

if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
