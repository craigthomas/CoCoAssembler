"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from enum import IntEnum

from cocoasm.virtualfiles.coco_file import CoCoFile
from cocoasm.virtualfiles.virtual_file_container import VirtualFileContainer
from cocoasm.virtualfiles.virtual_file_exceptions import VirtualFileValidationError
from cocoasm.values import NumericValue

# C L A S S E S ###############################################################


class CassetteFileType(IntEnum):
    BASIC_FILE = 0x00
    DATA_FILE = 0x01
    OBJECT_FILE = 0x02


class CassetteDataType(IntEnum):
    BINARY = 0x00
    ASCII = 0xFF


class CassetteFile(VirtualFileContainer):
    """
    A CassetteFile contains a series of blocks that are separated by leaders
    and gaps. There are three different types of blocks:

      header block - contains the filename, loading address, and execution address
      data block - contains the raw data for the file, may be multiple blocks
      EOF block - contains an EOF signature

    CassetteFile may contain more than one file on it. Each block is written into
    an internal buffer that is simply a list of bytes.
    """
    def __init__(self, buffer=None):
        super().__init__(buffer=buffer)

    def list_files(self, filenames=None):
        """
        Extracts a list of CoCoFile objects from the cassette file.

        :param filenames: the list of filenames to include if specified
        :return: a list of CoCoFile objects
        """
        files = []
        pointer = 0

        while True:
            coco_file, pointer = self.read_file(pointer)
            if not coco_file:
                return files

            if not filenames or coco_file.name in filenames:
                files.append(coco_file)

    def add_file(self, coco_file):
        """
        Adds a file to the buffer of the cassette data.

        :param coco_file: the CoCoFile object to add
        """
        self.append_blank()
        self.append_leader()
        self.append_header(coco_file)
        self.append_blank()
        self.append_leader()
        self.append_data_blocks(coco_file.data)
        self.append_eof()

    def skip_to_sequence(self, sequence, start=0):
        """
        Returns a pointer to the internal buffer where the start of the specified sequence begins.
        Will return -1 if the sequence does not exist.

        :param sequence: the sequence to search for
        :param start: the place in the buffer to start the search
        :return: a pointer to the internal buffer where the sequence begins
        """
        for pointer in range(start, start + len(self.buffer) - len(sequence) + 1):
            if self.buffer[pointer:pointer + len(sequence)] == sequence:
                return pointer

        return -1

    def read_coco_file_name(self, pointer):
        """
        Reads the filename from the tape data.

        :return: the string representation of the filename
        """
        raw_file_name = []
        for name_offset in range(8):
            raw_file_name.append(self.buffer[pointer + name_offset])
        coco_file_name = bytearray(raw_file_name).decode("utf-8")
        pointer += 8
        return coco_file_name, pointer

    def read_file(self, pointer):
        """
        Reads a cassette file, and returns a CoCoFile object with the
        information for the next file contained on the cassette file.

        :param pointer: an integer index into the buffer where to start reading from
        :return: a CoCoFile with header information, and a pointer to where the file ended
        """
        # Find the next header block
        pointer = self.skip_to_sequence([0x55, 0x3C, 0x00], start=pointer)
        if pointer == -1:
            return None, pointer

        # Skip length byte (always $0F)
        pointer += 4

        # Extract file name
        coco_file_name, pointer = self.read_coco_file_name(pointer)

        # Get the file type
        file_type = NumericValue(self.buffer[pointer])
        pointer += 1
        extension = "BAS"
        if file_type.int == 0x02:
            extension = "BIN"

        # Get the data type
        data_type = NumericValue(self.buffer[pointer])
        pointer += 1

        # Get the gap status
        gaps = NumericValue(self.buffer[pointer])
        pointer += 1

        # Get load and exec addresses
        load_addr = self.read_word(pointer)
        pointer += 2
        exec_addr = self.read_word(pointer)
        pointer += 2

        # Advance two spaces to move past the header
        pointer += 2

        # Read any data blocks
        data, pointer = self.read_blocks(pointer)

        if not data:
            return None, pointer

        return CoCoFile(
            name=coco_file_name,
            extension=extension,
            type=file_type,
            data_type=data_type,
            gaps=gaps,
            load_addr=load_addr,
            exec_addr=exec_addr,
            data=data
        ), pointer

    def read_blocks(self, pointer):
        """
        Read all the blocks that make up a file until an EOF block is found, or
        an error occurs.

        :return: an array-like object with all the file data bytes read in order
        """
        data = []

        while True:
            pointer = self.skip_to_sequence([0x55, 0x3C], start=pointer)
            if pointer == -1:
                raise VirtualFileValidationError("Data or EOF block not found")
            pointer += 2

            # Read the block type
            block_type = NumericValue(self.buffer[pointer])
            pointer += 1

            # Check for EOF block type, and if found skip over length, checksum and $55 byte and return
            if block_type.hex() == "FF":
                pointer += 3
                return data, pointer

            # Check for data block type and consume it
            elif block_type.hex() == "01":
                data_length = NumericValue(self.buffer[pointer]).int
                pointer += 1
                for block_data_pointer in range(data_length):
                    data.append(self.buffer[pointer + block_data_pointer])
                pointer += data_length

                # Skip over checksum
                pointer += 2
            else:
                raise VirtualFileValidationError("Unknown block type found: {}".format(block_type.hex()))

    def append_header(self, coco_file):
        """
        The header of a cassette file is 21 bytes long:
          byte 1 = $55 (fixed value)
          byte 2 = $3C (fixed value)
          byte 3 = $00 (block type - $00 = header)
          byte 4 = $0F (length of block - fixed at $0F)
          byte 5 - 12 = $XX XX XX XX XX XX XX XX (filename - 8 bytes long)
          byte 13 = $XX (filetype - $00 = BASIC, $01 = data file, $02 = object code)
          byte 14 = $XX (datatype - $00 = binary, $FF = ascii)
          byte 15 = $XX (gaps, $00 = none, $FF = gaps)
          byte 16 - 17 = $XX XX (loading address)
          byte 18 - 19 = $XX XX (exec address)
          byte 20 = $XX (checksum - sum of bytes 3 to 19, 8-bit, ignore carries)
          byte 21 = $55 (fixed value)

        :param coco_file: the CoCoFile to append to cassette
        """
        # Standard header
        self.buffer.append(0x55)
        self.buffer.append(0x3C)
        self.buffer.append(0x00)
        self.buffer.append(0x0F)
        checksum = 0x0F

        # Filename and type
        checksum += self.append_name(coco_file.name)
        self.buffer.append(coco_file.type.int)
        self.buffer.append(coco_file.data_type.int)
        checksum += coco_file.type.int
        checksum += coco_file.data_type.int

        # No gaps in blocks
        self.buffer.append(0x00)

        # The loading and execution addresses
        self.buffer.append(coco_file.load_addr.high_byte())
        self.buffer.append(coco_file.load_addr.low_byte())
        self.buffer.append(coco_file.exec_addr.high_byte())
        self.buffer.append(coco_file.exec_addr.low_byte())
        checksum += coco_file.load_addr.high_byte()
        checksum += coco_file.load_addr.low_byte()
        checksum += coco_file.exec_addr.high_byte()
        checksum += coco_file.exec_addr.low_byte()

        # Checksum byte
        self.buffer.append(checksum & 0xFF)

        # Final standard byte
        self.buffer.append(0x55)

    def append_name(self, name):
        """
        Appends the name of the file to the cassette header block. The name may only
        be 8 characters long. It is left padded by $00 values. The buffer is modified
        in-place.

        :param name: the name of the file as saved to the cassette
        """
        checksum = 0
        for index in range(8):
            if len(name) > index:
                self.buffer.append(ord(name[index]))
                checksum += ord(name[index])
            else:
                self.buffer.append(0x20)
                checksum += 0x20
        return checksum

    def append_data_blocks(self, raw_bytes, gaps=False):
        """
        Appends one or more data blocks to the buffer. Will continue to add
        data blocks to the buffer until the raw_bytes buffer is empty. The
        buffer is modified in-place.

        :param raw_bytes: the raw bytes of data to add to the data block
        :param gaps: if True, will append blanks and leaders between data blocks
        """
        if len(raw_bytes) == 0:
            return

        # Header of data block
        self.buffer.append(0x55)
        self.buffer.append(0x3C)
        self.buffer.append(0x01)

        # Length of data block
        if len(raw_bytes) < 255:
            self.buffer.append(len(raw_bytes))
        else:
            self.buffer.append(0xFF)

        # Data to write
        checksum = 0x01
        if len(raw_bytes) < 255:
            checksum += len(raw_bytes)
            for index in range(len(raw_bytes)):
                self.buffer.append(raw_bytes[index])
                checksum += raw_bytes[index]
            self.buffer.append(checksum & 0xFF)
            self.buffer.append(0x55)
        else:
            checksum += 0xFF
            for index in range(255):
                self.buffer.append(raw_bytes[index])
                checksum += raw_bytes[index]
            self.buffer.append(checksum & 0xFF)
            self.buffer.append(0x55)
            if gaps:
                self.append_blank()
                self.append_leader()
            self.append_data_blocks(raw_bytes[255:])

    def append_eof(self):
        """
        Appends an EOF block to a buffer. The block is 6 bytes long:

          byte 1 = $55 (fixed value)
          byte 2 = $3C (fixed value)
          byte 3 = $FF (block type, $FF = EOF block)
          byte 4 = $00 (length of block)
          byte 5 = $XX (checksum - addition of bytes 3 and 4)
          byte 6 = $55 (fixed value)

        The buffer is modified in-place.
        """
        self.buffer.append(0x55)
        self.buffer.append(0x3C)
        self.buffer.append(0xFF)
        self.buffer.append(0x00)
        self.buffer.append(0xFF)
        self.buffer.append(0x55)

    def append_leader(self):
        """
        Appends a cassette leader of character $55 to the buffer. The leader is
        always 128 bytes long consisting of value $55.
        """
        for _ in range(128):
            self.buffer.append(0x55)

    def append_blank(self):
        """
        Appends a blank space of character $00 to the buffer. The blank space is
        always 128 bytes long consisting of value $00.
        """
        for _ in range(128):
            self.buffer.append(0x00)

# E N D   O F   F I L E #######################################################
