"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from enum import IntEnum


from cocoasm.virtualfiles.virtualfile import VirtualFile, CoCoFile
from cocoasm.values import Value

# C L A S S E S ###############################################################


class CassetteFileType(IntEnum):
    BASIC_FILE = 0x00
    DATA_FILE = 0x01
    OBJECT_FILE = 0x02


class CassetteDataType(IntEnum):
    BINARY = 0x00
    ASCII = 0xFF


class CassetteFile(VirtualFile):
    """
    A CassetteFile contains a series of blocks that are separated by leaders
    and gaps. There are three different types of blocks:

      header block - contains the filename, loading address, and execution address
      data block - contains the raw data for the file, may be multiple blocks
      EOF block - contains an EOF signature

    CassetteFile may contain more than one file on it.
    """
    def __init__(self):
        super().__init__()

    def is_correct_type(self):
        if not self.host_file:
            raise ValueError("No file currently open")

        if not self.read_mode:
            raise ValueError("[{}] not open for reading".format(self.filename))

        self.host_file.seek(0)

        # First 128 bytes must be a leader of $55
        for _ in range(128):
            character = ord(self.host_file.read(1))
            if character != 0x55:
                return False

        self.host_file.seek(0)
        return True

    def get_file(self):
        if not self.seek_header(self.host_file):
            return -1
        else:
            self.read_header(self.host_file)
            return 1

    def list_files(self, files=None):
        if files is None:
            files = []

        cassette_file = self.get_file()
        if cassette_file == -1:
            return files

        files.append(cassette_file)
        return self.list_files(files=files)


    def save_to_host_file(self, coco_file):
        data = []
        self.write_leader(data)
        self.append_header(data, coco_file, CassetteFileType.OBJECT_FILE, CassetteDataType.BINARY)
        self.write_leader(data)
        self.append_data_blocks(data, coco_file.data)
        self.append_eof(data)
        self.host_file.write(bytearray(data))

    @staticmethod
    def read_leader(file):
        """
        Reads a cassette leader. Should consist of 128 bytes of the value $55.
        Raises a ValueError if there is a problem.

        :param file: the file object to read from
        """
        for _ in range(128):
            value = Value.create_from_byte(file.read(1))
            if value.hex() != "55":
                raise ValueError("[{}] invalid leader byte".format(value.hex()))

    @staticmethod
    def write_leader(buffer):
        """
        Appends a cassette leader of character $55 to the buffer. The leader is
        always 128 bytes long consisting of value $55.

        :param buffer: the buffer to add the leader to
        """
        for _ in range(128):
            buffer.append(0x55)

    @staticmethod
    def seek_header(file):
        """
        Reads the file until a header is found. If a header is found, then the file
        stream is rewound to the start of the header.

        :param file: the file object to read from
        """
        while True:
            try:
                last_values = [Value.create_from_byte(file.read(1)).hex(),
                               Value.create_from_byte(file.read(1)).hex(),
                               Value.create_from_byte(file.read(1)).hex()]
            except ValueError:
                return False

            if last_values == ["55", "3C", "00"]:
                file.seek(-3, 1)
                return True

            file.seek(-2, 1)

    @staticmethod
    def read_header(file):
        """
        Reads the header for the file, and returns a CoCoFile object with the
        information for the file (without data).

        :param file: the file object to read from
        :return: a CoCoFile with header information
        """
        value = Value.create_from_byte(file.read(1))
        if value.hex() != "55":
            raise ValueError("[{}] invalid first header byte".format(value.hex()))

        value = Value.create_from_byte(file.read(1))
        if value.hex() != "3C":
            raise ValueError("[{}] invalid second header byte".format(value.hex()))

        value = Value.create_from_byte(file.read(1))
        if value.hex() != "00":
            raise ValueError("[{}] invalid third header byte".format(value.hex()))

        value = Value.create_from_byte(file.read(1))
        if value.hex() != "0F":
            raise ValueError("[{}] invalid fourth header byte".format(value.hex()))

        # Read 8 bytes worth of data as the filename
        filename = file.read(8)
        print("--")
        print("Filename:   {}".format(filename.decode("utf-8")))

        value = Value.create_from_byte(file.read(1))
        filetype = "BASIC"
        if value.hex() == "01":
            filetype = "Data"
        if value.hex() == "02":
            filetype = "Object"
        print("File Type:  {}".format(filetype))

        value = Value.create_from_byte(file.read(1))
        data_type = "Binary"
        if value.hex() == "FF":
            data_type = "ASCII"
        print("Data Type:  {}".format(data_type))

        value = Value.create_from_byte(file.read(1))
        gaps = "No Gaps"
        if value.hex() == "FF":
            gaps = "Gaps"
        print("Gap Status: {}".format(gaps))

        value = Value.create_from_byte(file.read(2))
        print("Load Addr:  ${}".format(value.hex(size=4)))

        value = Value.create_from_byte(file.read(2))
        print("Exec Addr:  ${}".format(value.hex(size=4)))

    @staticmethod
    def append_header(buffer, coco_file, file_type, data_type):
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

        :param buffer: the buffer to append the header to
        :param coco_file: the CoCoFile to append to cassette
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
        checksum += CassetteFile.append_name(coco_file.name, buffer)
        buffer.append(file_type)
        buffer.append(data_type)
        checksum += file_type
        checksum += data_type

        # No gaps in blocks
        buffer.append(0x00)

        # The loading and execution addresses
        buffer.append(coco_file.load_addr.high_byte())
        buffer.append(coco_file.load_addr.low_byte())
        buffer.append(coco_file.exec_addr.high_byte())
        buffer.append(coco_file.exec_addr.low_byte())
        checksum += coco_file.load_addr.high_byte()
        checksum += coco_file.load_addr.low_byte()
        checksum += coco_file.exec_addr.high_byte()
        checksum += coco_file.exec_addr.low_byte()

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

# E N D   O F   F I L E #######################################################
