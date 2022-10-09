"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from mock import patch

from cocoasm.values import NumericValue
from cocoasm.virtualfiles.disk import DiskFile, DiskConstants, ASCIIPreamble, Postamble, MLPreamble, BasicPreamble
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
        disk_file = DiskFile(buffer=[])
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
        disk_file = DiskFile(buffer=[])
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

    def test_read_data_raises_on_empty_buffer(self):
        disk_file = DiskFile(buffer=[])
        preamble = MLPreamble()
        with self.assertRaises(VirtualFileValidationError):
            disk_file.read_data(0, [], preamble, data_length=4)

    def test_read_data_small_chunk_size_correct(self):
        buffer = [0xDE, 0xAD, 0xBE, 0xEF]
        disk_file = DiskFile(buffer=buffer)
        data, pointer = disk_file.read_data(0, [], None, data_length=4)
        self.assertEqual(buffer, data)
        self.assertEqual(4, pointer)

    def test_read_data_small_chunk_size_skips_preamble(self):
        buffer = [0x00, 0xDE, 0xAD, 0xBE, 0xEF, 0x01]
        disk_file = DiskFile(buffer=buffer)
        preamble = MLPreamble()
        data, pointer = disk_file.read_data(0, [], preamble, data_length=1)
        self.assertEqual([0x01], data)
        self.assertEqual(6, pointer)

    def test_read_data_multi_chunk_correct(self):
        buffer = [0x00, 0xDE, 0xAD, 0xBE, 0xEF]
        buffer.extend([0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88, 0x99] * 300)
        disk_file = DiskFile(buffer=buffer)
        preamble = MLPreamble()
        data, pointer = disk_file.read_data(0, [0x01], preamble, data_length=3000)
        self.assertEqual(buffer[5:], data)
        self.assertEqual(3005, pointer)

    def test_directory_entry_in_use_raises_on_negative_entry(self):
        disk_file = DiskFile()
        with self.assertRaises(VirtualFileValidationError):
            disk_file.directory_entry_in_use(-1)

    def test_directory_entry_in_use_raises_on_value_too_high(self):
        disk_file = DiskFile()
        with self.assertRaises(VirtualFileValidationError):
            disk_file.directory_entry_in_use(73)

    def test_directory_entry_in_use_correct_when_not_in_use(self):
        disk_file = DiskFile(buffer=[0x00] * 161280)
        for entry in range(0, 72):
            self.assertFalse(disk_file.directory_entry_in_use(entry))

        disk_file = DiskFile(buffer=[0xFF] * 161280)
        for entry in range(0, 72):
            self.assertFalse(disk_file.directory_entry_in_use(entry))

    def test_directory_entry_in_use_correct_when_in_use(self):
        disk_file = DiskFile(buffer=[0xDE] * 161280)
        for entry in range(0, 72):
            self.assertTrue(disk_file.directory_entry_in_use(entry))

    def test_find_empty_directory_entry_returns_negative_when_all_in_use(self):
        disk_file = DiskFile(buffer=[0xDE] * 161280)
        self.assertEqual(-1, disk_file.find_empty_directory_entry())

    def test_find_empty_directory_entry_returns_correct_when_none_in_use(self):
        disk_file = DiskFile(buffer=[0x00] * 161280)
        self.assertEqual(0, disk_file.find_empty_directory_entry())

    def test_granule_in_use_raises_on_negative_granule(self):
        disk_file = DiskFile(buffer=[0xDE] * 161280)
        with self.assertRaises(VirtualFileValidationError):
            disk_file.granule_in_use(-1)

    def test_granule_in_use_raises_on_granule_too_large(self):
        disk_file = DiskFile(buffer=[0xDE] * 161280)
        with self.assertRaises(VirtualFileValidationError):
            disk_file.granule_in_use(68)

    def test_granule_in_use_correct_when_not_in_use(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        for granule in range(0, 67):
            self.assertFalse(disk_file.granule_in_use(granule))

    def test_granule_in_use_correct_when_in_use(self):
        disk_file = DiskFile(buffer=[0xDE] * 161280)
        for granule in range(0, 67):
            self.assertTrue(disk_file.granule_in_use(granule))

    def test_find_empty_granule_raises_when_no_granules_free(self):
        disk_file = DiskFile(buffer=[0xDE] * 161280)
        with self.assertRaises(VirtualFileValidationError):
            disk_file.find_empty_granule()

    def test_find_empty_granule_returns_correct_when_granules_free(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        self.assertEqual(32, disk_file.find_empty_granule())

    def test_find_empty_granule_returns_correct_when_granules_free_with_different_preferred_granules(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280, granule_fill_order=[x for x in range(68)])
        self.assertEqual(0, disk_file.find_empty_granule())

    def test_find_empty_granule_raises_when_fill_order_too_small(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280, granule_fill_order=[0])
        with self.assertRaises(VirtualFileValidationError):
            disk_file.find_empty_granule()

    def test_granules_needed_empty_file(self):
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        self.assertEqual(1, DiskFile.calculate_granules_needed([], preamble, None))

    def test_granules_needed_single_byte_file(self):
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        self.assertEqual(1, DiskFile.calculate_granules_needed([], preamble, None))

    def test_granules_needed_single_granule(self):
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        self.assertEqual(1, DiskFile.calculate_granules_needed([0x00] * (DiskConstants.HALF_TRACK_LEN - 11), preamble, None))

    def test_granules_needed_two_granules(self):
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        self.assertEqual(2, DiskFile.calculate_granules_needed([0x00] * DiskConstants.HALF_TRACK_LEN, preamble, None))

    def test_sectors_needed_zero_byte_file_correct(self):
        self.assertEqual(1, DiskFile.calculate_sectors_needed(0))

    def test_sectors_needed_single_sector(self):
        self.assertEqual(1, DiskFile.calculate_sectors_needed(DiskConstants.BYTES_PER_SECTOR - 11))

    def test_sectors_needed_two_sectors(self):
        self.assertEqual(2, DiskFile.calculate_sectors_needed(DiskConstants.BYTES_PER_SECTOR))

    def test_calculate_last_sector_bytes_used_zero_length_file_correct(self):
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        self.assertEqual(5, DiskFile.calculate_last_sector_bytes_used([], preamble, None))

    def test_calculate_last_sector_bytes_used_large_file_correct(self):
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        self.assertEqual(10, DiskFile.calculate_last_sector_bytes_used([0x00] * 2565, preamble, None))

    @patch("cocoasm.virtualfiles.disk.DiskConstants.DIR_OFFSET", 0)
    def test_write_dir_entry(self):
        disk_file = DiskFile(buffer=[0x00] * 32)
        coco_file = CoCoFile(
            name="test    ",
            extension="bas",
            type=NumericValue(0x99),
            data_type=NumericValue(0x10),
        )
        disk_file.write_dir_entry(0, coco_file, 0x20, 0x22)
        self.assertEqual(
            [0x54, 0x45, 0x53, 0x54, 0x20, 0x20, 0x20, 0x20, 0x42, 0x41, 0x53, 0x99, 0x10, 0x20, 0x00, 0x22,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            disk_file.get_buffer()
        )

    @patch("cocoasm.virtualfiles.disk.DiskConstants.DIR_OFFSET", 0)
    def test_write_dir_entry_space_fills_name(self):
        disk_file = DiskFile(buffer=[0x00] * 32)
        coco_file = CoCoFile(
            name="test",
            extension="bas",
            type=NumericValue(0x99),
            data_type=NumericValue(0x10),
        )
        disk_file.write_dir_entry(0, coco_file, 0x20, 0x22)
        self.assertEqual(
            [0x54, 0x45, 0x53, 0x54, 0x20, 0x20, 0x20, 0x20, 0x42, 0x41, 0x53, 0x99, 0x10, 0x20, 0x00, 0x22,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            disk_file.get_buffer()
        )

    def test_calculate_last_granules_sectors_used_empty_file_data(self):
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        self.assertEqual(1, DiskFile.calculate_last_granules_sectors_used([], preamble, None))

    def test_calculate_last_granules_sectors_used_less_than_one_sector(self):
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        self.assertEqual(1, DiskFile.calculate_last_granules_sectors_used([0x00] * 245, preamble, None))

    def test_calculate_last_granules_sectors_used_more_than_one_sector(self):
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        self.assertEqual(2, DiskFile.calculate_last_granules_sectors_used([0x00] * 500, preamble, None))

    def test_write_bytes_to_buffer_empty_bytes_does_nothing(self):
        disk_file = DiskFile(buffer=[0xAA] * 5)
        disk_file.write_bytes_to_buffer(0, [])
        self.assertEqual([0xAA, 0xAA, 0xAA, 0xAA, 0xAA], disk_file.get_buffer())

    def test_write_bytes_works_correctly(self):
        disk_file = DiskFile(buffer=[0xAA] * 5)
        disk_file.write_bytes_to_buffer(0, [0xDE, 0xAD, 0xBE, 0xEF])
        self.assertEqual([0xDE, 0xAD, 0xBE, 0xEF, 0xAA], disk_file.get_buffer())

    @patch("cocoasm.virtualfiles.disk.DiskConstants.FAT_OFFSET", 0)
    def test_to_fat_no_allocated_granules_does_nothing(self):
        disk_file = DiskFile(buffer=[0x00] * DiskConstants.TOTAL_GRANULES)
        disk_file.write_to_fat([], 1)
        self.assertEqual([0x00] * DiskConstants.TOTAL_GRANULES, disk_file.get_buffer())

    @patch("cocoasm.virtualfiles.disk.DiskConstants.FAT_OFFSET", 0)
    def test_to_fat_single_granule_correct(self):
        disk_file = DiskFile(buffer=[0x00] * DiskConstants.TOTAL_GRANULES)
        disk_file.write_to_fat([2], 1)
        self.assertEqual(
            [0x00, 0x00, 0xC1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00
             ]
            , disk_file.get_buffer()
        )

    @patch("cocoasm.virtualfiles.disk.DiskConstants.FAT_OFFSET", 0)
    def test_to_fat_single_granule_correct(self):
        disk_file = DiskFile(buffer=[0x00] * DiskConstants.TOTAL_GRANULES)
        disk_file.write_to_fat([2, 4, 6, 8], 1)
        self.assertEqual(
            [0x00, 0x00, 0x04, 0x00, 0x06, 0x00, 0x08, 0x00, 0xC1, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00
             ]
            , disk_file.get_buffer()
        )

    def test_list_files_raises_on_incorrect_size(self):
        disk_file = DiskFile(buffer=[0xFF] * 256)
        with self.assertRaises(VirtualFileValidationError):
            disk_file.list_files()

    def test_list_files_no_entries_returns_empty_list(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        self.assertEqual([], disk_file.list_files())

    def test_list_files_single_entry_correct(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        disk_file.write_bytes_to_buffer(
            DiskConstants.DIR_OFFSET,
            [0x54, 0x45, 0x53, 0x54, 0x20, 0x20, 0x20, 0x20, 0x42, 0x49, 0x4E, 0x02, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        )
        disk_file.write_bytes_to_buffer(
            0,
            [0x00, 0x00, 0x01, 0xDE, 0xAD, 0xAA, 0xFF, 0x00, 0x00, 0xBE, 0xEF]
        )
        coco_files = disk_file.list_files()
        self.assertEqual(1, len(coco_files))
        coco_file = coco_files[0]
        self.assertEqual("TEST", coco_file.name)
        self.assertEqual("BIN", coco_file.extension)
        self.assertEqual(0x02, coco_file.type.int)
        self.assertEqual(0x00, coco_file.data_type.int)
        self.assertEqual("DEAD", coco_file.load_addr.hex())
        self.assertEqual("BEEF", coco_file.exec_addr.hex())
        self.assertEqual([0xAA], coco_file.data)

    def test_list_files_multiple_entries_correct(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        disk_file.write_bytes_to_buffer(
            DiskConstants.DIR_OFFSET,
            [0x54, 0x45, 0x53, 0x54, 0x20, 0x20, 0x20, 0x20, 0x42, 0x49, 0x4E, 0x02, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x53, 0x45, 0x43, 0x4F, 0x4E, 0x44, 0x20, 0x20, 0x42, 0x41, 0x53, 0x00, 0x00, 0x01, 0x00, 0x0C,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x41, 0x53, 0x43, 0x49, 0x49, 0x20, 0x20, 0x20, 0x41, 0x53, 0x43, 0x00, 0xFF, 0x02, 0x00, 0x0C,
             0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,]
        )
        disk_file.write_bytes_to_buffer(
            DiskFile.seek_granule(0),
            [0x00, 0x00, 0x01, 0xDE, 0xAD, 0xAA, 0xFF, 0x00, 0x00, 0xBE, 0xEF]
        )
        disk_file.write_bytes_to_buffer(
            DiskFile.seek_granule(1),
            [0xFF, 0x00, 0x09, 0xCA, 0xFE, 0xBB, 0xBB, 0xFF, 0x00, 0x00, 0xBA, 0xBE]
        )
        disk_file.write_bytes_to_buffer(
            DiskFile.seek_granule(2),
            [0xFF, 0x00, 0x09, 0xCA, 0xFE, 0xBB, 0xBB, 0xFF, 0x00, 0x00, 0xBA, 0xBE]
        )
        disk_file.write_bytes_to_buffer(
            DiskConstants.FAT_OFFSET,
            [0xC1, 0xC1, 0xC1]
        )
        coco_files = disk_file.list_files()
        self.assertEqual(3, len(coco_files))
        coco_file = coco_files[0]
        self.assertEqual("TEST", coco_file.name)
        self.assertEqual("BIN", coco_file.extension)
        self.assertEqual(0x02, coco_file.type.int)
        self.assertEqual(0x00, coco_file.data_type.int)
        self.assertEqual("DEAD", coco_file.load_addr.hex())
        self.assertEqual("BEEF", coco_file.exec_addr.hex())
        self.assertEqual([0xAA], coco_file.data)

        coco_file = coco_files[1]
        self.assertEqual("SECOND", coco_file.name)
        self.assertEqual("BAS", coco_file.extension)
        self.assertEqual(0x00, coco_file.type.int)
        self.assertEqual(0x00, coco_file.data_type.int)
        self.assertEqual("", coco_file.load_addr.hex())
        self.assertEqual("", coco_file.exec_addr.hex())
        self.assertEqual([0xCA, 0xFE, 0xBB, 0xBB, 0xFF, 0x00, 0x00, 0xBA, 0xBE], coco_file.data)

        coco_file = coco_files[2]
        self.assertEqual("ASCII", coco_file.name)
        self.assertEqual("ASC", coco_file.extension)
        self.assertEqual(0x00, coco_file.type.int)
        self.assertEqual(0xFF, coco_file.data_type.int)
        self.assertEqual("", coco_file.load_addr.hex())
        self.assertEqual("", coco_file.exec_addr.hex())
        self.assertEqual([0xFF, 0x00, 0x09, 0xCA, 0xFE, 0xBB, 0xBB, 0xFF, 0x00, 0x00, 0xBA, 0xBE], coco_file.data)

    def test_write_to_granules_does_nothing_on_empty_allocated_granules(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        disk_file.write_to_granules([0x00] * 512, [], None, None)
        self.assertEqual([0xFF] * 161280, disk_file.get_buffer())

    def test_write_to_granules_correct_no_preamble(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        disk_file.write_to_granules([0x00] * 234, [0], None, None)
        expected = [0x00] * 234
        expected.extend([0xFF] * 161046)
        self.assertEqual(expected, disk_file.get_buffer())

    def test_write_to_granules_correct_with_preamble(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        preamble = MLPreamble()
        preamble.load_addr = NumericValue("$DEAD")
        preamble.data_length = NumericValue("$BEEF")
        postamble = Postamble()
        postamble.exec_addr = NumericValue("$CAFE")
        disk_file.write_to_granules([0x00] * 234, [0], preamble, postamble)
        expected = [0x00, 0xBE, 0xEF, 0xDE, 0xAD]
        expected.extend([0x00] * 234)
        expected.extend([0xFF, 0x00, 0x00, 0xCA, 0xFE])
        expected.extend([0xFF] * 161036)
        self.assertEqual(expected, disk_file.get_buffer())

    def test_write_to_granules_multiple_granules_correct(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        disk_file.write_to_granules([0x00] * 2305, [0, 2], None, None)
        expected = [0xFF] * 161280
        for pointer in range(0, 2304):
            expected[pointer] = 0x00
        expected[4608] = 0x00
        self.assertEqual(expected, disk_file.get_buffer())

    def test_add_file_raises_if_insufficient_granules_available(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        disk_file.write_bytes_to_buffer(
            DiskConstants.FAT_OFFSET,
            [0x00, 0x00, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0,
             0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0,
             0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0,
             0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0, 0xC0]
        )
        with self.assertRaises(VirtualFileValidationError):
            disk_file.add_file(
                CoCoFile(
                    name="TEST    ",
                    extension="BIN",
                    type=NumericValue(0),
                    load_addr=NumericValue("$0123"),
                    exec_addr=NumericValue("$4567"),
                    data=[0x00] * 5000,
                )
            )

    def test_add_file_raises_if_no_directory_entry_available(self):
        disk_file = DiskFile(buffer=[0xFF] * 161280)
        disk_file.write_bytes_to_buffer(
            DiskConstants.DIR_OFFSET,
            [0xAA] * 2304
        )
        with self.assertRaises(VirtualFileValidationError):
            disk_file.add_file(
                CoCoFile(
                    name="TEST    ",
                    extension="BIN",
                    type=NumericValue(0),
                    load_addr=NumericValue("$0123"),
                    exec_addr=NumericValue("$4567"),
                    data=[0x00] * 5000,
                )
            )

    def test_calculate_file_length_single_granule_single_sector_correct(self):
        result = DiskFile.calculate_file_length(0, [0xC1], 256)
        self.assertEqual(256, result)

    def test_calculate_file_length_single_granule_multiple_sectors_correct(self):
        result = DiskFile.calculate_file_length(0, [0xC2], 256)
        self.assertEqual(512, result)

    def test_calculate_file_length_mutiple_granules_multiple_sectors_correct(self):
        result = DiskFile.calculate_file_length(0, [0x01, 0x02, 0xC2], 256)
        self.assertEqual(4608 + 512, result)


class TestMLPreamble(unittest.TestCase):
    """
    A test class for the MLPreamble class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_ml_preamble_true_is_ml(self):
        preamble = MLPreamble()
        self.assertTrue(preamble.is_ml())

    def test_read_ml_preamble_raises_on_empty_buffer(self):
        preamble = MLPreamble()
        with self.assertRaises(VirtualFileValidationError):
            preamble.read([], 0)

    def test_read_ml_preamble_raises_on_bad_preamble(self):
        preamble = MLPreamble()
        with self.assertRaises(VirtualFileValidationError):
            preamble.read([0xDE, 0xAD, 0xBE, 0xEF, 0x00], 0)

    def test_read_ml_preamble_raises_when_buffer_too_small(self):
        preamble = MLPreamble()
        with self.assertRaises(VirtualFileValidationError):
            preamble.read([0xDE, 0xAD], 0)

    def test_read_ml_preamble_works_correct(self):
        preamble = MLPreamble()
        pointer = preamble.read([0x00, 0xDE, 0xAD, 0xBE, 0xEF], 0)
        self.assertEqual("DEAD", preamble.data_length.hex())
        self.assertEqual("BEEF", preamble.load_addr.hex())
        self.assertEqual(5, pointer)

    def test_write_ml_preamble_fails_when_not_enough_space(self):
        preamble = MLPreamble()
        buffer = [1, 2, 3]
        with self.assertRaises(VirtualFileValidationError):
            preamble.write(buffer, 0)

    def test_write_ml_preamble_works_correctly(self):
        preamble = MLPreamble()
        preamble.data_length = NumericValue(0xDEAD)
        preamble.load_addr = NumericValue(0xBEEF)
        buffer = [0x00] * 5
        preamble.write(buffer, 0)
        self.assertEqual([0x00, 0xDE, 0xAD, 0xBE, 0xEF], buffer)

    def test_write_ml_preamble_get_data_length_works_correctly(self):
        preamble = MLPreamble()
        preamble.data_length = NumericValue(0xDEAD)
        preamble.load_addr = NumericValue(0xBEEF)
        buffer = [0x00] * 5
        preamble.write(buffer, 0)
        self.assertEqual(0xDEAD, preamble.get_data_length())


class TestBasicPreamble(unittest.TestCase):
    """
    A test class for the BasicPreamble class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_basic_preamble_true_is_ml(self):
        preamble = BasicPreamble()
        self.assertFalse(preamble.is_ml())

    def test_read_basic_preamble_raises_on_empty_buffer(self):
        preamble = BasicPreamble()
        with self.assertRaises(VirtualFileValidationError):
            preamble.read([], 0)

    def test_read_basic_preamble_raises_on_bad_preamble(self):
        preamble = BasicPreamble()
        with self.assertRaises(VirtualFileValidationError):
            preamble.read([0xDE, 0xAD, 0xBE, 0xEF, 0x00], 0)

    def test_read_basic_preamble_raises_when_buffer_too_small(self):
        preamble = BasicPreamble()
        with self.assertRaises(VirtualFileValidationError):
            preamble.read([0xDE, 0xAD], 0)

    def test_read_basic_preamble_works_correct(self):
        preamble = BasicPreamble()
        pointer = preamble.read([0xFF, 0xDE, 0xAD], 0)
        self.assertEqual("DEAD", preamble.data_length.hex())
        self.assertEqual(3, pointer)

    def test_write_basic_preamble_fails_when_not_enough_space(self):
        preamble = BasicPreamble()
        buffer = [1, 2]
        with self.assertRaises(VirtualFileValidationError):
            preamble.write(buffer, 0)

    def test_write_basic_preamble_works_correctly(self):
        preamble = BasicPreamble()
        preamble.data_length = NumericValue(0xDEAD)
        buffer = [0x00] * 3
        preamble.write(buffer, 0)
        self.assertEqual([0xFF, 0xDE, 0xAD], buffer)

    def test_write_basic_preamble_get_data_length_works_correctly(self):
        preamble = BasicPreamble()
        preamble.data_length = NumericValue(0xDEAD)
        buffer = [0x00] * 3
        preamble.write(buffer, 0)
        self.assertEqual(0xDEAD, preamble.get_data_length())


class TestASCIIPreamble(unittest.TestCase):
    """
    A test class for the BasicPreamble class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_ascii_preamble_true_is_ml(self):
        preamble = ASCIIPreamble()
        self.assertFalse(preamble.is_ml())

    def test_read_ascii_preamble_works_correct(self):
        preamble = ASCIIPreamble()
        pointer = preamble.read([0xFF, 0xDE, 0xAD], 0)
        self.assertEqual(0, preamble.data_length.int)
        self.assertEqual(0, pointer)

    def test_write_ascii_preamble_works_correctly(self):
        preamble = ASCIIPreamble()
        buffer = [0x00] * 3
        preamble.write(buffer, 0)
        self.assertEqual([0x00, 0x00, 0x00], buffer)


class TestPostamble(unittest.TestCase):
    """
    A test class for the BasicPreamble class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """

    def test_read_raises_on_first_invalid_byte(self):
        postamble = Postamble()
        with self.assertRaises(VirtualFileValidationError):
            postamble.read([0xAA, 0x00, 0x00, 0xDE, 0xAD], 0)

    def test_read_raises_on_second_invalid_byte(self):
        postamble = Postamble()
        with self.assertRaises(VirtualFileValidationError):
            postamble.read([0xFF, 0xAA, 0x00, 0xDE, 0xAD], 0)

    def test_read_raises_on_third_invalid_byte(self):
        postamble = Postamble()
        with self.assertRaises(VirtualFileValidationError):
            postamble.read([0xFF, 0x00, 0xAA, 0xDE, 0xAD], 0)

    def test_read_returns_correct_pointer(self):
        postamble = Postamble()
        result = postamble.read([0xFF, 0x00, 0x00, 0xDE, 0xAD], 0)
        self.assertEqual(5, result)
        self.assertEqual(0xDEAD, postamble.exec_addr.int)

    def test_write_postamble_fails_when_not_enough_space(self):
        postamble = Postamble()
        buffer = [1, 2]
        with self.assertRaises(VirtualFileValidationError):
            postamble.write(buffer, 0)

    def test_write_postamble_works_correctly(self):
        postamble = Postamble()
        postamble.exec_addr = NumericValue(0xDEAD)
        buffer = [0x00] * 5
        postamble.write(buffer, 0)
        self.assertEqual([0xFF, 0x00, 0x00, 0xDE, 0xAD], buffer)

    def test_read_postamble_raises_on_empty_buffer(self):
        postamble = Postamble()
        with self.assertRaises(VirtualFileValidationError):
            postamble.read([], 0)

    def test_read_postamble_correct(self):
        postamble = Postamble()
        postamble.read([0xFF, 0x00, 0x00, 0xDE, 0xAD], 0)
        self.assertEqual("DEAD", postamble.exec_addr.hex())


# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
