"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import os

from abc import ABC, abstractmethod
from typing import NamedTuple

from cocoasm.values import Value

# C L A S S E S ###############################################################


class CoCoFile(NamedTuple):
    """
    A CoCoFile stores information relating to a file that should be stored on a
    VirtualFile's filesystem. It includes meta information such as the load point,
    execution point, the name, type, etc.
    """
    name: str = ""
    type: int = 0
    load_addr: Value = None
    exec_addr: Value = None
    data_type: int = 0
    gaps: int = 0
    ascii: int = 0
    data: list = []


class VirtualFile(ABC):
    """
    A VirtualFile represents a file that should be stored on the host system's hard drive.
    VirtualFiles may store one or many programs according to whatever format that supports
    it. For example, a CassetteFile has a certain format containing headers and data blocks,
    while a DiskFile contains a file allocation table, as well as headers and data blocks.
    """
    def __init__(self):
        self.host_file = None
        self.read_mode = False
        self.write_mode = False
        self.append_mode = False
        self.filename = None

    def open_host_file_for_write(self, filename, append=False):
        """
        Opens the file on the host drive for writing.

        :param filename: the name of the file to open
        :param append: whether to append to an existing file
        """
        if not append and os.path.exists(filename):
            raise ValueError("[{}] already exists, use --append to add to this file".format(filename))

        if append and not os.path.exists(filename):
            raise ValueError("[{}] file not found".format(filename))

        if not append:
            self.host_file = open(filename, "wb")
        else:
            self.host_file = open(filename, "ab")
            self.append_mode = True

        self.write_mode = True
        self.filename = filename

    def open_host_file_for_read(self, filename):
        """
        Opens the file on the host drive for reading.

        :param filename: the name of the file to open
        """
        if not os.path.exists(filename):
            raise ValueError("[{}] file not found".format(filename))

        self.host_file = open(filename, "rb")
        self.read_mode = True
        self.filename = filename

    def close_host_file(self):
        """
        Closes the file on the host drive.
        """
        if self.host_file:
            self.host_file.close()
            self.host_file = None
            self.filename = None
            self.read_mode = False
            self.write_mode = False
            self.append_mode = False

    @abstractmethod
    def save_to_host_file(self, coco_file):
        """
        Saves the specified file to the virtual image.

        :param coco_file: the CoCoFile to save to the virtual image
        """

    @abstractmethod
    def list_files(self):
        """
        Lists the files contained within the virtual file.

        :return: a list of CoCoFile objects in the virtual file
        """

    @abstractmethod
    def is_correct_type(self):
        """
        Determines whether the opened file for reading is of the correct type for the class.

        :return: True if the file content is correct, False otherwise
        """

# E N D   O F   F I L E #######################################################
