"""
Copyright (C) 2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from mock import patch

from cocoasm.virtualfiles.source_file import SourceFile, SourceFileType

# C L A S S E S ###############################################################


class TestSourceFile(unittest.TestCase):
    """
    A test class for the SourceFile class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_get_buffer_empty_on_create(self):
        source_file = SourceFile()
        self.assertEqual([], source_file.get_buffer())

    def test_set_buffer_works_correctly(self):
        source_file = SourceFile()
        buffer = [0xDE, 0xAD, 0xBE, 0xEF]
        source_file.set_buffer(buffer)
        self.assertEqual(buffer, source_file.get_buffer())

    def test_filename_set_at_creation(self):
        source_file = SourceFile(file_name="testfile")
        self.assertEqual("testfile", source_file.get_file_name())

    def test_read_when_assembly_file(self):
        with patch.object(SourceFile, 'read_assembly_contents') as read_mock:
            source_file = SourceFile(file_name="testfile")
            source_file.read_file()
            read_mock.assert_called_with("testfile")

    def test_read_when_binary_file(self):
        with patch.object(SourceFile, 'read_binary_contents') as read_mock:
            source_file = SourceFile(file_name="testfile", file_type=SourceFileType.BINARY)
            source_file.read_file()
            read_mock.assert_called_with("testfile")

    def test_write_when_binary_file(self):
        with patch.object(SourceFile, 'write_binary_contents') as write_mock:
            source_file = SourceFile(file_name="testfile", file_type=SourceFileType.BINARY)
            source_file.set_buffer([0xDE, 0xAD, 0xBE, 0xEF])
            source_file.write_file()
            write_mock.assert_called_with("testfile", [0xDE, 0xAD, 0xBE, 0xEF])


# M A I N #####################################################################

if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
