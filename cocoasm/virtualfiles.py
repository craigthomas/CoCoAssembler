"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import os

from abc import ABC, abstractmethod
from enum import IntEnum

from cocoasm.values import NoneValue

# C L A S S E S ###############################################################


class CassetteFileType(IntEnum):
    BASIC_FILE = 0x00
    DATA_FILE = 0x01
    OBJECT_FILE = 0x02


class CassetteDataType(IntEnum):
    BINARY = 0x00
    ASCII = 0xFF


class CoCoFile(object):
    pass


class VirtualFile(ABC):
    def __init__(self):
        self.host_file = None
        self.load_addr = NoneValue()
        self.exec_addr = NoneValue()
        self.append_mode = False
        self.filename = None

    def open_host_file(self, filename, append=False):
        """
        Opens the file on the host drive for reading.

        :param filename: the name of the file to open
        :param append: whether to append to an existing file
        """
        if not append and os.path.exists(filename):
            raise ValueError("[{}] already exists, use --append to add to this file".format(filename))

        if not append:
            self.host_file = open(filename, "wb")
        else:
            self.host_file = open(filename, "ab")
            self.append_mode = True

        self.filename = filename

    def close_host_file(self):
        """
        Closes the file on the host drive.
        """
        if self.host_file:
            self.host_file.close()
            self.host_file = None

    def is_host_file_open(self):
        """
        Returns True if a host file is open, False otherwise.

        :return: True if the host file is open, False otherwise
        """
        return self.host_file is not None

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

    def save_file(self, name, raw_bytes):
        if self.append_mode:
            raise ValueError("[{}] cannot append to binary file".format(self.filename))
        self.host_file.write(bytearray(raw_bytes))


class CassetteFile(VirtualFile):
    """
    A CassetteFile contains a series of blocks that are separated by leaders
    and gaps. There are three different types of blocks:

      header block - contains the filename, loading address, and execution address
      data block - contains the raw data for the file, may be multiple blocks
      EOF block - contains an EOF signature

    CassetteFile may contain more than one file on it.
    """
    def __init__(self, load_addr, exec_addr):
        super().__init__()
        self.load_addr = load_addr
        self.exec_addr = exec_addr

    def list_files(self):
        pass

    def save_file(self, name, raw_bytes):
        buffer = []
        self.append_leader(buffer)
        self.append_header(buffer, name, CassetteFileType.OBJECT_FILE, CassetteDataType.BINARY)
        self.append_leader(buffer)
        self.append_data_blocks(buffer, raw_bytes)
        self.append_eof(buffer)
        self.host_file.write(bytearray(buffer))

    @staticmethod
    def append_leader(buffer):
        """
        Appends a cassette leader of character $55 to the buffer. The leader is
        always 128 bytes long consisting of value $55.

        :param buffer: the buffer to add the leader to
        """
        for _ in range(128):
            buffer.append(0x55)

    def append_header(self, buffer, name, file_type, data_type):
        """
        The header of a cassette file is 21 bytes long:
          byte 1 = $55 (fixed value)
          byte 2 = $3C (fixed value)
          byte 3 = $00 (block type - $00 = header)
          byte 4 - 12 = $XX XX XX XX XX XX XX XX (filename - 8 bytes long)
          byte 13 = $XX (filetype - $00 = BASIC, $01 = data file, $02 = object code)
          byte 14 = $XX (datatype - $00 = binary, $FF = ascii)
          byte 15 = $XX (gaps, $00 = none, $FF = gaps)
          byte 16 - 17 = $XX XX (loading address)
          byte 18 - 19 = $XX XX (exec address)
          byte 20 = $XX (checksum - sum of bytes 3 to 19, 8-bit, ignore carries)
          byte 21 = $55 (fixed value)

        :param buffer: the buffer to append the header to
        :param name: the name of the file as it should appear on the cassette
        :param file_type: the CassetteFileType to save as
        :param data_type: the CassetteDataType to save as
        """
        # Standard header
        buffer.append(0x55)
        buffer.append(0x3C)
        buffer.append(0x00)
        buffer.append(0x0F)
        checksum = 0x0F

        # Filename and type
        checksum += CassetteFile.append_name(name, buffer)
        buffer.append(file_type)
        buffer.append(data_type)
        checksum += file_type
        checksum += data_type

        # No gaps in blocks
        buffer.append(0x00)

        # The loading and execution addresses
        buffer.append(self.load_addr.high_byte())
        buffer.append(self.load_addr.low_byte())
        buffer.append(self.exec_addr.high_byte())
        buffer.append(self.exec_addr.low_byte())
        checksum += self.load_addr.high_byte()
        checksum += self.load_addr.low_byte()
        checksum += self.exec_addr.high_byte()
        checksum += self.exec_addr.low_byte()

        # Checksum byte
        buffer.append(checksum & 0xFF)

        # Final standard byte
        buffer.append(0x55)

    @staticmethod
    def append_name(name, buffer):
        """
        Appends the name of the file to the cassette header block. The name may only
        be 8 characters long. It is left padded by $00 values. The buffer is modified
        in-place.

        :param name: the name of the file as saved to the cassette
        :param buffer: the buffer to write to
        """
        checksum = 0
        for index in range(8):
            if len(name) > index:
                buffer.append(ord(name[index]))
                checksum += ord(name[index])
            else:
                buffer.append(0x20)
                checksum += 0x20
        return checksum

    @staticmethod
    def append_data_blocks(buffer, raw_bytes):
        """
        Appends one or more data blocks to the buffer. Will continue to add
        data blocks to the buffer until the raw_bytes buffer is empty. The
        buffer is modified in-place.

        :param buffer: the buffer to append to
        :param raw_bytes: the raw bytes of data to add to the data block
        """
        if len(raw_bytes) == 0:
            return

        # Header of data block
        buffer.append(0x55)
        buffer.append(0x3C)
        buffer.append(0x01)

        # Length of data block
        if len(raw_bytes) < 255:
            buffer.append(len(raw_bytes))
        else:
            buffer.append(0xFF)

        # Data to write
        checksum = 0x01
        if len(raw_bytes) < 255:
            checksum += len(raw_bytes)
            for index in range(len(raw_bytes)):
                buffer.append(raw_bytes[index])
                checksum += raw_bytes[index]
            buffer.append(checksum & 0xFF)
            buffer.append(0x55)
        else:
            checksum += 0xFF
            for index in range(255):
                buffer.append(raw_bytes[index])
                checksum += raw_bytes[index]
            buffer.append(checksum & 0xFF)
            buffer.append(0x55)
            CassetteFile.append_data_blocks(buffer, raw_bytes[255:])

    @staticmethod
    def append_eof(buffer):
        """
        Appends an EOF block to a buffer. The block is 6 bytes long:

          byte 1 = $55 (fixed value)
          byte 2 = $3C (fixed value)
          byte 3 = $FF (block type, $FF = EOF block)
          byte 4 = $00 (length of block)
          byte 5 = $XX (checksum - addition of bytes 3 and 4)
          byte 6 = $55 (fixed value)

        The buffer is modified in-place.

        :param buffer: the buffer to write the EOF block to
        """
        buffer.append(0x55)
        buffer.append(0x3C)
        buffer.append(0xFF)
        buffer.append(0x00)
        buffer.append(0xFF)
        buffer.append(0x55)


class DiskFile(VirtualFile):
    def __init__(self):
        super().__init__()

    def list_files(self):
        pass

    def save_file(self, name, raw_bytes):
        pass

# E N D   O F   F I L E #######################################################
