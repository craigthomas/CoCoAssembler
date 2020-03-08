"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import mock
import unittest

from cocoasm.instruction import InstructionBundle

# C L A S S E S ###############################################################


class TestInstructionBundle(unittest.TestCase):
    """
    A test class for the InstructionBundle class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_str(self):
        result = InstructionBundle(op_code=1, address=2, post_byte=3, additional=4)
        self.assertEqual("op_code: 1, address: 2, post_byte: 3, additional: 4", str(result))

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
