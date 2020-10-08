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
    type: Value = None
    load_addr: Value = None
    exec_addr: Value = None
    data_type: Value = None
    gaps: Value = None
    ascii: int = 0
    data: list = []
    ignore_gaps: bool = False

    def __str__(self):
        result = "Filename:   {}\n".format(self.name)
        filetype = "BASIC"
        if self.type.hex() == "01":
            filetype = "Data"
        if self.type.hex() == "02":
            filetype = "Object"
        if self.type.hex() == "03":
            filetype = "Text"
        result += "File Type:  {}\n".format(filetype)

        data_type = "Binary"
        if self.data_type.hex() == "FF":
            data_type = "ASCII"
        result += "Data Type:  {}\n".format(data_type)

        if not self.ignore_gaps:
            gaps = "No Gaps"
            if self.gaps.hex() == "FF":
                gaps = "Gaps"
            result += "Gap Status: {}\n".format(gaps)

        result += "Load Addr:  ${}\n".format(self.load_addr.hex(size=4))
        result += "Exec Addr:  ${}\n".format(self.exec_addr.hex(size=4))
        result += "Data Len:   {} bytes".format(len(self.data))
        return result


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
    def list_files(self, filenames=None):
        """
        Lists the files contained within the virtual file.

        :param filenames: a list of filename strings to extract if they exist
        :return: a list of CoCoFile objects in the virtual file
        """

    @abstractmethod
    def is_correct_type(self):
        """
        Determines whether the opened file for reading is of the correct type for the class.

        :return: True if the file content is correct, False otherwise
        """

# E N D   O F   F I L E #######################################################
