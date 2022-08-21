"""
Copyright (C) 2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from enum import Enum


# C L A S S E S ###############################################################

class SourceFileType(Enum):
    ASSEMBLY = 0
    BINARY = 1


class SourceFile(object):
    def __init__(self, file_name=None, file_type=SourceFileType.ASSEMBLY):
        self.file_type = file_type
        self.file_name = file_name
        self.buffer = []

    def read_file(self):
        if self.file_type == SourceFileType.ASSEMBLY:
            self.buffer = self.read_assembly_contents(self.file_name)

        if self.file_type == SourceFileType.BINARY:
            self.buffer = self.read_binary_contents(self.file_name)

    def write_file(self):
        if self.file_type == SourceFileType.BINARY:
            self.write_binary_contents(self.file_name, self.buffer)

    def get_buffer(self):
        return self.buffer

    def set_buffer(self, buffer):
        self.buffer = buffer

    def get_file_name(self):
        return self.file_name

    @staticmethod
    def read_assembly_contents(filename):
        with open(filename, "r") as source_file:
            return source_file.readlines()

    @staticmethod
    def read_binary_contents(filename):
        contents = []
        with open(filename, "rb") as source_file:
            byte = source_file.read(1)
            while byte:
                contents.append(int.from_bytes(byte, "big"))
                byte = source_file.read(1)
        return contents

    @staticmethod
    def write_binary_contents(filename, buffer):
        with open(filename, "wb") as outfile:
            outfile.write(bytearray(buffer))

# E N D   O F   F I L E #######################################################
