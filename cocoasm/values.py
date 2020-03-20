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

# Patten to recognize an expression
EXPRESSION_REGEX = re.compile(
    r"^(?P<left>[\d\w]+)(?P<operation>[+\-/*])(?P<right>[\d\w]+)$"
)

# C L A S S E S  ##############################################################


class ValueType(Enum):
    UNKNOWN = 0
    NUMERIC = 1
    STRING = 2
    SYMBOL = 3
    ADDRESS = 4
    EXPRESSION = 5
    NONE = 6


class Value(ABC):
    def __init__(self, value):
        self.original_string = value
        self.type = ValueType.UNKNOWN
        self.resolved = True

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
        return self.type == value_type

    @classmethod
    def create_from_str(cls, value):
        print("creating Value from {}".format(value))
        try:
            return NumericValue(value)
        except ValueError:
            pass

        try:
            return StringValue(value)
        except ValueError:
            pass

        raise ValueError("unknown value type")

    @abstractmethod
    def hex(self):
        """
        Returns the hex representation of the object.

        :return: the hex representation of the object
        """
        pass

    @abstractmethod
    def hex_len(self):
        """
        Returns the full length of the hex representation.

        :return: the full number of hex characters
        """
        pass


class NoneValue(Value):
    def __init__(self, value):
        super().__init__(value)
        self.type = ValueType.NONE

    def hex(self):
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

    def hex(self):
        """
        Returns a hex string representation of the object.

        :return: the hex representation of the object
        """
        return "".join(self.hex_array)

    def hex_len(self):
        """
        Returns the full length of the hex representation.

        :return: the full number of hex characters
        """
        return len(self.hex())


class NumericValue(Value):
    """
    Represents a numeric value that can be retrieved as an integer or hex value
    string.
    """
    def __init__(self, value):
        super().__init__(value)
        self.int_value = 0
        self.type = ValueType.NUMERIC
        data = HEX_REGEX.match(value)
        if data:
            if len(data.group("value")) > 4:
                raise ValueError("hex value length cannot exceed 4 characters")
            self.int_value = int(data.group("value"), 16)
            return

        data = INT_REGEX.match(value)
        if data:
            self.int_value = int(data.group("value"), 10)
            if self.int_value > 65535:
                raise ValueError("integer value cannot exceed 65535")
            return

        raise ValueError("[{}] is neither integer or hex value".format(value))

    def int(self):
        """
        Returns an integer value for the object.

        :return: the integer value of the object
        """
        return self.int_value

    def hex(self):
        """
        Returns a hex string representation of the object.

        :return: the hex representation of the object
        """
        size = self.hex_len()
        size += 1 if size % 2 == 1 else 0
        format_specifier = "{{:0>{}X}}".format(size)
        return format_specifier.format(self.int())

    def hex_len(self):
        """
        Returns the full length of the hex representation.

        :return: the full number of hex characters
        """
        return len(hex(self.int_value)[2:])


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
            raise ValueError("{} is not a valid symbol".format(value))
        self.value = value

    def hex(self):
        """
        Returns a hex string representation of the object.

        :return: the hex representation of the object
        """
        return self.value.hex() if self.resolved else ""

    def hex_len(self):
        """
        Returns the full length of the hex representation.

        :return: the full number of hex characters
        """
        return self.value.hex_len() if self.resolved else 0


class AddressValue(Value):
    """
    Represents a symbol value that stores an index to a statement.
    """
    def __init__(self, value):
        super().__init__(value)
        self.int_value = int(value)
        self.type = ValueType.ADDRESS

    def get_integer(self):
        """
        Returns an integer value for the object.

        :return: the integer value of the object
        """
        return self.int_value

    def hex(self):
        """
        Returns a hex string representation of the object.

        :return: the hex representation of the object
        """
        size = self.hex_len()
        size += 1 if size % 2 == 1 else 0
        format_specifier = "{{:0>{}X}}".format(size)
        return format_specifier.format(self.get_integer())

    def hex_len(self):
        """
        Returns the full length of the hex representation.

        :return: the full number of hex characters
        """
        return len(hex(self.int_value)[2:])


class ExpressionValue(Value):
    """
    Represents a symbol value that stores an address or index.
    """
    def __init__(self, value):
        super().__init__(value)
        self.resolved = False
        self.value = None
        self.type = ValueType.EXPRESSION
        match = EXPRESSION_REGEX.match(value)
        if not match:
            raise ValueError("supplied value is not a valid expression")
        self.left = match.group("left")
        self.right = match.group("right")
        self.operation = match.group("operation")

    def hex(self):
        """
        Returns a hex string representation of the object.

        :return: the hex representation of the object
        """
        return self.value.hex() if self.resolved else ""

    def hex_len(self):
        """
        Returns the full length of the hex representation.

        :return: the full number of hex characters
        """
        return self.value.hex_len() if self.resolved else 0

# E N D   O F   F I L E #######################################################
