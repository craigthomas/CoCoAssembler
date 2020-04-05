"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from abc import ABC, abstractmethod

# C L A S S E S ###############################################################


class CoCoFile(object):
    pass


class VirtualFile(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def list_files(self):
        """
        Lists the files contained within the virtual file.

        :return: a list of CoCoFile objects in the virtual file
        """

    @abstractmethod
    def open_host_file(self, filename):
        """
        Opens the file on the host drive for reading.

        :param filename: the name of the file to open
        """

    @abstractmethod
    def save_file(self, name, raw_bytes):
        """
        Saves the specified file to the virtual image.

        :param name: the name of the program
        :param raw_bytes: the raw bytes of the file
        """

    @abstractmethod
    def close_host_file(self):
        """
        Closes the file on the host drive.
        """


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

    def open_host_file(self, filename):
        self.outfile = open(filename, "wb")

    def save_file(self, name, raw_bytes):
        self.outfile.write(bytearray(raw_bytes))

    def close_host_file(self):
        if self.outfile:
            self.outfile.close()


class CassetteFile(VirtualFile):
    def __init__(self):
        super().__init__()

    def list_files(self):
        pass

    def open_host_file(self, filename):
        pass

    def save_file(self, name, raw_bytes):
        pass

    def close_host_file(self):
        pass


class DiskFile(VirtualFile):
    def __init__(self):
        super().__init__()

    def list_files(self):
        pass

    def open_host_file(self, filename):
        pass

    def save_file(self, name, raw_bytes):
        pass

    def close_host_file(self):
        pass

# E N D   O F   F I L E #######################################################
