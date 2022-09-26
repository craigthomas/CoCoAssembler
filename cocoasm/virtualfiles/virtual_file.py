"""
Copyright (C) 2013-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import os

from enum import Enum

from cocoasm.virtualfiles.cassette import CassetteFile
from cocoasm.virtualfiles.disk import DiskFile
from cocoasm.virtualfiles.binary import BinaryFile
from cocoasm.virtualfiles.virtual_file_exceptions import VirtualFileValidationError

# C L A S S E S ###############################################################


class VirtualFileType(Enum):
    """
    The VirtualFileType enumeration stores what kind of virtual file exists.
    """
    UNKNOWN = 0
    CASSETTE = 1
    BINARY = 2
    DISK = 3


class VirtualFile(object):
    """
    A VirtualFile represents a file that should be stored on the host system's hard drive.
    VirtualFiles may store one or many programs according to whatever format that supports
    it. For example, a CassetteFile has a certain format containing headers and data blocks,
    while a DiskFile contains a file allocation table, as well as headers and data blocks.
    """
    def __init__(self, source_file=None, virtual_file_type=None):
        self.source_file = source_file
        self.virtual_file_type = virtual_file_type
        self.coco_file_list = []
        self.file_exists = False

    def get_coco_files(self):
        try:
            disk_file = DiskFile(buffer=self.source_file.get_buffer())
            return disk_file.list_files(), VirtualFileType.DISK
        except VirtualFileValidationError:
            pass

        try:
            cassette_file = CassetteFile(buffer=self.source_file.get_buffer())
            return cassette_file.list_files(), VirtualFileType.CASSETTE
        except VirtualFileValidationError as error:
            pass

        return [], VirtualFileType.BINARY

    def open_virtual_file(self):
        """
        Attempts to open the specified virtual file name. If found, will attempt to read
        the list of CoCoFiles from the list and save them to an internal array.
        """
        if os.path.exists(self.source_file.get_file_name()):
            self.file_exists = True
            self.source_file.read_file()
            self.coco_file_list, virtual_file_type = self.get_coco_files()
            if self.virtual_file_type and self.virtual_file_type != virtual_file_type:
                raise VirtualFileValidationError("[{}] is not of type {}".format(
                    self.source_file.get_file_name(), virtual_file_type
                ))
            self.virtual_file_type = virtual_file_type

    def save_virtual_file(self, append_mode=False):
        """
        Saves the CoCoFiles contained in the virtual file to disk.
        """
        if self.virtual_file_type == VirtualFileType.CASSETTE:
            cassette_file = CassetteFile()
            cassette_file.add_files(self.coco_file_list)
            if self.file_exists and not append_mode:
                raise FileExistsError(
                    "Target file [{}] already exists, use --append to overwrite".format(
                        self.source_file.get_file_name()
                    )
                )
            self.source_file.set_buffer(cassette_file.get_buffer())
            self.source_file.write_file()

        if self.virtual_file_type == VirtualFileType.BINARY:
            binary_file = BinaryFile()
            binary_file.add_files(self.coco_file_list)
            if self.file_exists and not append_mode:
                raise FileExistsError(
                    "Target file [{}] already exists, use --append to overwrite".format(
                        self.source_file.get_file_name()
                    )
                )
            self.source_file.set_buffer(binary_file.get_buffer())
            self.source_file.write_file()

        if self.virtual_file_type == VirtualFileType.DISK:
            disk_file = DiskFile()
            disk_file.add_files(self.coco_file_list)
            if self.file_exists and not append_mode:
                raise FileExistsError(
                    "Target file [{}] already exists, use --append to overwrite".format(
                        self.source_file.get_file_name()
                    )
                )
            self.source_file.set_buffer(disk_file.get_buffer())
            self.source_file.write_file()

    def add_coco_file(self, coco_file):
        """
        Adds the specified CoCoFile to the virtual image.

        :param coco_file: the CoCoFile to save to the virtual image
        """
        self.coco_file_list.append(coco_file)

    def delete_coco_file(self, coco_file_name):
        """

        :param coco_file_name:
        :return:
        """

    def list_files(self, filenames=None):
        """
        Lists the files contained within the virtual file.
        """
        if filenames:
            return [coco_file for coco_file in self.coco_file_list if coco_file.name in filenames]
        return self.coco_file_list


# E N D   O F   F I L E #######################################################
