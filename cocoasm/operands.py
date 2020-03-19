"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from abc import ABC, abstractmethod
from copy import copy
from enum import Enum

from cocoasm.values import StringValue, NumericValue, SymbolValue,  \
    NoneValue, ExpressionValue, ValueType, AddressValue
from cocoasm.symbol import SymbolType

# C O N S T A N T S ###########################################################

# Pattern to recognize an immediate value
IMMEDIATE_REGEX = re.compile(
    r"^#(?P<value>.*)"
)

# Pattern to recognize an immediate value
DIRECT_REGEX = re.compile(
    r"^\<(?P<value>.*)"
)

# Pattern to recognize an immediate value
EXTENDED_REGEX = re.compile(
    r"^\<(?P<value>.*)"
)

# Pattern to recognize an indexed value
EXTENDED_INDIRECT_REGEX = re.compile(
    r"^\[(?P<value>.*)\]"
)


# C L A S S E S ###############################################################


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


class Operand(ABC):
    def __init__(self, mnemonic):
        self.type = OperandType.UNKNOWN
        self.operand_string = ""
        self.mnemonic = mnemonic
        self.requires_resolution = False
        self.sub_expression = NoneValue(None)

    @classmethod
    def create_from_str(cls, operand_string, mnemonic):
        try:
            return InherentOperand(operand_string, mnemonic)
        except ValueError:
            pass

        try:
            return ImmediateOperand(operand_string, mnemonic)
        except ValueError:
            pass

        try:
            return DirectOperand(operand_string, mnemonic)
        except ValueError:
            pass

        try:
            return ExtendedOperand(operand_string, mnemonic)
        except ValueError:
            pass

        try:
            return ExtendedIndirectOperand(operand_string, mnemonic)
        except ValueError:
            pass

        try:
            return IndexedOperand(operand_string, mnemonic)
        except ValueError:
            pass

        try:
            return ExpressionOperand(operand_string, mnemonic)
        except ValueError:
            pass

        try:
            return UnknownOperand(operand_string, mnemonic)
        except ValueError:
            pass

        raise ValueError("unknown operand type {}".format(operand_string))

    def is_type(self, operand_type):
        return self.type == operand_type

    def get_operand_string(self):
        return self.operand_string

    def parse_sub_expression(self, value):
        try:
            self.sub_expression = NumericValue(value)
            return
        except ValueError:
            pass

        if self.mnemonic == "FCC":
            try:
                self.sub_expression = StringValue(value)
                return
            except ValueError:
                pass

        try:
            self.sub_expression = SymbolValue(value)
            self.requires_resolution = True
            return
        except ValueError:
            pass

        try:
            self.sub_expression = ExpressionValue(value)
            self.requires_resolution = True
            return
        except ValueError:
            pass

        raise ValueError("cannot parse sub expression")

    def requires_resolution(self):
        return self.requires_resolution

    def get_hex_value(self):
        return self.sub_expression.get_hex_str()

    def resolve_symbols(self, symbol_table):
        if not self.sub_expression.is_type(ValueType.SYMBOL):
            return

        symbol_label = self.sub_expression.get_ascii_str()
        if symbol_label not in symbol_table:
            raise ValueError("{} not in symbol table".format(symbol_label))

        symbol = symbol_table[symbol_label]
        if symbol.is_type(ValueType.ADDRESS):
            self.sub_expression = AddressValue(symbol.get_integer())
            self.type = OperandType.EXTENDED if self.type == OperandType.UNKNOWN else self.type
            return

        if symbol.is_type(ValueType.NUMERIC):
            self.sub_expression = copy(symbol)
            self.type = OperandType.DIRECT if self.sub_expression.get_hex_length() == 2 else OperandType.EXTENDED


class UnknownOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.operand_string = operand_string
        self.parse_sub_expression(operand_string)


class InherentOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.INHERENT
        if operand_string:
            raise ValueError("inherent operands do not have values")


class ImmediateOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.IMMEDIATE
        self.operand_string = operand_string
        self.parsed_value = None
        self.sub_expression = None
        self.parse_operand(operand_string)

    def parse_operand(self, operand_string):
        """
        Returns true if the operand is immediate data.

        :return: True if the operand is immediate
        """
        match = IMMEDIATE_REGEX.match(self.operand_string)
        if not match:
            raise ValueError("operand is not an immediate value")
        self.parsed_value = match.group("value")
        self.parse_sub_expression(self.parsed_value)


class DirectOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.DIRECT
        self.operand_string = operand_string
        self.parsed_value = None
        self.sub_expression = None
        self.parse_operand(operand_string)

    def parse_operand(self, operand_string):
        """
        Returns true if the operand is immediate data.

        :return: True if the operand is immediate
        """
        match = DIRECT_REGEX.match(self.operand_string)
        if match:
            self.parsed_value = match.group("value")
        else:
            self.parsed_value = self.operand_string
            self.parse_sub_expression(self.parsed_value)
            if self.sub_expression is None:
                raise ValueError("operand is not a direct value")
            if self.sub_expression.get_hex_byte_size() != 1:
                raise ValueError("operand is not a direct value")


class ExtendedOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.EXTENDED
        self.operand_string = operand_string
        self.parsed_value = None
        self.sub_expression = None
        self.parse_operand(operand_string)

    def parse_operand(self, operand_string):
        """
        Returns true if the operand is immediate data.

        :return: True if the operand is immediate
        """
        match = EXTENDED_REGEX.match(self.operand_string)
        if match:
            self.parsed_value = match.group("value")
        else:
            self.parsed_value = self.operand_string
            self.parse_sub_expression(self.parsed_value)
            if self.sub_expression is None:
                raise ValueError("operand is not an extended value")
            if self.sub_expression.get_hex_byte_size() != 2:
                raise ValueError("operand is not an extended value")


class ExtendedIndirectOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.EXTENDED_INDIRECT
        self.operand_string = operand_string
        self.parsed_value = None
        self.sub_expression = None
        self.parse_operand(operand_string)

    def parse_operand(self, operand_string):
        """
        Returns true if the operand is immediate data.

        :return: True if the operand is immediate
        """
        match = EXTENDED_INDIRECT_REGEX.match(self.operand_string)
        if not match:
            raise ValueError("operand is not an extended indirect value")
        self.parsed_value = match.group("value")
        self.parse_sub_expression(self.parsed_value)


class IndexedOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.INDEXED
        self.operand_string = operand_string
        self.parsed_value = None
        self.sub_expression = None
        self.parse_operand(operand_string)

    def parse_operand(self, operand_string):
        """
        Returns true if the operand is immediate data.

        :return: True if the operand is immediate
        """
        if "," not in operand_string:
            raise ValueError("operand is not an indexed value")
        self.parsed_value = operand_string
        self.sub_expression = NoneValue(operand_string)


class ExpressionOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.EXPRESSION
        self.operand_string = operand_string
        self.sub_expression = None
        self.parse_operand(operand_string)

    def parse_operand(self, operand_string):
        """
        Returns true if the operand is immediate data.

        :return: True if the operand is immediate
        """
        self.sub_expression = ExpressionValue(operand_string)

# E N D   O F   F I L E #######################################################
