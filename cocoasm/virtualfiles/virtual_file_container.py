"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import copy

from abc import abstractmethod
from cocoasm.virtualfiles.virtual_file_exceptions import VirtualFileValidationError
from cocoasm.values import NumericValue

# C L A S S E S ###############################################################


class VirtualFileContainer(object):
    """
    A VirtualFileContainer is a container for a specific set of CoCoFile
    objects. Containers typically represent the specific device that will
    be used to access the files within the virtual file (i.e. via Cassette,
    Disk, etc).
    """
    def __init__(self, buffer=None):
        self.original_buffer = []
        self.buffer = []
        if buffer:
            self.original_buffer = copy.deepcopy(buffer)
            self.buffer = buffer

    def add_files(self, file_list):
        """
        Adds a list of CoCoFile objects to the container.

        :param file_list: the list of CoCoFile objects to add to the container
        """
        for coco_file in file_list:
            self.add_file(coco_file)

    def get_buffer(self):
        """
        Returns the internal data buffer for the container.

        :return: the container buffer
        """
        return self.buffer

    @abstractmethod
    def add_file(self, coco_file):
        """
        Adds a CoCoFile object to the container.

        :param coco_file: the CoCoFile object to add
        """

    @abstractmethod
    def list_files(self, filenames=None):
        """
        Lists all the CoCoFile objects within the container.

        :param filenames: the list of CoCoFiles to list (if they exist)
        :return: a list of all the CoCoFile objects in the container
        """

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

# E N D   O F   F I L E #######################################################
