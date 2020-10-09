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
    load_addr: Value = None
    data_length: Value = None


class Postamble(NamedTuple):
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
        fat = []

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
                name = "{}.{}".format(
                    self.host_file.read(8).decode("utf-8").replace(" ", ""),
                    self.host_file.read(3).decode("utf-8")
                )
                file_type = Value.create_from_byte(self.host_file.read(1))
                data_type = Value.create_from_byte(self.host_file.read(1))
                starting_granule = Value.create_from_byte(self.host_file.read(1))
                current_location = self.host_file.tell()
                preamble = DiskFile.read_preamble(self.host_file, starting_granule.int)
                print("preamble data length: {}".format(preamble.data_length.hex()))
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
        granule_offset = DiskFile.HALF_TRACK_LEN * granule
        if granule > 33:
            granule_offset += DiskFile.HALF_TRACK_LEN * 2
        file.seek(granule_offset, 0)

    @classmethod
    def read_preamble(cls, file, starting_granule):
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
        Reads the post-amble of a binary file.
        :param file:
        :return:
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
                file_data.append(file.read(1))
                data_length -= 1
            next_granule = fat[starting_granule]
            file_data.extend(DiskFile.read_data(file, next_granule, data_length=data_length, fat=fat))
        else:
            for _ in range(data_length):
                file_data.append(file.read(1))
        return file_data

    def save_to_host_file(self, coco_file):
        pass

# E N D   O F   F I L E #######################################################
