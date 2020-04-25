"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from abc import ABC, abstractmethod
from enum import Enum

# C O N S T A N T S ###########################################################

# Pattern to recognize a hex value
HEX_REGEX = re.compile(
    r"^\$(?P<value>[0-9a-fA-F]+)$"
)

# Pattern to recognize an integer value
INT_REGEX = re.compile(
    r"^(?P<value>[\d]+)$"
)

# Pattern to recognize a symbol value
SYMBOL_REGEX = re.compile(
    r"^(?P<value>[a-zA-Z0-9@]+)$"
)

# C L A S S E S  ##############################################################


class ValueType(Enum):
    """
    The ValueType enumeration stores what type of value is stored in a
    particular class.
    """
    UNKNOWN = 0
    NUMERIC = 1
    STRING = 2
    SYMBOL = 3
    ADDRESS = 4
    NONE = 5


class Value(ABC):
    """
    A Value stores a basic value recognized by the assembler. Values are
    one of several types, being Unknown, Numeric, String, Symbol,
    Address, Expression or a special None type.
    """
    def __init__(self, value, size_hint=0):
        self.original_string = value
        self.type = ValueType.UNKNOWN
        self.resolved = True
        self.int = 0
        self.size_hint = size_hint

    def __str__(self):
        return self.hex()

    def ascii(self):
        """
        Returns the original ascii representation of the value.

        :return: the original ascii representation of the value
        """
        return self.original_string

    def byte_len(self):
        """
        Returns how many bytes are in the hex representation.

        :return: the number of hex bytes in the object
        """
        return int(self.hex_len() / 2)

    def is_type(self, value_type):
        """
        Returns whether the Value is the type specified.

        :param value_type: the ValueType to check
        :return: True if the type of the Value is the type being checked, False otherwise
        """
        return self.type == value_type

    def high_byte(self):
        if self.hex_len() < 2:
            return 0x00
        return int(self.hex()[0:2], 16)

    def low_byte(self):
        if self.hex_len() < 1:
            return 0x00
        if self.hex_len() < 2:
            return int(self.hex()[0:2], 16)
        return int(self.hex()[2:], 16)

    @abstractmethod
    def hex(self, size=0):
        """
        Returns the hex representation of the object.

        :return: the hex representation of the object
        """

    @abstractmethod
    def hex_len(self):
        """
        Returns the full length of the hex representation.

        :return: the full number of hex characters
        """

    @classmethod
    def create_from_str(cls, value, instruction):
        """
        Parses the value by trying to instantiate various Value classes.

        :param value: the string value to parse
        :param instruction: the instruction
        :return: the Value class parsed
        """
        try:
            return NumericValue(value)
        except ValueError:
            pass

        if instruction.is_string_define:
            try:
                return StringValue(value)
            except ValueError:
                pass

        try:
            return SymbolValue(value)
        except ValueError:
            pass

        raise ValueError("[{}] is an invalid value".format(value))


class NoneValue(Value):
    """
    Represents a special None type value that does not store any information.
    """
    def __init__(self, value=None):
        super().__init__(value)
        self.type = ValueType.NONE
        self.original_string = ""

    def hex(self, size=0):
        return ""

    def hex_len(self):
        return 0


class StringValue(Value):
    """
    Represents a numeric value that can be retrieved as an integer or hex value
    string.
    """
    def __init__(self, value):
        super().__init__(value)
        self.hex_array = []
        self.type = ValueType.STRING
        delimiter = value[0]
        if not value[-1] == delimiter:
            raise ValueError("string must begin and end with same delimiter")
        self.original_string = value[1:-1]
        self.hex_array = ["{:X}".format(ord(x)) for x in value[1:-1]]

    def hex(self, size=0):
        return "".join(self.hex_array)

    def hex_len(self):
        return len(self.hex())


class NumericValue(Value):
    """
    Represents a numeric value that can be retrieved as an integer or hex value
    string.
    """
    def __init__(self, value, size_hint=0):
        super().__init__(value, size_hint)
        self.type = ValueType.NUMERIC
        if type(value) == int:
            self.int = value
            if self.int > 65535:
                raise ValueError("integer value cannot exceed 65535")
            return

        data = HEX_REGEX.match(value)
        if data:
            if len(data.group("value")) > 4:
                raise ValueError("hex value length cannot exceed 4 characters")
            self.int = int(data.group("value"), 16)
            return

        data = INT_REGEX.match(value)
        if data:
            self.int = int(data.group("value"), 10)
            if self.int > 65535:
                raise ValueError("integer value cannot exceed 65535")
            return

        raise ValueError("[{}] is neither integer or hex value".format(value))

    def hex(self, size=0):
        if self.size_hint != 0:
            size = self.size_hint
        if size == 0:
            size = self.hex_len()
            size += 1 if size % 2 == 1 else 0
        format_specifier = "{{:0>{}X}}".format(size)
        return format_specifier.format(self.int)

    def hex_len(self):
        if self.size_hint:
            return self.size_hint
        length = len(hex(self.int)[2:])
        length += 1 if length % 2 == 1 else 0
        return length


class SymbolValue(Value):
    """
    Represents a symbol value that stores an address or index.
    """
    def __init__(self, value):
        super().__init__(value)
        self.value = None
        self.resolved = False
        self.type = ValueType.SYMBOL
        data = SYMBOL_REGEX.match(value)
        if not data:
            raise ValueError("[{}] is not a valid symbol".format(value))
        self.value = value

    def hex(self, size=0):
        return self.value.hex() if self.resolved else ""

    def hex_len(self):
        return self.value.hex_len() if self.resolved else 0


class AddressValue(Value):
    """
    Represents a symbol value that stores an index to a statement.
    """
    def __init__(self, value):
        super().__init__(value)
        self.int = int(value)
        self.type = ValueType.ADDRESS

    def hex(self, size=0):
        if size == 0:
            size = self.hex_len()
            size += 1 if size % 2 == 1 else 0
        format_specifier = "{{:0>{}X}}".format(size)
        return format_specifier.format(self.int)

    def hex_len(self):
        return len(hex(self.int)[2:])

# E N D   O F   F I L E #######################################################
