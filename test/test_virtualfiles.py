"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from fileutil.virtualfiles import BinaryFile

# C L A S S E S ###############################################################


class TestBinaryFile(unittest.TestCase):
    """
    A test class for the BinaryFile class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_list_files_returns_empty_list(self):
        binary_file = BinaryFile()
        result = binary_file.list_files()
        self.assertEqual([], result)


# M A I N #####################################################################

if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
