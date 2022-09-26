"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from typing import NamedTuple

from abc import ABC, abstractmethod
from enum import Enum

from cocoasm.virtualfiles.coco_file import CoCoFile
from cocoasm.virtualfiles.virtual_file_container import VirtualFileContainer
from cocoasm.values import NumericValue, NoneValue
from cocoasm.virtualfiles.virtual_file_exceptions import VirtualFileValidationError

# C L A S S E S ###############################################################


class DiskConstants(object):
    FAT_OFFSET = 78592
    DIR_OFFSET = 78848
    HALF_TRACK_LEN = 2304
    SECTORS_PER_TRACK = 18
    BYTES_PER_SECTOR = 256
    TOTAL_GRANULES = 68
    PREAMBLE_LEN = 5
    POSTAMBLE_LEN = 5
    IMAGE_SIZE = 161280
    GRANULE_FILL_ORDER = [
        32, 33, 34, 35, 30, 31, 36, 37, 28, 29, 38, 39, 26, 25, 40, 41, 24, 25, 42, 43,
        22, 23, 40, 41, 20, 21, 42, 43, 18, 19, 44, 45, 16, 17, 46, 47, 14, 15, 48, 49,
        12, 13, 50, 51, 10, 11, 52, 53, 8, 9, 54, 55, 6, 7, 56, 57, 4, 5, 58, 59, 2, 3,
        60, 61, 0, 1, 62, 63, 64, 65, 66, 67
    ]


class DirectoryEntry(NamedTuple):
    file_name: str = "        "
    extension: str = "   "
    file_type: int = 2
    ascii_flag: int = 0x00
    first_granule: int = 0x00


class PreambleType(Enum):
    ML = 0
    OTHER = 1


class Preamble(ABC):
    def __init__(self):
        self.data_length = NoneValue()
        self.load_addr = NoneValue()
        self.length = 0

    def get_data_length(self):
        """
        Returns the length of the actual data.

        :return: the length of the data
        """
        return self.data_length.int

    @abstractmethod
    def read(self, buffer, pointer):
        """
        Given a buffer and a pointer, reads the preamble, and returns a pointer
        past the point of the preamble.
        """

    @abstractmethod
    def write(self, buffer, pointer):
        """
        Given a buffer and a pointer, writes the preamble, and returns a pointer
        past the point of the preamble.

        :param buffer: the buffer to write into
        :param pointer: the pointer into the buffer to start the write
        :return: a pointer to the byte past the preamble
        """

    def is_ml(self):
        """
        Returns whether this is an ML preamble or a basic preamble.

        :return: True if it is an ML preamble
        """
        return False


class MLPreamble(Preamble):
    """
    The machine language preamble data for the file. The preamble is a collection of 5
    bytes at the start of a binary file:

        byte 0 - always $00
        byte 1,2 - the data length of the file
        byte 3,4 - the load address for the file

    """
    def __init__(self):
        super().__init__()
        self.length = 5

    def read(self, buffer, pointer):
        if len(buffer[pointer:]) < self.length:
            raise VirtualFileValidationError("Not enough bytes to read preamble")

        if buffer[pointer] != 0x00:
            raise VirtualFileValidationError("Invalid ML preamble flag")

        self.data_length = NumericValue((buffer[pointer + 1] << 8) + buffer[pointer + 2])
        self.load_addr = NumericValue((buffer[pointer + 3] << 8) + buffer[pointer + 4])

        return pointer + self.length

    def write(self, buffer, pointer):
        if len(buffer[pointer:]) < self.length:
            raise VirtualFileValidationError("Not enough bytes to write preamble")

        buffer[pointer] = 0x00
        buffer[pointer + 1] = self.data_length.high_byte()
        buffer[pointer + 2] = self.data_length.low_byte()
        buffer[pointer + 3] = self.load_addr.high_byte()
        buffer[pointer + 4] = self.load_addr.low_byte()
        return pointer + self.length

    def is_ml(self):
        return True


class ASCIIPreamble(Preamble):
    """
    ASCII encoded files in TRS-DOS do not have a preamble or a postamble.
    """
    def __init__(self):
        super().__init__()
        self.length = 0

    def read(self, buffer, pointer):
        return pointer

    def write(self, buffer, pointer):
        return pointer


