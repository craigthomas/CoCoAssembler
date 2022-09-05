"""
Copyright (C) 2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.values import NumericValue
from cocoasm.virtualfiles.disk import DiskFile
from cocoasm.virtualfiles.coco_file import CoCoFile
from cocoasm.virtualfiles.virtual_file_exceptions import VirtualFileValidationError

# C L A S S E S ###############################################################


class TestDiskFile(unittest.TestCase):
    """
    A test class for the DiskFile class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_read_sequence_buffer_empty_raises(self):
        disk_file = DiskFile()
        with self.assertRaises(VirtualFileValidationError):
            disk_file.read_sequence(0, 4)

    def test_read_sequence(self):
        buffer = [0xDE, 0xAD, 0xBE, 0xEF]
        disk_file = DiskFile(buffer=buffer)
        sequence = disk_file.read_sequence(0, 4)
        self.assertEqual(buffer, sequence)

    def test_read_sequence_with_decode(self):
        buffer = [0x74, 0x65, 0x73, 0x74]
        disk_file = DiskFile(buffer=buffer)
        sequence = disk_file.read_sequence(0, 4, decode=True)
        self.assertEqual("test", sequence)

    def test_read_word(self):
        buffer = [0xDE, 0xAD]
        disk_file = DiskFile(buffer=buffer)
        word = disk_file.read_word(0)
        self.assertEqual("DEAD", word.hex())

    def test_read_word_raises_on_buffer_too_small(self):
        buffer = [0xDE]
        disk_file = DiskFile(buffer=buffer)
        with self.assertRaises(VirtualFileValidationError):
            disk_file.read_word(0)

    def test_validate_sequence_buffer_empty_raises(self):
        disk_file = DiskFile()
        with self.assertRaises(VirtualFileValidationError):
            disk_file.validate_sequence(0, [0xDE, 0xAD, 0xBE, 0xEF])

    def test_validate_sequence_on_correct_sequence_returns_true(self):
        buffer = [0xDE, 0xAD, 0xBE, 0xEF]
        disk_file = DiskFile(buffer=buffer)
        self.assertTrue(disk_file.validate_sequence(0, buffer))

    def test_validate_sequence_on_incorrect_sequence_returns_false(self):
        buffer = [0xDE, 0xAD, 0xBE, 0xEF]
        disk_file = DiskFile(buffer=buffer)
        self.assertFalse(disk_file.validate_sequence(0, [0xDE, 0xAD, 0x00, 0x00]))

    def test_seek_granule_0_correct(self):
        disk_file = DiskFile()
        pointer = disk_file.seek_granule(0)
        self.assertEqual(0, pointer)

    def test_seek_granule_2_correct(self):
        disk_file = DiskFile()
        pointer = disk_file.seek_granule(2)
        self.assertEqual(4608, pointer)

    def test_seek_granule_more_than_33_correct(self):
        disk_file = DiskFile()
        pointer = disk_file.seek_granule(34)
        self.assertEqual(82944, pointer)

    def test_read_preamble_raises_on_empty_buffer(self):
        disk_file = DiskFile()
        with self.assertRaises(VirtualFileValidationError):
            disk_file.read_preamble(0)

    def test_read_preamble_raises_on_bad_preamble(self):
        disk_file = DiskFile(buffer=[0xDE, 0xAD, 0xBE, 0xEF])
        with self.assertRaises(VirtualFileValidationError):
            disk_file.read_preamble(0)

    def test_read_preamble_raises_when_buffer_too_small(self):
        disk_file = DiskFile(buffer=[0xDE, 0xAD])
        with self.assertRaises(VirtualFileValidationError):
            disk_file.read_preamble(0)

    def test_read_preamble_works_correct(self):
        disk_file = DiskFile(buffer=[0x00, 0xDE, 0xAD, 0xBE, 0xEF])
        preamble = disk_file.read_preamble(0)
        self.assertEqual("DEAD", preamble.data_length.hex())
        self.assertEqual("BEEF", preamble.load_addr.hex())

    def test_read_postamble_raises_on_empty_buffer(self):
        disk_file = DiskFile()
        with self.assertRaises(VirtualFileValidationError):
            disk_file.read_postamble(0)

    def test_read_postamble_raises_on_bad_postamble(self):
        disk_file = DiskFile(buffer=[0xDE, 0xAD, 0xBE, 0xEF])
        with self.assertRaises(VirtualFileValidationError):
            disk_file.read_postamble(0)

    def test_read_postamble_correct(self):
        disk_file = DiskFile(buffer=[0xFF, 0x00, 0x00, 0xDE, 0xAD])
        postamble = disk_file.read_postamble(0)
        self.assertEqual("DEAD", postamble.exec_addr.hex())

    def test_read_data_raises_on_empty_buffer(self):
        disk_file = DiskFile()
        with self.assertRaises(VirtualFileValidationError):
            disk_file.read_data(0, [], data_length=4)

    def test_read_data_small_chunk_size_correct(self):
        buffer = [0xDE, 0xAD, 0xBE, 0xEF]
        disk_file = DiskFile(buffer=buffer)
        data, pointer = disk_file.read_data(0, [], data_length=4)
        self.assertEqual(buffer, data)
        self.assertEqual(4, pointer)

    def test_read_data_small_chunk_size_skips_preamble(self):
        buffer = [0x00, 0xDE, 0xAD, 0xBE, 0xEF, 0x01]
        disk_file = DiskFile(buffer=buffer)
        data, pointer = disk_file.read_data(0, [], has_preamble=True, data_length=1)
        self.assertEqual([0x01], data)
        self.assertEqual(6, pointer)


# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
