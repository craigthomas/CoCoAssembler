"""
Copyright (C) 2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from typing import NamedTuple

from cocoasm.virtualfiles.coco_file import CoCoFile
from cocoasm.virtualfiles.virtual_file_container import VirtualFileContainer
from cocoasm.values import Value, NumericValue
from cocoasm.virtualfiles.virtual_file_exceptions import VirtualFileValidationError

# C L A S S E S ###############################################################


class DiskConstants(object):
    FAT_OFFSET = 78592
    DIR_OFFSET = 78848
    HALF_TRACK_LEN = 2304


class Preamble(NamedTuple):
    """
    The Preamble class is used to store information relating to a binary file
    on a disk image. The Preamble only contains the load address and the length
    of data for the binary file.
    """
    load_addr: Value = None
    data_length: Value = None


class Postamble(NamedTuple):
    """
    The Postamble class is used to store information relating t a binary file
    on a disk image. The Postamble is stored at the end of a binary file and
    contains the exec address for the binary.
    """
    exec_addr: Value = None


class DiskFile(VirtualFileContainer):
    def __init__(self, buffer=None):
        super().__init__(buffer=buffer)

    def read_sequence(self, pointer, length, decode=False):
        """
        Reads a sequence of bytes of the specified length and returns a list like
        object that contains the sequence read.

        :param pointer: the byte number in to the buffer to start the read
        :param length: the number of bytes to read
        :param decode: whether to UTF-8 decode the resultant data
        :return: a list like object of the bytes read
        """
        sequence = []
        if length > len(self.buffer) or (len(self.buffer[pointer:]) < length):
            raise VirtualFileValidationError("Unable to read sequence of length {}".format(length))

        for file_name_pointer in range(pointer, pointer + length):
            sequence.append(self.buffer[file_name_pointer])
        return bytearray(sequence).decode("utf-8") if decode else sequence

    def read_word(self, pointer):
        """
        Reads a 16-bit value from the buffer starting at the specified
        pointer offset.

        :param pointer: the offset into the buffer to read from
        :return: the NumericValue read
        """
        if len(self.buffer) < 2 or (len(self.buffer[pointer:]) < 2):
            raise VirtualFileValidationError("Unable to read word - insufficient bytes in buffer")

        word_int = int(self.buffer[pointer])
        word_int = word_int << 8
        word_int |= int(self.buffer[pointer + 1])
        return NumericValue(word_int)

    def validate_sequence(self, pointer, sequence):
        """
        Ensures that the next group of bytes read matches the sequence specified.
        Advances the buffer down the object

        :param pointer: a pointer into the data of the file
        :param sequence: an array-like list of bytes to read in the sequence
        :return: True if the bytes follow the sequence specified, false otherwise
        """
        if len(self.buffer[pointer:]) < len(sequence):
            raise VirtualFileValidationError("Not enough bytes in buffer to validate sequence")

        for sequence_pointer in range(len(sequence)):
            byte_read = NumericValue(self.buffer[pointer + sequence_pointer])
            if byte_read.int != sequence[sequence_pointer]:
                return False
        return True

    def list_files(self, filenames=None):
        files = []

        # Read the File Allocation Table
        fat = self.buffer[DiskConstants.FAT_OFFSET:DiskConstants.FAT_OFFSET + 256]

        # Move through elements in the Directory Table and read them into CoCoFile objects
        pointer = DiskConstants.DIR_OFFSET
        for _ in range(0, 72):
            next_byte = NumericValue(self.buffer[pointer])
            if next_byte.hex() == "00" or next_byte.hex() == "FF":
                pointer += 32
            else:
                name = "{}".format(self.read_sequence(pointer, 8, decode=True).replace(" ", ""))
                pointer += 8
                extension = "{}".format(self.read_sequence(pointer, 3, decode=True))
                pointer += 3
                file_type = NumericValue(self.buffer[pointer])
                pointer += 1
                data_type = NumericValue(self.buffer[pointer])
                pointer += 1
                starting_granule = NumericValue(self.buffer[pointer])
                pointer += 1

                preamble = self.read_preamble(starting_granule.int)

                file_data, pointer = self.read_data(
                    starting_granule.int,
                    fat,
                    has_preamble=True,
                    data_length=preamble.data_length.int,
                )

                postamble = self.read_postamble(pointer)
                pointer += 5

                coco_file = CoCoFile(
                    name=name,
                    extension=extension,
                    type=file_type,
                    data_type=data_type,
                    load_addr=preamble.load_addr,
                    exec_addr=postamble.exec_addr,
                    data=file_data,
                    ignore_gaps=True
                )
                files.append(coco_file)
                pointer += 19

        return files

    @staticmethod
    def seek_granule(granule):
        """
        Returns a pointer to the start of the specified granule in the buffer.

        :param granule: the granule to seek to
        :return: a pointer to the specified granule
        """
        granule_offset = DiskConstants.HALF_TRACK_LEN * granule
        if granule > 33:
            granule_offset += DiskConstants.HALF_TRACK_LEN * 2
        return granule_offset

    def read_preamble(self, starting_granule):
        """
        Reads the preamble data for the file. The preamble is a collection of 5
        bytes at the start of a binary file:

            byte 0 - always $00
            byte 1,2 - the data length of the file
            byte 3,4 - the load address for the file

        :param starting_granule: the granule number that contains the preamble
        :return: a populated Preamble object
        """
        pointer = self.seek_granule(starting_granule)
        if not self.validate_sequence(pointer, [0x00]):
            raise VirtualFileValidationError("Invalid preamble flag")

        return Preamble(
            data_length=self.read_word(pointer + 1),
            load_addr=self.read_word(pointer + 3),
        )

    def read_postamble(self, pointer):
        """
        Reads the postamble of a binary file. The postamble is a collection of
        5 bytes as follows:

            byte 0 - always $FF
            byte 1,2 - always $00, $00
            byte 3,4 - the exec address of the binary file

        :param pointer: a pointer to the postamble data
        :return: a populated Postamble object
        """
        if not self.validate_sequence(pointer, [0xFF, 0x00, 0x00]):
            raise VirtualFileValidationError("Invalid postamble flags")

        return Postamble(
            exec_addr=self.read_word(pointer + 3),
        )

    def read_data(self, starting_granule, fat, has_preamble=False, data_length=0):
        """
        Reads a collection of data from a disk image.

        :param starting_granule: the starting granule for the file
        :param has_preamble: whether there is a preamble to be read
        :param data_length: the length of data to read
        :param fat: the File Allocation Table data for the disk
        :return: the raw data from the specified file and the pointer to the end of the file
        """
        pointer = self.seek_granule(starting_granule)
        file_data = []
        chunk_size = DiskConstants.HALF_TRACK_LEN

        if len(self.buffer[pointer:]) < data_length:
            raise VirtualFileValidationError("Unable to read data - insufficient bytes in buffer")

        # Skip over preamble if it exists
        if has_preamble:
            pointer += 5
            chunk_size -= 5

        # Check to see if we are reading more than one granule
        if data_length > chunk_size:
            for _ in range(chunk_size):
                file_data.append(self.buffer[pointer])
                data_length -= 1
                pointer += 1
            next_granule = fat[starting_granule]
            granule_data, pointer = self.read_data(next_granule, fat, data_length=data_length, has_preamble=False)
            file_data.extend(granule_data)
        else:
            for _ in range(data_length):
                file_data.append(self.buffer[pointer])
                pointer += 1
        return file_data, pointer

    def add_file(self, coco_file):
        pass


# E N D   O F   F I L E #######################################################
