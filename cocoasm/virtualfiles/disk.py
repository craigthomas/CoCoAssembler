"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from cocoasm.virtualfiles.virtualfile import VirtualFile, CoCoFile
from cocoasm.values import Value
from typing import NamedTuple

# C L A S S E S ###############################################################


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


class DiskFile(VirtualFile):
    FAT_OFFSET = 78592
    DIR_OFFSET = 78848
    HALF_TRACK_LEN = 2304

    def __init__(self):
        super().__init__()
        self.raw_data = []

    def is_correct_type(self):
        if not self.host_file:
            raise ValueError("No file currently open")

        if not self.read_mode:
            raise ValueError("[{}] not open for reading".format(self.filename))

        self.host_file.seek(0, 2)
        size = self.host_file.tell()
        return True if size == 161280 else False

    def list_files(self, filenames=None):
        files = []

        # Read the File Allocation Table
        self.host_file.seek(DiskFile.FAT_OFFSET, 0)
        fat = self.host_file.read(256)

        # Move through elements in the Directory Table and read them into CoCoFile objects
        self.host_file.seek(DiskFile.DIR_OFFSET, 0)
        for file_number in range(0, 72):
            next_byte = Value.create_from_byte(self.host_file.peek(1)[:1])
            if next_byte.hex() == "00" or next_byte.hex() == "FF":
                self.host_file.seek(32, 1)
            else:
                name = "{}".format(self.host_file.read(8).decode("utf-8").replace(" ", ""))
                extension = "{}".format(self.host_file.read(3).decode("utf-8"))
                file_type = Value.create_from_byte(self.host_file.read(1))
                data_type = Value.create_from_byte(self.host_file.read(1))
                starting_granule = Value.create_from_byte(self.host_file.read(1))
                current_location = self.host_file.tell()
                preamble = DiskFile.read_preamble(self.host_file, starting_granule.int)
                file_data = self.read_data(
                    self.host_file,
                    starting_granule.int,
                    has_preamble=True,
                    data_length=preamble.data_length.int,
                    fat=fat,
                )
                postamble = DiskFile.read_postamble(self.host_file)
                self.host_file.seek(current_location, 0)
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
                self.host_file.seek(19, 1)

        return files

    @classmethod
    def seek_granule(cls, file, granule):
        """
        Seeks to the specified granule in the disk image. Modifies the file
        object pointer to start at the specified granule.

        :param file: the file object to use
        :param granule: the granule to seek to
        """
        granule_offset = DiskFile.HALF_TRACK_LEN * granule
        if granule > 33:
            granule_offset += DiskFile.HALF_TRACK_LEN * 2
        file.seek(granule_offset, 0)

    @classmethod
    def read_preamble(cls, file, starting_granule):
        """
        Reads the preamble data for the file. The preamble is a collection of 5
        bytes at the start of a binary file:

            byte 0 - always $00
            byte 1,2 - the data length of the file
            byte 3,4 - the load address for the file

        :param file: the file object to modify
        :param starting_granule: the granule number that contains the preamble
        :return: a populated Preamble object
        """
        DiskFile.seek_granule(file, starting_granule)
        preamble_flag = Value.create_from_byte(file.read(1))
        if preamble_flag.hex() != "00":
            raise ValueError("Invalid preamble flag {}".format(preamble_flag.hex()))
        return Preamble(
            data_length=Value.create_from_byte(file.read(2)),
            load_addr=Value.create_from_byte(file.read(2))
        )

    @classmethod
    def read_postamble(cls, file):
        """
        Reads the postamble of a binary file. The postamble is a collection of
        5 bytes as follows:

            byte 0 - always $FF
            byte 1,2 - always $00, $00
            byte 3,4 - the exec address of the binary file

        :param file: the file object to modify
        :return: a populated Postamble object
        """
        postamble_flag = Value.create_from_byte(file.read(1))
        if postamble_flag.hex() != "FF":
            raise ValueError("Invalid first postamble flag {}".format(postamble_flag.hex()))
        postamble_flag = Value.create_from_byte(file.read(2))
        if postamble_flag.hex() != "00":
            raise ValueError("Invalid second postamble flag {}".format(postamble_flag.hex()))
        return Postamble(
            exec_addr=Value.create_from_byte(file.read(2)),
        )

    @classmethod
    def read_data(cls, file, starting_granule, has_preamble=False, data_length=0, fat=[]):
        """
        Reads a collection of data from a disk image.

        :param file: the file object containing data to read from
        :param starting_granule: the starting granule for the file
        :param has_preamble: whether there is a preamble to be read
        :param data_length: the length of data to read
        :param fat: the File Allocation Table data for the disk
        :return: the raw data from the specified file
        """
        DiskFile.seek_granule(file, starting_granule)
        file_data = []
        chunk_size = DiskFile.HALF_TRACK_LEN

        # Skip over preamble if it exists
        if has_preamble:
            file.read(5)
            chunk_size -= 5

        # Check to see if we are reading more than one granule
        if data_length > chunk_size:
            for _ in range(chunk_size):
                file_data.append(Value.create_from_byte(file.read(1)).int)
                data_length -= 1
            next_granule = fat[starting_granule]
            file_data.extend(DiskFile.read_data(file, next_granule, data_length=data_length, fat=fat))
        else:
            for _ in range(data_length):
                file_data.append(Value.create_from_byte(file.read(1)).int)
        return file_data

    def save_to_host_file(self, coco_file):
        pass

# E N D   O F   F I L E #######################################################
