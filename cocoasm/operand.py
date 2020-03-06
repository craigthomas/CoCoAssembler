"""
Copyright (C) 2019 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from enum import Enum

from cocoasm.helpers import hex_value

# C O N S T A N T S ###########################################################

# Patten to recognize an expression
EXPR_REGEX = re.compile(
    r"^(?P<symbol0>[\d\w]+)(?P<operation>[\+\-\/\*])(?P<symbol1>[\d\w]+)"
)

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
    INDEXED = 3
    EXTENDED_INDIRECT = 4
    EXTENDED = 5
    DIRECT = 6
    RELATIVE = 7
    SYMBOL = 8
    EXPRESSION = 9
    VALUE = 10
    ADDRESS = 11


class Operand(object):
    def __init__(self, operand, original_symbol=None):
        self.operand = operand or ""
        self.variables = []
        self.operand_type = OperandType.UNKNOWN
        self.original_symbol = operand if original_symbol is None else original_symbol
        self.determine_operand_type()

    def __str__(self):
        return "Operand [{}, {}]".format(self.operand, self.operand_type)

    def determine_operand_type(self):
        if self.get_expression() != "":
            self.operand_type = OperandType.EXPRESSION
            return

        if self.is_indexed():
            self.operand_type = OperandType.INDEXED
            return

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
            operand_hex_value = hex_value(self.operand)
            self.operand_type = OperandType.DIRECT if len(operand_hex_value) < 3 else OperandType.EXTENDED
            return

        self.operand_type = OperandType.SYMBOL

    def get_original_symbol(self):
        return self.original_symbol

    def get_string_value(self):
        return str(self.operand)

    def get_operand_type(self):
        return self.operand_type

    def is_inherent(self):
        return self.get_operand_type() == OperandType.INHERENT

    def is_immediate(self):
        return self.get_operand_type() == OperandType.IMMEDIATE

    def is_indexed(self):
        return "," in self.operand if type(self.operand) is str else False

    def is_extended(self):
        return self.get_operand_type() == OperandType.EXTENDED

    def is_extended_indirect(self):
        return self.get_operand_type() == OperandType.EXTENDED_INDIRECT

    def is_symbol(self):
        return self.get_operand_type() == OperandType.SYMBOL

    def is_direct(self):
        return self.get_operand_type() == OperandType.DIRECT

    def is_value(self):
        return self.get_operand_type() == OperandType.VALUE

    def is_address(self):
        return self.get_operand_type() == OperandType.ADDRESS

    def get_immediate(self):
        """
        Returns true if the operand is immediate data.

        :return: True if the operand is immediate
        """
        match = IMM_REGEX.match(self.operand) or ""
        return match.group("value") if match else ""

    def get_extended_indirect(self):
        match = EXTENDED_INDIRECT_REGEX.match(self.operand) or ""
        return match.group("value") if match else ""

    def get_hex_value(self):
        match = HEX_REGEX.match(self.operand) or ""
        return match.group("value") if match else ""

    def get_extended(self):
        match = HEX_REGEX.match(self.operand) or ""
        return match.group("value") if match else ""

    def get_expression(self):
        match = EXPR_REGEX.match(self.operand) or ""
        return [match.group("symbol0"), match.group("operation"), match.group("symbol1")] if match else ""

    def check_symbol(self, symbol_table):
        if self.is_symbol():
            symbol_string = self.get_string_value()
            if symbol_string not in symbol_table:
                raise ValueError("Unknown symbol [{}]".format(symbol_string))
            symbol = symbol_table[symbol_string]
            if symbol.is_value():
                new_operand = Operand(symbol_table[symbol_string].get_value(), symbol_string)
                self.operand_type = new_operand.get_operand_type()
                self.operand = new_operand.get_string_value()
            else:
                self.operand_type = OperandType.ADDRESS
                self.operand = symbol_table[symbol_string].get_address()


# E N D   O F   F I L E #######################################################
