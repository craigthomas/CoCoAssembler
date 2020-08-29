"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from cocoasm.virtualfiles.virtualfile import VirtualFile

# C L A S S E S ###############################################################


class BinaryFile(VirtualFile):
    """
    A binary file is a single file on the host filesystem that contains the
    assembled program code. Note that no meta-information about the binary
    file is stored within the file. Binary files store exactly one machine
    code program, therefore list_files returns an empty list.
    """
    def __init__(self):
        super().__init__()
        self.outfile = None

    def list_files(self):
        return []

    def is_correct_type(self):
        return False

    def save_to_host_file(self, coco_file):
        if self.append_mode:
            raise ValueError("[{}] already exists and cannot append to binary file".format(self.filename))
        self.host_file.write(bytearray(coco_file.data))

# E N D   O F   F I L E #######################################################
