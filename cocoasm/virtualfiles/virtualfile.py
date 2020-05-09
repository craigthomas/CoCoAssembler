"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import os

from abc import ABC, abstractmethod

from cocoasm.values import NoneValue

# C L A S S E S ###############################################################


class VirtualFile(ABC):
    def __init__(self):
        self.host_file = None
        self.load_addr = NoneValue()
        self.exec_addr = NoneValue()
        self.read_mode = False
        self.write_mode = False
        self.append_mode = False
        self.filename = None

    def open_for_write(self, filename, append=False):
        """
        Opens the file on the host drive for writing.

        :param filename: the name of the file to open
        :param append: whether to append to an existing file
        """
        if not append and os.path.exists(filename):
            raise ValueError("[{}] already exists, use --append to add to this file".format(filename))

        if not os.path.exists(filename):
            raise ValueError("[{}] file not found".format(filename))

        if not append:
            self.host_file = open(filename, "wb")
        else:
            self.host_file = open(filename, "ab")
            self.append_mode = True

        self.write_mode = True
        self.filename = filename

    def open_for_read(self, filename):
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
    def list_files(self):
        """
        Lists the files contained within the virtual file.

        :return: a list of CoCoFile objects in the virtual file
        """

    @abstractmethod
    def save_file(self, name, raw_bytes):
        """
        Saves the specified file to the virtual image.

        :param name: the name of the program
        :param raw_bytes: the raw bytes of the file
        """

    @abstractmethod
    def is_correct_type(self):
        """
        Determines whether the opened file for reading is of the correct type for the class.

        :return: True if the file content is correct, False otherwise
        """

# E N D   O F   F I L E #######################################################
