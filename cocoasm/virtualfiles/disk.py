"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from cocoasm.virtualfiles.virtualfile import VirtualFile, CoCoFile
from cocoasm.values import Value

# C L A S S E S ###############################################################


class DiskFile(VirtualFile):
    FAT_OFFSET = 78848

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
        self.host_file.seek(DiskFile.FAT_OFFSET)
        for file_number in range(0, 72):
            next_byte = Value.create_from_byte(self.host_file.peek(1)[:1])
            if next_byte.hex() == "00" or next_byte.hex() == "FF":
                self.host_file.seek(32, 1)
            else:
                coco_file = CoCoFile(
                    name="{}.{}".format(self.host_file.read(8).decode("utf-8"), self.host_file.read(3).decode("utf-8")),
                    type=Value.create_from_byte(self.host_file.read(1)),
                    data_type=Value.create_from_byte(self.host_file.read(1)),
                    load_addr=Value.create_from_byte(b"0"),
                    exec_addr=Value.create_from_byte(b"0"),
                    ignore_gaps=True
                )
                files.append(coco_file)
                self.host_file.seek(19, 1)

        return files

    def save_to_host_file(self, coco_file):
        pass

# E N D   O F   F I L E #######################################################
