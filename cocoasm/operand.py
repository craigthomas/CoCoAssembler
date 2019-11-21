"""
Copyright (C) 2019 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from enum import Enum

from cocoasm.helpers import hex_value, decimal_value

# C O N S T A N T S ###########################################################

# Pattern to recognize an immediate value
IMM_REGEX = re.compile(
    r"^#(?P<value>.*)"
)

# Pattern to recognize an indexed value
EXTENDED_INDIRECT_REGEX = re.compile(
    r"^\[(?P<value>.*)\]"
)

# Pattern to recognize a hex value
HEX_REGEX = re.compile(
    r"^\$(?P<value>[0-9a-fA-F]+)"
)

# Pattern to recognize an integer value
INT_REGEX = re.compile(
    r"^(?P<value>[\d]+)"
)

# C L A S S E S  ##############################################################


class OperandType(Enum):
    UNKNOWN = 0
    INHERENT = 1
    IMMEDIATE = 2
    INDIRECT = 3
    EXTENDED_INDIRECT = 4
    EXTENDED = 5
    DIRECT = 6
    RELATIVE = 7
    SYMBOL = 8
    EXPRESSION = 9


class Operand(object):
    def __init__(self, operand):
        self.operand = operand or ""
        self.variables = []
        self.operand_type = OperandType.UNKNOWN
        self.determine_operand_type()

    def determine_operand_type(self):
        if self.operand == "":
            self.operand_type = OperandType.INHERENT
            return

        if self.get_immediate() != "":
            self.operand_type = OperandType.IMMEDIATE
            return

        if self.get_extended_indirect() != "":
            self.operand_type = OperandType.EXTENDED_INDIRECT
            return

        if self.get_hex_value() != "":
            self.operand_type = OperandType.EXTENDED
            return

    def get_string_value(self):
        return str(self.operand)

    def get_operand_type(self):
        return self.operand_type

    def is_inherent(self):
        return self.get_operand_type() == OperandType.INHERENT

    def is_immediate(self):
        return self.get_operand_type() == OperandType.IMMEDIATE

    def get_immediate(self):
        """
        Returns true if the operand is immediate data.

        :return: True if the operand is immediate
        """
        return IMM_REGEX.match(self.operand) or ""

    def get_extended_indirect(self):
        return EXTENDED_INDIRECT_REGEX.match(self.operand) or ""

    def get_hex_value(self):
        return HEX_REGEX.match(self.operand) or ""

# E N D   O F   F I L E #######################################################