class BasicPreamble(Preamble):
    """
    All BASIC files under TRS-DOS are considered to have just a preamble that
    contains the data length. The preamble is a collection of 3 bytes at the
    start of a file:

        byte 0 - always $FF
        byte 1,2 - the data length of the file

    """
    def __init__(self):
        super().__init__()
        self.length = 3

    def read(self, buffer, pointer):
        if len(buffer[pointer:]) < self.length:
            raise VirtualFileValidationError("Not enough bytes to read preamble")

        if buffer[pointer] != 0xFF:
            raise VirtualFileValidationError("Invalid basic preamble flag")

        self.data_length = NumericValue((buffer[pointer + 1] << 8) + buffer[pointer + 2])

        return pointer + self.length

    def write(self, buffer, pointer):
        if len(buffer[pointer:]) < self.length:
            raise VirtualFileValidationError("Not enough bytes to write preamble")

        buffer[pointer] = 0xFF
        buffer[pointer + 1] = self.data_length.high_byte()
        buffer[pointer + 2] = self.data_length.low_byte()
        return pointer + self.length


class Postamble(object):
    """
    The Postamble class is used to store information relating t a binary file
    on a disk image. The Postamble is stored at the end of a binary file and
    contains the exec address for the binary.
    """
    def __init__(self):
        self.exec_addr = NoneValue()
        self.length = 5

    def read(self, buffer, pointer):
        if len(buffer[pointer:]) < self.length:
            raise VirtualFileValidationError("Not enough bytes to read postamble")

        if buffer[pointer] != 0xFF:
            raise VirtualFileValidationError("Invalid postamble byte 0 not 0xFF, got {}".format(hex(buffer[pointer])))

        if buffer[pointer + 1] != 0x00:
            raise VirtualFileValidationError("Invalid postamble byte 1 not 0x00, got {}".format(hex(buffer[pointer+1])))

        if buffer[pointer + 2] != 0x00:
            raise VirtualFileValidationError("Invalid postamble byte 2 not 0x00, got {}".format(hex(buffer[pointer+2])))

        self.exec_addr = NumericValue((buffer[pointer + 3] << 8) + buffer[pointer + 4])
        return pointer + self.length

    def write(self, buffer, pointer):
        if len(buffer[pointer:]) < self.length:
            raise VirtualFileValidationError("Not enough bytes to write postamble")

        buffer[pointer] = 0xFF
        buffer[pointer + 1] = 0
        buffer[pointer + 2] = 0
        buffer[pointer + 3] = self.exec_addr.high_byte()
        buffer[pointer + 4] = self.exec_addr.low_byte()
        return pointer + self.length


