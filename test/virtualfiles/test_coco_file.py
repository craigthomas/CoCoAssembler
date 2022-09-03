"""
Copyright (C) 2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.values import NumericValue, NoneValue
from cocoasm.virtualfiles.coco_file import CoCoFile

# C L A S S E S ###############################################################


class TestCoCoFile(unittest.TestCase):
    """
    A test class for the CoCoFile class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        self.str_format = (
            'Filename:   {}\nExtension:  {}\nFile Type:  {}\nData Type:  {}\nGap Status: {}\n'
            'Load Addr:  ${}\nExec Addr:  ${}\nData Len:   {} bytes'
        )
        self.str_format_no_gaps = (
            'Filename:   {}\nExtension:  {}\nFile Type:  {}\nData Type:  {}\n'
            'Load Addr:  ${}\nExec Addr:  ${}\nData Len:   {} bytes'
        )
        self.name = "testfile"
        self.extension = "bas"
        self.file_type = NumericValue(0)
        self.data_type = NumericValue(0)
        self.ignore_gaps = False
        self.load_addr = NumericValue(0x0E00)
        self.exec_addr = NumericValue(0x0F00)
        self.data = [0x01, 0x02, 0x03, 0x04]
        self.gaps = NoneValue()

    def compose_coco_file(self):
        return CoCoFile(
            name=self.name,
            extension=self.extension,
            type=self.file_type,
            data_type=self.data_type,
            ignore_gaps=self.ignore_gaps,
            load_addr=self.load_addr,
            exec_addr=self.exec_addr,
            data=self.data,
            gaps=self.gaps,
        )

    def compose_expected_string(self):
        return self.str_format.format(
            self.name, self.extension, self.file_type, self.data_type, self.ignore_gaps,
            self.load_addr, self.exec_addr, len(self.data)
        )

    def compose_expected_string_ignore_gaps(self):
        return self.str_format_no_gaps.format(
            self.name, self.extension, self.file_type, self.data_type,
            self.load_addr, self.exec_addr, len(self.data)
        )

    def test_str_is_correct_default_branches(self):
        result = self.compose_coco_file()
        self.ignore_gaps = "No Gaps"
        self.file_type = "BASIC"
        self.data_type = "Binary"
        self.assertEqual(self.compose_expected_string(), str(result))

    def test_str_is_correct_data_filetype(self):
        self.file_type = NumericValue(1)
        result = self.compose_coco_file()
        self.ignore_gaps = "No Gaps"
        self.file_type = "Data"
        self.data_type = "Binary"
        self.assertEqual(self.compose_expected_string(), str(result))

    def test_str_is_correct_object_filetype(self):
        self.file_type = NumericValue(2)
        result = self.compose_coco_file()
        self.ignore_gaps = "No Gaps"
        self.file_type = "Object"
        self.data_type = "Binary"
        self.assertEqual(self.compose_expected_string(), str(result))

    def test_str_is_correct_text_filetype(self):
        self.file_type = NumericValue(3)
        result = self.compose_coco_file()
        self.ignore_gaps = "No Gaps"
        self.file_type = "Text"
        self.data_type = "Binary"
        self.assertEqual(self.compose_expected_string(), str(result))

    def test_str_is_correct_ascii_datatype(self):
        self.data_type = NumericValue(0xFF)
        result = self.compose_coco_file()
        self.ignore_gaps = "No Gaps"
        self.file_type = "BASIC"
        self.data_type = "ASCII"
        self.assertEqual(self.compose_expected_string(), str(result))

    def test_str_is_correct_gaps(self):
        self.gaps = NumericValue(0xFF)
        result = self.compose_coco_file()
        self.ignore_gaps = "Gaps"
        self.file_type = "BASIC"
        self.data_type = "Binary"
        self.assertEqual(self.compose_expected_string(), str(result))

    def test_str_is_correct_ignore_gaps(self):
        self.ignore_gaps = True
        result = self.compose_coco_file()
        self.file_type = "BASIC"
        self.data_type = "Binary"
        self.assertEqual(self.compose_expected_string_ignore_gaps(), str(result))


# M A I N #####################################################################

if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
