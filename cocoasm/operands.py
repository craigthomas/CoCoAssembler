"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from abc import ABC
from copy import copy
from enum import Enum

from cocoasm.values import StringValue, NumericValue, SymbolValue,  \
    NoneValue, ExpressionValue, ValueType, AddressValue

# C O N S T A N T S ###########################################################

# Pattern to recognize an immediate value
IMMEDIATE_REGEX = re.compile(
    r"^#(?P<value>.*)"
)

# Pattern to recognize an immediate value
DIRECT_REGEX = re.compile(
    r"^<(?P<value>.*)"
)

# Pattern to recognize an immediate value
EXTENDED_REGEX = re.compile(
    r"^<(?P<value>.*)"
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
        self.value = NoneValue(None)

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

        raise ValueError("unknown operand type: {}".format(operand_string))

    def is_type(self, operand_type):
        return self.type == operand_type

    def parse_value(self, value):
        try:
            self.value = NumericValue(value)
            return
        except ValueError:
            pass

        if self.mnemonic == "FCC":
            try:
                self.value = StringValue(value)
                return
            except ValueError:
                pass

        try:
            self.value = SymbolValue(value)
            self.requires_resolution = True
            return
        except ValueError:
            pass

        try:
            self.value = ExpressionValue(value)
            self.requires_resolution = True
            return
        except ValueError:
            pass

        raise ValueError("cannot parse value: {}".format(value))

    def resolve_symbols(self, symbol_table):
        if not self.value.is_type(ValueType.SYMBOL):
            return

        symbol_label = self.value.ascii()
        if symbol_label not in symbol_table:
            raise ValueError("{} not in symbol table".format(symbol_label))

        symbol = symbol_table[symbol_label]
        if symbol.is_type(ValueType.ADDRESS):
            self.value = AddressValue(symbol.get_integer())
            self.type = OperandType.EXTENDED if self.type == OperandType.UNKNOWN else self.type
            return

        if symbol.is_type(ValueType.NUMERIC):
            self.value = copy(symbol)
            self.type = OperandType.DIRECT if self.value.hex_len() == 2 else OperandType.EXTENDED


class UnknownOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.operand_string = operand_string
        self.parse_value(operand_string)


class InherentOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.INHERENT
        if operand_string:
            raise ValueError("{} is not an inherent value".format(operand_string))


class ImmediateOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.IMMEDIATE
        self.operand_string = operand_string
        match = IMMEDIATE_REGEX.match(operand_string)
        if not match:
            raise ValueError("{} is not an immediate value".format(operand_string))
        self.parse_value(match.group("value"))


class DirectOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.DIRECT
        self.operand_string = operand_string
        match = DIRECT_REGEX.match(self.operand_string)
        if match:
            self.parse_value(match.group("value")[1:])
        else:
            self.parse_value(operand_string)
        if self.value is None or self.value.byte_len() != 1:
            raise ValueError("{} is not a direct value".format(operand_string))


class ExtendedOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.EXTENDED
        self.operand_string = operand_string
        match = EXTENDED_REGEX.match(self.operand_string)
        if match:
            self.parse_value(match.group("value")[1:])
        else:
            self.parse_value(operand_string)
        if self.value is None or self.value.byte_len() != 2:
            raise ValueError("{} is not an extended value".format(operand_string))


class ExtendedIndirectOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.EXTENDED_INDIRECT
        self.operand_string = operand_string
        match = EXTENDED_INDIRECT_REGEX.match(self.operand_string)
        if not match:
            raise ValueError("operand is not an extended indirect value")
        self.parse_value(match.group("value"))


class IndexedOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.INDEXED
        self.operand_string = operand_string
        if "," not in operand_string:
            raise ValueError("operand is not an indexed value")
        self.value = NoneValue(operand_string)


class ExpressionOperand(Operand):
    def __init__(self, operand_string, mnemonic):
        super().__init__(mnemonic)
        self.type = OperandType.EXPRESSION
        self.operand_string = operand_string
        self.value = ExpressionValue(operand_string)

# E N D   O F   F I L E #######################################################