class DiskFile(VirtualFileContainer):
    def __init__(self, buffer=None, granule_fill_order=None):
        super().__init__(buffer=buffer)
        if buffer is None:
            self.buffer = [0xFF] * DiskConstants.IMAGE_SIZE
        self.granule_fill_order = DiskConstants.GRANULE_FILL_ORDER
        if granule_fill_order:
            self.granule_fill_order = granule_fill_order

    def read_sequence(self, pointer, length, decode=False):
        """
        Reads a sequence of bytes of the specified length and returns a list like
        object that contains the sequence read.

        :param pointer: the byte number in to the buffer to start the read
        :param length: the number of bytes to read
        :param decode: whether to UTF-8 decode the resultant data
        :return: a list like object of the bytes read
        """
        sequence = []
        if length > len(self.buffer) or (len(self.buffer[pointer:]) < length):
            raise VirtualFileValidationError("Unable to read sequence of length {}".format(length))

        for file_name_pointer in range(pointer, pointer + length):
            sequence.append(self.buffer[file_name_pointer])
        return bytearray(sequence).decode("utf-8") if decode else sequence

    def validate_sequence(self, pointer, sequence):
        """
        Ensures that the next group of bytes read matches the sequence specified.
        Advances the buffer down the object

        :param pointer: a pointer into the data of the file
        :param sequence: an array-like list of bytes to read in the sequence
        :return: True if the bytes follow the sequence specified, false otherwise
        """
        if len(self.buffer[pointer:]) < len(sequence):
            raise VirtualFileValidationError("Not enough bytes in buffer to validate sequence")

        for sequence_pointer in range(len(sequence)):
            byte_read = NumericValue(self.buffer[pointer + sequence_pointer])
            if byte_read.int != sequence[sequence_pointer]:
                return False
        return True

    def list_files(self, filenames=None):
        if len(self.buffer) < DiskConstants.IMAGE_SIZE:
            raise VirtualFileValidationError("Disk image size is not {:,d} bytes long".format(DiskConstants.IMAGE_SIZE))
        files = []

        # Read the File Allocation Table
        fat = self.buffer[DiskConstants.FAT_OFFSET:DiskConstants.FAT_OFFSET + 256]

        # Move through elements in the Directory Table and read them into CoCoFile objects
        pointer = DiskConstants.DIR_OFFSET
        for _ in range(0, 72):
            next_byte = NumericValue(self.buffer[pointer])
            if next_byte.hex() == "00" or next_byte.hex() == "FF":
                pointer += 32
            else:
                name = "{}".format(self.read_sequence(pointer, 8, decode=True).replace(" ", ""))
                pointer += 8
                extension = "{}".format(self.read_sequence(pointer, 3, decode=True))
                pointer += 3
                file_type = NumericValue(self.buffer[pointer])
                pointer += 1
                data_type = NumericValue(self.buffer[pointer])
                pointer += 1
                starting_granule = NumericValue(self.buffer[pointer])
                pointer += 1
                bytes_in_last_sector = self.read_word(pointer)
                pointer += 18

                # Set up data definitions
                exec_addr = NoneValue()

                # If the file is binary, read the preamble and postamble, otherwise don't
                if file_type.int == 0x02:
                    preamble = MLPreamble()
                elif data_type.int == 0xFF:
                    preamble = ASCIIPreamble()
                else:
                    preamble = BasicPreamble()

                preamble.read(self.buffer, self.seek_granule(starting_granule.int))

                data_length = preamble.data_length.int
                if data_length == 0:
                    data_length = self.calculate_file_length(starting_granule.int, fat, bytes_in_last_sector.int)

                file_data, post_pointer = self.read_data(
                    starting_granule.int,
                    fat,
                    preamble=preamble,
                    data_length=data_length,
                )

                if preamble.is_ml():
                    postamble = Postamble()
                    postamble.read(self.buffer, post_pointer)
                    exec_addr = postamble.exec_addr

                coco_file = CoCoFile(
                    name=name,
                    extension=extension,
                    type=file_type,
                    data_type=data_type,
                    load_addr=preamble.load_addr,
                    exec_addr=exec_addr,
                    data=file_data,
                    ignore_gaps=True
                )
                files.append(coco_file)

        return files

    @staticmethod
    def calculate_file_length(granule, fat, bytes_in_last_sector):
        """
        Calculates the length of the file without using preamble data. It does so by
        calculating how many granules are used as described in the FAT, and then
        calculating how many sectors are used in the final granule of the file,
        and adding the final number of bytes used in the last sector of the last
        granule.

        :param granule: the granule where the file starts at
        :param fat: the file allocation table data
        :param bytes_in_last_sector: the number of bytes stored in the last sector
        :return: the total bytes used by the file
        """
        is_last_granule = False
        total_bytes = 0

        while not is_last_granule:
            fat_entry = fat[granule]
            if (fat_entry & 0xC0) == 0xC0:
                is_last_granule = True
                total_bytes += ((fat_entry & 0x1F) - 1) * DiskConstants.BYTES_PER_SECTOR
                total_bytes += bytes_in_last_sector
            else:
                total_bytes += DiskConstants.HALF_TRACK_LEN
                granule = fat_entry

        return total_bytes

    def directory_entry_in_use(self, entry_number):
        """
        Returns True if the directory entry specified is in use, False otherwise.

        :param entry_number: the directory entry number to check
        :return: True if the entry is in use, False otherwise
        """
        if entry_number > 71 or entry_number < 0:
            raise VirtualFileValidationError("Invalid directory entry number [{}]".format(entry_number))

        return self.buffer[DiskConstants.DIR_OFFSET + (32 * entry_number)] not in [0x00, 0xFF]

    def find_empty_directory_entry(self):
        """
        Returns the first directory entry number that is not in use. Will return -1
        if all directory entry slots are in use.

        :return: the first directory entry number not in use, otherwise -1 if all used
        """
        for entry_number in range(0, 71):
            if not self.directory_entry_in_use(entry_number):
                return entry_number
        return -1

    def granule_in_use(self, granule_number):
        """
        Returns True if the granule number specified is in use, False otherwise.

        :param granule_number: the granule number to check
        :return: True if the granule is being used, False otherwise
        """
        if granule_number > 67 or granule_number < 0:
            raise VirtualFileValidationError("Invalid granule number [{}]".format(granule_number))

        return self.buffer[DiskConstants.FAT_OFFSET + granule_number] != 0xFF

    def find_empty_granule(self):
        """
        Returns the first granule number that is not in use. Will return -1 if
        all granules are in use.

        :return: the first granule number not in use, otherwise -1 if all used
        """
        if len(self.granule_fill_order) < DiskConstants.TOTAL_GRANULES:
            raise VirtualFileValidationError("granule_fill_order does not contain 68 granules")

        for granule_number in self.granule_fill_order:
            if not self.granule_in_use(granule_number):
                return granule_number

        raise VirtualFileValidationError("no free granules available for allocation")

    @staticmethod
    def calculate_granules_needed(file_data, preamble, postamble):
        """
        Given an array that contains the actual file data to store, calculates how many
        granules are needed on disk to store the file. A 0-byte file will always take
        1 granule on disk.

        :param file_data: the array-like structure containing the file data
        :param preamble: the preamble data
        :param postamble: the postamble data if it exists, else None
        :return: a count of the number of granules needed for the file
        """
        additional_len = preamble.length
        additional_len += postamble.length if postamble else 0
        return int((len(file_data) + additional_len) / DiskConstants.HALF_TRACK_LEN) + 1

    @staticmethod
    def calculate_sectors_needed(data_len):
        """
        Given the length of data that needs to be stored, calculates how many sectors are
        needed on disk. The routine assumes that a 5-byte preamble and 5-byte postamble
        will be appended to the file. A 0-byte file will always take 1 sector on disk.

        :param data_len: the length of data to store
        :return: the number of sectors needed to store the file on disk
        """
        return int(data_len / DiskConstants.BYTES_PER_SECTOR) + 1

    @staticmethod
    def calculate_last_sector_bytes_used(file_data, preamble, postamble):
        """
        Given an array structure that contains the data to be saved to the virtual disk,
        calculates how many bytes will be used in the last sector of the last granule
        for the file.

        :param file_data: an array-like structure with file data in it
        :param preamble: the preamble data
        :param postamble: the postamble data if it exists, else None
        :return: the number of bytes stored in the last sector of the last granule
        """
        granules_needed = DiskFile.calculate_granules_needed(file_data, preamble, postamble)

        additional_len = preamble.length
        additional_len += postamble.length if postamble else 0

        file_data_len = len(file_data) + additional_len
        full_granule_len = (granules_needed - 1) * DiskConstants.HALF_TRACK_LEN
        file_data_len -= full_granule_len

        # Calculate number of sectors needed, find number of bytes in last sector
        sectors_needed = DiskFile.calculate_sectors_needed(file_data_len)
        sectors_needed -= 1
        file_data_len -= sectors_needed * DiskConstants.BYTES_PER_SECTOR
        return file_data_len

    @staticmethod
    def calculate_last_granules_sectors_used(file_data, preamble, postamble):
        """
        Given an array-like structure that contains data to be saved to the virtual disk,
        calculates how many sectors are used in the last granule. Note that this function
        adds the pre- and post-amble bytes to the number of bytes used to store the file.

        :param file_data: an array-like structure with file data in it
        :param preamble: the preamble data
        :param postamble: the postamble data if it exists, else None
        :return: the number of sectors used in the last granule of the file
        """
        granules_needed = DiskFile.calculate_granules_needed(file_data, preamble, postamble)

        additional_len = preamble.length
        additional_len += postamble.length if postamble else 0
        file_data_len = len(file_data) + additional_len
        full_granule_len = (granules_needed - 1) * DiskConstants.HALF_TRACK_LEN
        file_data_len -= full_granule_len

        # Calculate number of sectors needed, find number of bytes in last sector
        return DiskFile.calculate_sectors_needed(file_data_len)

    @staticmethod
    def seek_granule(granule):
        """
        Returns a pointer to the start of the specified granule in the buffer.

        :param granule: the granule to seek to
        :return: a pointer to the specified granule
        """
        granule_offset = DiskConstants.HALF_TRACK_LEN * granule
        if granule > 33:
            granule_offset += DiskConstants.HALF_TRACK_LEN * 2
        return granule_offset

    def read_data(self, starting_granule, fat, preamble, data_length=0):
        """
        Reads a collection of data from a disk image.

        :param starting_granule: the starting granule for the file
        :param preamble: the preamble type to read
        :param data_length: the length of data to read
        :param fat: the File Allocation Table data for the disk
        :return: the raw data from the specified file and the pointer to the end of the file
        """
        pointer = self.seek_granule(starting_granule)
        file_data = []
        chunk_size = DiskConstants.HALF_TRACK_LEN

        if len(self.buffer[pointer:]) < data_length:
            raise VirtualFileValidationError("Unable to read data - insufficient bytes in buffer")

        # Skip over preamble if it exists
        if preamble:
            pointer += preamble.length
            chunk_size -= preamble.length

        # Check to see if we are reading more than one granule
        if data_length > chunk_size:
            for _ in range(chunk_size):
                file_data.append(self.buffer[pointer])
                data_length -= 1
                pointer += 1
            next_granule = fat[starting_granule]
            granule_data, pointer = self.read_data(next_granule, fat, None, data_length=data_length)
            file_data.extend(granule_data)
        else:
            for _ in range(data_length):
                file_data.append(self.buffer[pointer])
                pointer += 1
        return file_data, pointer

    def write_dir_entry(self, directory_entry_number, coco_file, first_granule, last_sector_bytes_used):
        """
        Writes a directory entry to the filesystem.

        :param directory_entry_number: the directory entry number to use
        :param coco_file: the CoCoFile object with the file data
        :param first_granule: the first granule to write to
        :param last_sector_bytes_used: the number of bytes used in the last sector
        """
        pointer = DiskConstants.DIR_OFFSET + (directory_entry_number * 32)
        for letter in coco_file.name.ljust(8, " ").upper():
            self.buffer[pointer] = ord(letter) if ord(letter) != 0x00 else 0x20
            pointer += 1

        for letter in coco_file.extension.ljust(3, " ").upper():
            self.buffer[pointer] = ord(letter) if ord(letter) != 0x00 else 0x20
            pointer += 1

        self.buffer[pointer] = coco_file.type.int
        pointer += 1

        self.buffer[pointer] = coco_file.data_type.int
        pointer += 1

        self.buffer[pointer] = first_granule
        pointer += 1

        bytes_used = NumericValue(last_sector_bytes_used)
        self.buffer[pointer] = bytes_used.high_byte()
        pointer += 1
        self.buffer[pointer] = bytes_used.low_byte()
        pointer += 1

        for _ in range(0, 16):
            self.buffer[pointer] = 0x00
            pointer += 1

    def write_bytes_to_buffer(self, pointer, data_to_write):
        """
        Given a pointer into the disk buffer, and an array-like object of bytes to write
        into the buffer, write the specified bytes into the buffer and return a pointer
        to the byte past the end of where bytes were written.

        :param pointer: a pointer into the disk buffer
        :param data_to_write: the array-like object of bytes to write
        :return: a pointer one byte past where the final byte was written
        """
        for byte_to_write in data_to_write:
            self.buffer[pointer] = byte_to_write
            pointer += 1
        return pointer

    def write_to_fat(self, allocated_granules, last_granule_sectors_used):
        """
        Given a list of granules used to store file data, writes out the granule linked
        list to the file allocation table. Each entry in the allocated_granules list points
        to the next granule used to store file data. The last allocated granule stores the number
        of sectors used in the final granule. Note that the last granule information has the
        two highest bits set in the byte, meaning that values of the final granule will
        range from $C0 - $C9.

        :param allocated_granules: the list of granules allocated to the file
        :param last_granule_sectors_used: the number of sectors used in the last granule
        """
        if not allocated_granules:
            return

        # Grab a pointer into the FAT
        pointer = DiskConstants.FAT_OFFSET

        # Write the next granule number in each granule
        if len(allocated_granules) > 1:
            for index, current_granule in enumerate(allocated_granules[:-1]):
                self.buffer[pointer + current_granule] = allocated_granules[index + 1]

        # Write out the number of sectors used in the last granule
        self.buffer[pointer + allocated_granules[-1]] = 0xC0 + last_granule_sectors_used

    def write_to_granules(self, file_data, allocated_granules, preamble, postamble, first_granule=True):
        """
        Given an array-like object of data that is a file to be written to the disk, and a list of
        granules to write data to, writes the data to the virtual disk in the granules that were
        allocated. Both pre- and post-amble data are supplied as well.

        :param file_data: an array-like object of bytes to be written to the virtual disk
        :param allocated_granules: the list of granules to write into
        :param preamble: the preamble data to write for the file
        :param postamble: the postamble data to write for the file
        :param first_granule: if True, writes the preamble to the granule
        """
        if not allocated_granules:
            return

        granule = allocated_granules[0]
        allocated_granules = allocated_granules[1:]
        pointer = self.seek_granule(granule)
        skip_bytes = 0

        if first_granule and preamble:
            pointer = preamble.write(self.buffer, pointer)
            skip_bytes += preamble.length

        if len(file_data) < (DiskConstants.HALF_TRACK_LEN - skip_bytes):
            pointer = self.write_bytes_to_buffer(pointer, file_data)
            if postamble:
                postamble.write(self.buffer, pointer)
        else:
            self.write_bytes_to_buffer(pointer, file_data[:DiskConstants.HALF_TRACK_LEN - skip_bytes])
            self.write_to_granules(
                file_data[DiskConstants.HALF_TRACK_LEN - skip_bytes:],
                allocated_granules,
                None,
                postamble,
                first_granule=False
            )

    def add_file(self, coco_file):
        """
        Adds a CoCoFile object to the virtual disk. It calculates the number of granules needed,
        allocates a directory entry and granules in the file allocation table, and then writes
        the file data, along with pre- and post-amble data as required.

        :param coco_file: the CoCoFile object to write
        """
        if coco_file.type.int == 0x02:
            preamble = MLPreamble()
            preamble.data_length = NumericValue(len(coco_file.data))
            preamble.load_addr = coco_file.load_addr
            postamble = Postamble()
            postamble.exec_addr = coco_file.exec_addr
        elif coco_file.data_type.int == 0xFF:
            preamble = ASCIIPreamble()
            postamble = None
        else:
            preamble = BasicPreamble()
            preamble.data_length = NumericValue(len(coco_file.data))
            postamble = None

        granules_needed = self.calculate_granules_needed(coco_file.data, preamble, postamble)

        # Check to see if there are enough granules for allocation
        allocated_granules = []
        while len(allocated_granules) < granules_needed:
            granule = self.find_empty_granule()
            allocated_granules.append(granule)
            self.buffer[DiskConstants.FAT_OFFSET + granule] = 0x99

        # Check to see if there is a free directory entry to save the file
        directory_entry = self.find_empty_directory_entry()
        if directory_entry == -1:
            raise VirtualFileValidationError("No free directory entry to save file")

        # Calculate the number of bytes used in the last sector, and the number of sectors in the last granule
        last_sector_bytes_used = self.calculate_last_sector_bytes_used(coco_file.data, preamble, postamble)
        last_granule_sectors_used = self.calculate_last_granules_sectors_used(coco_file.data, preamble, postamble)

        # Write out the directory entry
        self.write_dir_entry(directory_entry, coco_file, allocated_granules[0], last_sector_bytes_used)

        # Write the granule data to disk
        self.write_to_granules(coco_file.data, allocated_granules, preamble, postamble)

        # Write out the file allocation table data
        self.write_to_fat(allocated_granules, last_granule_sectors_used)

        # Blank out data in FAT that correspond to invalid granules
        for pointer in range(78660, 78848):
            self.buffer[pointer] = 0x00


# E N D   O F   F I L E #######################################################
