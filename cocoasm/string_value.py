"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# C L A S S E S  ##############################################################


class StringValue(object):
    """
    Represents a numeric value that can be retrieved as an integer or hex value
    string.
    """
    def __init__(self, value):
        self.original_string = None
        self.hex_array = []
        self.parse_string(value)

    def __str__(self):
        return self.get_hex_str()

    def parse_string(self, value):
        """
        Parses an input string value. Input strings are simply string values
        that must begin and end with the same character.

        :param value: the value to parse
        """
        delimiter = value[0]
        if not value[-1] == delimiter:
            raise ValueError("string must begin and end with same delimiter")
        self.original_string = value[1:-1]
        self.hex_array = ["{:X}".format(ord(x)) for x in value[1:-1]]

    def get_ascii_str(self):
        """
        Returns the ascii representation of the string

        :return: the ascii representation of the string
        """
        return self.original_string

    def get_hex_str(self):
        """
        Returns a hex string representation of the object.

        :return: the hex representation of the object
        """
        return "".join(self.hex_array)

    def get_hex_length(self):
        """
        Returns the full length of the hex representation.

        :return: the full number of hex characters
        """
        return len(self.get_hex_str())

    def get_hex_byte_size(self):
        """
        Returns how many bytes are in the hex representation.

        :return: the number of hex bytes in the object
        """
        return int(self.get_hex_length() / 2)

# E N D   O F   F I L E #######################################################
