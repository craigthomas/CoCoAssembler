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
        while True:
            coco_file = self.read_file()
            if not coco_file:
                return files

            if not filenames or coco_file.name in filenames:
                files.append(coco_file)

    def add_file(self, coco_file):
        """
        Adds a file to the buffer of the cassette data.

        :param coco_file: the CoCoFile object to add
        """
        self.write_leader()
        self.append_header(coco_file, CassetteFileType.OBJECT_FILE, CassetteDataType.BINARY)
        self.write_leader()
        self.append_data_blocks(coco_file.data)
        self.append_eof()

    def read_leader(self):
        """
        Reads a cassette leader. Should consist of 128 bytes of the value $55.
        Raises a ValueError if there is a problem. Returns True if the leader is okay.
        """
        if len(self.buffer) < 128:
            raise VirtualFileValidationError("Leader on tape is less than 128 bytes")

        for pointer in range(128):
            value = NumericValue(self.buffer[pointer])
            if value.hex() != "55":
                raise VirtualFileValidationError("[{}] invalid leader byte".format(value.hex()))

        self.buffer = self.buffer[128:]
        return True

    def write_leader(self):
        """
        Appends a cassette leader of character $55 to the buffer. The leader is
        always 128 bytes long consisting of value $55.
        """
        for _ in range(128):
            self.buffer.append(0x55)

    def validate_sequence(self, sequence):
        """
        Ensures that the next group of bytes read matches the sequence specified.
        Advances the buffer down the object

        :param sequence: an array-like list of bytes to read in the sequence
        :return: True if the bytes follow the sequence specified, false otherwise
        """
        if len(self.buffer) < len(sequence):
            raise VirtualFileValidationError("Not enough bytes in buffer to validate sequence")

        for pointer in range(len(sequence)):
            byte_read = NumericValue(self.buffer[0])
            if byte_read.int != sequence[pointer]:
                return False
            self.buffer = self.buffer[1:]
        return True

    def read_coco_file_name(self):
        """
        Reads the filename from the tape data.

        :return: the string representation of the filename
        """
        raw_file_name = []
        for pointer in range(8):
            raw_file_name.append(self.buffer[pointer])
        self.buffer = self.buffer[8:]
        coco_file_name = bytearray(raw_file_name).decode("utf-8")
        return coco_file_name

    def read_file(self):
        """
        Reads a cassette file, and returns a CoCoFile object with the
        information for the next file contained on the cassette file.

        :return: a CoCoFile with header information
        """
        # Make sure there is data to read
        if len(self.buffer) == 0:
            return None

        # Validate and skip over tape leader
        self.read_leader()

        # Validate header block
        if not self.validate_sequence([0x55, 0x3C, 0x00]):
            raise VirtualFileValidationError("Cassette header does not start with $55 $3C $00")

        # Length byte
        self.buffer = self.buffer[1:]

        # Extract file name
        coco_file_name = self.read_coco_file_name()

        # Get the file type
        file_type = NumericValue(self.buffer[0])
        data_type = NumericValue(self.buffer[1])
        gaps = NumericValue(self.buffer[2])

        load_addr_int = int(self.buffer[3])
        load_addr_int = load_addr_int << 8
        load_addr_int |= int(self.buffer[4])
        load_addr = NumericValue(load_addr_int)

        exec_addr_int = int(self.buffer[5])
        exec_addr_int = exec_addr_int << 8
        exec_addr_int |= int(self.buffer[6])
        exec_addr = NumericValue(exec_addr_int)

        # Advance two spaces to move past the header
        self.buffer = self.buffer[9:]

        # Skip over 128 byte leader
        self.read_leader()

        data = self.read_blocks()

        if not data:
            return None

        return CoCoFile(
            name=coco_file_name,
            type=file_type,
            data_type=data_type,
            gaps=gaps,
            load_addr=load_addr,
            exec_addr=exec_addr,
            data=data
        )

    def read_blocks(self):
        """
        Read all of the blocks that make up a file until an EOF block is found, or
        an error occurs.

        :return: an array-like object with all of the file data bytes read in order
        """
        data = []

        while True:
            if not self.validate_sequence([0x55, 0x3C]):
                raise VirtualFileValidationError("Data or EOF block validation failed")

            block_type = NumericValue(self.buffer[0])
            self.buffer = self.buffer[1:]

            if block_type.hex() == "FF":
                # Skip over length byte, checksum, and final $55
                self.buffer = self.buffer[3:]
                return data

            elif block_type.hex() == "01":
                data_length = NumericValue(self.buffer[0]).int
                self.buffer = self.buffer[1:]
                for ptr in range(data_length):
                    data.append(self.buffer[ptr])
                # Skip over block size, and checksum
                self.buffer = self.buffer[data_length:]
                self.buffer = self.buffer[2:]
            else:
                raise VirtualFileValidationError("Unknown block type found: {}".format(block_type.hex()))

    def append_header(self, coco_file, file_type, data_type):
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
        :param file_type: the CassetteFileType to save as
        :param data_type: the CassetteDataType to save as
        """
        # Standard header
        self.buffer.append(0x55)
        self.buffer.append(0x3C)
        self.buffer.append(0x00)
        self.buffer.append(0x0F)
        checksum = 0x0F

        # Filename and type
        checksum += self.append_name(coco_file.name)
        self.buffer.append(file_type)
        self.buffer.append(data_type)
        checksum += file_type
        checksum += data_type

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

    def append_data_blocks(self, raw_bytes):
        """
        Appends one or more data blocks to the buffer. Will continue to add
        data blocks to the buffer until the raw_bytes buffer is empty. The
        buffer is modified in-place.

        :param raw_bytes: the raw bytes of data to add to the data block
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


# E N D   O F   F I L E #######################################################
