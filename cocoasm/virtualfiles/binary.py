"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from cocoasm.virtualfiles.virtual_file_container import VirtualFileContainer

# C L A S S E S ###############################################################


class BinaryFile(VirtualFileContainer):
    """
    A binary file is a single file on the host filesystem that contains the
    assembled program code. Note that no meta-information about the binary
    file is stored within the file. Binary files store exactly one machine
    code program, therefore list_files returns an empty list.
    """
    def __init__(self, buffer=None):
        super().__init__(buffer=buffer)

    def add_file(self, coco_file):
        self.buffer.extend(coco_file.data)

    def list_files(self, filenames=None):
        return []

# E N D   O F   F I L E #######################################################
