"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from fileutil.virtualfiles import BinaryFile, CassetteFile

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


class TestCassetteFile(unittest.TestCase):
    """
    A test class for the CassetteFile class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_append_eof_correct(self):
        expected = [0x55, 0x3C, 0xFF, 0x00, 0xFF, 0x55]
        buffer = []
        CassetteFile.append_eof(buffer)
        self.assertEqual(expected, buffer)

    def test_append_name_full_length_correct(self):
        name = "testfile"
        expected = [0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6C, 0x65]
        buffer = []
        checksum = CassetteFile.append_name(name, buffer)
        self.assertEqual(expected, buffer)
        self.assertEqual(864, checksum)

    def test_append_name_more_than_8_characters_correct(self):
        name = "testfiletestfile"
        expected = [0x74, 0x65, 0x73, 0x74, 0x66, 0x69, 0x6C, 0x65]
        buffer = []
        checksum = CassetteFile.append_name(name, buffer)
        self.assertEqual(expected, buffer)
        self.assertEqual(864, checksum)

    def test_append_name_less_than_8_characters_correct(self):
        name = "test"
        expected = [0x74, 0x65, 0x73, 0x74, 0x00, 0x00, 0x00, 0x00]
        buffer = []
        checksum = CassetteFile.append_name(name, buffer)
        self.assertEqual(expected, buffer)
        self.assertEqual(448, checksum)

# M A I N #####################################################################

if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
