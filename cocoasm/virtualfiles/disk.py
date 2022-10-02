"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from typing import NamedTuple

from cocoasm.virtualfiles.coco_file import CoCoFile
from cocoasm.virtualfiles.virtual_file_container import VirtualFileContainer
from cocoasm.values import Value, NumericValue, NoneValue
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


class Preamble(NamedTuple):
    """
    The Preamble class is used to store information relating to a binary file
    on a disk image. The Preamble only contains the load address and the length
    of data for the binary file.
    """
    load_addr: Value = NoneValue()
    data_length: Value = NoneValue()


class Postamble(NamedTuple):
    """
    The Postamble class is used to store information relating t a binary file
    on a disk image. The Postamble is stored at the end of a binary file and
    contains the exec address for the binary.
    """
    exec_addr: Value = NoneValue()


class DiskFile(VirtualFileContainer):
    def __init__(self, buffer=None, granule_fill_order=None):
        super().__init__(buffer=buffer)
        if buffer is None:
            self.buffer = [0xFF] * DiskConstants.IMAGE_SIZE
        self.granule_fill_order = DiskConstants.GRANULE_FILL_ORDER if not granule_fill_order else granule_fill_order

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

    def read_word(self, pointer):
        """
        Reads a 16-bit value from the buffer starting at the specified
        pointer offset.

        :param pointer: the offset into the buffer to read from
        :return: the NumericValue read
        """
        if len(self.buffer) < 2 or (len(self.buffer[pointer:]) < 2):
            raise VirtualFileValidationError("Unable to read word - insufficient bytes in buffer")

        word_int = int(self.buffer[pointer])
        word_int = word_int << 8
        word_int |= int(self.buffer[pointer + 1])
        return NumericValue(word_int)

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
                pointer += 19

                # TODO: if the type is not binary, then don't look for preamble or postamble
                preamble = self.read_preamble(starting_granule.int)

                file_data, post_pointer = self.read_data(
                    starting_granule.int,
                    fat,
                    has_preamble=True,
                    data_length=preamble.data_length.int,
                )

                postamble = self.read_postamble(post_pointer)

                coco_file = CoCoFile(
                    name=name,
                    extension=extension,
                    type=file_type,
                    data_type=data_type,
                    load_addr=preamble.load_addr,
                    exec_addr=postamble.exec_addr,
                    data=file_data,
                    ignore_gaps=True
                )
                files.append(coco_file)

        return files

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
        return -1

    @staticmethod
    def calculate_granules_needed(file_data):
        """
        Given an array that contains the actual file data to store, calculates how many
        granules are needed on disk to store the file. The routine assumes that a 5-byte
        preamble and 5-byte postamble will be appended to the file. A 0-byte file will
        always take 1 granule on disk.

        :param file_data: the array-like structure containing the file data
        :return: a count of the number of granules needed for the file
        """
        pre_post_amble_len = DiskConstants.PREAMBLE_LEN + DiskConstants.POSTAMBLE_LEN
        return int((len(file_data) + pre_post_amble_len) / DiskConstants.HALF_TRACK_LEN) + 1

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
    def calculate_last_sector_bytes_used(file_data):
        """
        Given an array structure that contains the data to be saved to the virtual disk,
        calculates how many bytes will be used in the last sector of the last granule
        for the file.

        :param file_data: an array-like structure with file data in it
        :return: the number of bytes stored in the last sector of the last granule
        """
        granules_needed = DiskFile.calculate_granules_needed(file_data)

        file_data_len = len(file_data) + DiskConstants.PREAMBLE_LEN + DiskConstants.POSTAMBLE_LEN
        full_granule_len = (granules_needed - 1) * DiskConstants.HALF_TRACK_LEN
        file_data_len -= full_granule_len

        # Calculate number of sectors needed, find number of bytes in last sector
        sectors_needed = DiskFile.calculate_sectors_needed(file_data_len)
        sectors_needed -= 1
        file_data_len -= sectors_needed * DiskConstants.BYTES_PER_SECTOR
        return file_data_len

    @staticmethod
    def calculate_last_granules_sectors_used(file_data):
        """
        Given an array-like structure that contains data to be saved to the virtual disk,
        calculates how many sectors are used in the last granule. Note that this function
        adds the pre- and post-amble bytes to the number of bytes used to store the file.

        :param file_data: an array-like structure with file data in it
        :return: the number of sectors used in the last granule of the file
        """
        granules_needed = DiskFile.calculate_granules_needed(file_data)

        file_data_len = len(file_data) + DiskConstants.PREAMBLE_LEN + DiskConstants.POSTAMBLE_LEN
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

    def read_preamble(self, starting_granule):
        """
        Reads the preamble data for the file. The preamble is a collection of 5
        bytes at the start of a binary file:

            byte 0 - always $00
            byte 1,2 - the data length of the file
            byte 3,4 - the load address for the file

        :param starting_granule: the granule number that contains the preamble
        :return: a populated Preamble object
        """
        pointer = self.seek_granule(starting_granule)
        if not self.validate_sequence(pointer, [0x00]):
            raise VirtualFileValidationError("Invalid preamble flag")

        return Preamble(
            data_length=self.read_word(pointer + 1),
            load_addr=self.read_word(pointer + 3),
        )

    def read_postamble(self, pointer):
        """
        Reads the postamble of a binary file. The postamble is a collection of
        5 bytes as follows:

            byte 0 - always $FF
            byte 1,2 - always $00, $00
            byte 3,4 - the exec address of the binary file

        :param pointer: a pointer to the postamble data
        :return: a populated Postamble object
        """
        if not self.validate_sequence(pointer, [0xFF, 0x00, 0x00]):
            raise VirtualFileValidationError("Invalid postamble flags")

        return Postamble(
            exec_addr=self.read_word(pointer + 3),
        )

    def read_data(self, starting_granule, fat, has_preamble=False, data_length=0):
        """
        Reads a collection of data from a disk image.

        :param starting_granule: the starting granule for the file
        :param has_preamble: whether there is a preamble to be read
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
        if has_preamble:
            pointer += DiskConstants.PREAMBLE_LEN
            chunk_size -= DiskConstants.PREAMBLE_LEN

        # Check to see if we are reading more than one granule
        if data_length > chunk_size:
            for _ in range(chunk_size):
                file_data.append(self.buffer[pointer])
                data_length -= 1
                pointer += 1
            next_granule = fat[starting_granule]
            granule_data, pointer = self.read_data(next_granule, fat, data_length=data_length, has_preamble=False)
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

    def write_preamble(self, preamble, granule):
        """
        Given preamble data, writes the preamble to the start of the specified granule.

        :param preamble: the preamble data to write
        :param granule: the granule number to write to
        """
        pointer = self.seek_granule(granule)

        # First byte of preamble is $00
        self.buffer[pointer] = 0x00
        pointer += 1

        self.buffer[pointer] = preamble.data_length.high_byte()
        pointer += 1
        self.buffer[pointer] = preamble.data_length.low_byte()
        pointer += 1

        self.buffer[pointer] = preamble.load_addr.high_byte()
        pointer += 1
        self.buffer[pointer] = preamble.load_addr.low_byte()

    def write_postamble(self, postamble, pointer):
        """
        Given postamble data, writes the postamble format into the buffer at the
        specified pointer location.

        :param postamble: the postamble data to write
        :param pointer: a pointer into the buffer where to write the postamble data
        """
        if not postamble:
            return pointer

        # First three bytes of postamble is always $FF $00 $00
        self.buffer[pointer] = 0xFF
        pointer += 1
        self.buffer[pointer] = 0x00
        pointer += 1
        self.buffer[pointer] = 0x00
        pointer += 1

        self.buffer[pointer] = postamble.exec_addr.high_byte()
        pointer += 1
        self.buffer[pointer] = postamble.exec_addr.low_byte()

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
            self.write_preamble(preamble, granule)
            pointer += DiskConstants.PREAMBLE_LEN
            skip_bytes += DiskConstants.PREAMBLE_LEN

        if len(file_data) < (DiskConstants.HALF_TRACK_LEN - skip_bytes):
            pointer = self.write_bytes_to_buffer(pointer, file_data)
            self.write_postamble(postamble, pointer)
        else:
            self.write_bytes_to_buffer(pointer, file_data[:DiskConstants.HALF_TRACK_LEN])
            self.write_to_granules(
                file_data[DiskConstants.HALF_TRACK_LEN:],
                allocated_granules,
                preamble,
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
        granules_needed = self.calculate_granules_needed(coco_file.data)

        # Check to see if there are enough granules for allocation
        allocated_granules = []
        for granule in range(DiskConstants.TOTAL_GRANULES):
            if not self.granule_in_use(granule):
                allocated_granules.append(granule)
                if len(allocated_granules) == granules_needed:
                    break

        if len(allocated_granules) != granules_needed:
            raise VirtualFileValidationError("Not enough free granules to save file")

        # Check to see if there is a free directory entry to save the file
        directory_entry = self.find_empty_directory_entry()
        if directory_entry == -1:
            raise VirtualFileValidationError("No free directory entry to save file")

        # Calculate the number of bytes used in the last sector, and the number of sectors in the last granule
        last_sector_bytes_used = self.calculate_last_sector_bytes_used(coco_file.data)
        last_granule_sectors_used = self.calculate_last_granules_sectors_used(coco_file.data)

        # Write out the directory entry
        self.write_dir_entry(directory_entry, coco_file, allocated_granules[0], last_sector_bytes_used)

        # Generate pre- and post-amble as required
        preamble = Preamble(
            load_addr=coco_file.load_addr,
            data_length=NumericValue(len(coco_file.data))
        )
        postamble = Postamble(
            exec_addr=coco_file.exec_addr
        )

        # Write the granule data to disk
        self.write_to_granules(coco_file.data, allocated_granules, preamble, postamble)

        # Write out the file allocation table data
        self.write_to_fat(allocated_granules, last_granule_sectors_used)

        # Blank out data in FAT that correspond to invalid granules
        for pointer in range(78660, 78848):
            self.buffer[pointer] = 0x00


# E N D   O F   F I L E #######################################################
