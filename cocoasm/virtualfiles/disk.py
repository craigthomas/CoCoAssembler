"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from cocoasm.virtualfiles.virtualfile import VirtualFile

# C L A S S E S ###############################################################


class DiskFile(VirtualFile):
    def __init__(self):
        super().__init__()

    def list_files(self):
        pass

    def save_to_host_file(self, name, raw_bytes):
        pass

# E N D   O F   F I L E #######################################################
