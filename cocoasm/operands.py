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

from cocoasm.values import NoneValue, ValueType, AddressValue, Value, NumericValue
from cocoasm.instruction import CodePackage

# C O N S T A N T S ###########################################################

# Pattern to recognize an immediate value
IMMEDIATE_REGEX = re.compile(
    r"^#(?P<value>.*)"
)

# Pattern to recognize a direct value
DIRECT_REGEX = re.compile(
    r"^<(?P<value>.*)"
)

# Pattern to recognize an extended value
EXTENDED_REGEX = re.compile(
    r"^<(?P<value>.*)"
)

# Pattern to recognize an indexed value
EXTENDED_INDIRECT_REGEX = re.compile(
    r"^\[(?P<value>.*)\]"
)

# Patten to recognize an expression
EXPRESSION_REGEX = re.compile(
    r"^(?P<left>[\d\w]+)(?P<operation>[+\-/*])(?P<right>[\d\w]+)$"
)

# C L A S S E S ###############################################################


class OperandType(Enum):
    """
    The OperandType enumeration stores what kind of operand we have parsed.
    """
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
    def __init__(self, mnemonic, value=None):
        self.type = OperandType.UNKNOWN
        self.operand_string = ""
        self.mnemonic = mnemonic
        self.requires_resolution = False
        self.value = value if value else NoneValue(None)
        self.left = NoneValue(None)
        self.right = NoneValue(None)
        self.operation = ""

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
        """
        Returns True if the type of this operand class is the type being compared.

        :param operand_type: the OperandType to check
        :return: True if the OperandType values match, False otherwise
        """
        return self.type == operand_type

    def resolve_symbols(self, symbol_table):
        if self.is_type(OperandType.EXPRESSION):
            return self.resolve_expression(symbol_table)

        if not self.value.is_type(ValueType.SYMBOL):
            return self

        symbol = self.get_symbol(self.value.ascii(), symbol_table)

        if symbol.is_type(ValueType.ADDRESS):
            self.value = AddressValue(symbol.int)
            if self.type == OperandType.UNKNOWN:
                return ExtendedOperand(self.operand_string, self.mnemonic, value=self.value)
            return self

        if symbol.is_type(ValueType.NUMERIC):
            self.value = copy(symbol)
            if self.value.hex_len() == 2:
                return DirectOperand(self.operand_string, self.mnemonic, value=self.value)
            return ExtendedOperand(self.operand_string, self.mnemonic, value=self.value)

    def resolve_expression(self, symbol_table):
        if self.left.is_type(ValueType.SYMBOL):
            self.left = self.get_symbol(self.left.ascii(), symbol_table)

        if self.right.is_type(ValueType.SYMBOL):
            self.right = self.get_symbol(self.right.ascii(), symbol_table)

        if self.right.is_type(ValueType.NUMERIC) and self.left.is_type(ValueType.NUMERIC):
            left = self.left.int
            right = self.right.int
            if self.operation == "+":
                self.value = NumericValue("{}".format(left + right))
            if self.operation == "-":
                self.value = NumericValue("{}".format(left - right))
            if self.operation == "*":
                self.value = NumericValue("{}".format(left * right))
            if self.operation == "/":
                self.value = NumericValue("{}".format(left / right))
            if self.value.hex_len() == 2:
                return DirectOperand(self.operand_string, self.mnemonic, value=self.value)
            return ExtendedOperand(self.operand_string, self.mnemonic, value=self.value)

        raise ValueError("[{}] unresolved expression".format(self.operand_string))

    @staticmethod
    def get_symbol(symbol_label, symbol_table):
        if symbol_label not in symbol_table:
            raise ValueError("[{}] not in symbol table".format(symbol_label))
        return symbol_table[symbol_label]

    @abstractmethod
    def translate(self, instruction):
        """
        Using information contained within the instruction, translate the operand,
        and return a code package containing the equivalent machine code information.

        :param instruction: the instruction associated with the operand
        :return: a CodePackage containing the translated instruction
        """


class UnknownOperand(Operand):
    def __init__(self, operand_string, mnemonic, value=None):
        super().__init__(mnemonic)
        self.operand_string = operand_string
        self.value = value if value else Value.create_from_str(operand_string, mnemonic)

    def translate(self, instruction):
        return CodePackage(additional=self.value)


class RelativeOperand(Operand):
    def __init__(self, operand_string, mnemonic, value=None):
        super().__init__(mnemonic)
        self.operand_string = operand_string
        self.value = value if value else Value.create_from_str(operand_string, mnemonic)

class InherentOperand(Operand):
    def __init__(self, operand_string, mnemonic, value=None):
        super().__init__(mnemonic)
        self.type = OperandType.INHERENT
        if value:
            raise ValueError("[{}] is not an inherent value".format(value.ascii()))
        if operand_string:
            raise ValueError("[{}] is not an inherent value".format(operand_string))

    def translate(self, instruction):
        if not instruction.mode.supports_inherent():
            raise ValueError("Instruction [{}] requires an operand".format(self.mnemonic))
        return CodePackage(op_code=NumericValue(instruction.mode.inh), size=instruction.mode.inh_sz)


class ImmediateOperand(Operand):
    def __init__(self, operand_string, mnemonic, value=None):
        super().__init__(mnemonic)
        self.type = OperandType.IMMEDIATE
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        match = IMMEDIATE_REGEX.match(operand_string)
        if not match:
            raise ValueError("[{}] is not an immediate value".format(operand_string))
        self.value = Value.create_from_str(match.group("value"), mnemonic)

    def translate(self, instruction):
        if not instruction.mode.supports_immediate():
            raise ValueError("Instruction [{}] does not support immediate addressing".format(self.mnemonic))
        return CodePackage(op_code=NumericValue(instruction.mode.imm),
                           additional=self.value,
                           size=instruction.mode.imm_sz)


class DirectOperand(Operand):
    def __init__(self, operand_string, mnemonic, value=None):
        super().__init__(mnemonic)
        self.type = OperandType.DIRECT
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        match = DIRECT_REGEX.match(self.operand_string)
        if match:
            self.value = Value.create_from_str(match.group("value")[1:], mnemonic)
        else:
            self.value = Value.create_from_str(operand_string, mnemonic)
        if self.value is None or self.value.byte_len() != 1:
            raise ValueError("[{}] is not a direct value".format(operand_string))

    def translate(self, instruction):
        if not instruction.mode.supports_direct():
            raise ValueError("Instruction [{}] does not support direct addressing".format(self.mnemonic))
        return CodePackage(op_code=NumericValue(instruction.mode.dir),
                           additional=self.value,
                           size=instruction.mode.dir_sz)


class ExtendedOperand(Operand):
    def __init__(self, operand_string, mnemonic, value=None):
        super().__init__(mnemonic)
        self.type = OperandType.EXTENDED
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        match = EXTENDED_REGEX.match(self.operand_string)
        if match:
            self.value = Value.create_from_str(match.group("value")[1:], mnemonic)
        else:
            self.value = Value.create_from_str(operand_string, mnemonic)
        if self.value is None or self.value.byte_len() != 2:
            raise ValueError("[{}] is not an extended value".format(operand_string))

    def translate(self, instruction):
        if not instruction.mode.supports_extended():
            raise ValueError("Instruction [{}] does not support extended addressing".format(self.mnemonic))
        return CodePackage(op_code=NumericValue(instruction.mode.ext),
                           additional=self.value,
                           size=instruction.mode.ext_sz)


class ExtendedIndirectOperand(Operand):
    def __init__(self, operand_string, mnemonic, value=None):
        super().__init__(mnemonic)
        self.type = OperandType.EXTENDED_INDIRECT
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        match = EXTENDED_INDIRECT_REGEX.match(self.operand_string)
        if not match:
            raise ValueError("[{}] is not an extended indirect value".format(operand_string))
        self.value = Value.create_from_str(match.group("value"), mnemonic)

    def translate(self, instruction):
        pass


class IndexedOperand(Operand):
    def __init__(self, operand_string, mnemonic, value=None):
        super().__init__(mnemonic)
        self.type = OperandType.INDEXED
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        if "," not in operand_string or mnemonic == "FCC":
            raise ValueError("[{}] is not an indexed value".format(operand_string))
        self.value = NoneValue(operand_string)

    def translate(self, instruction):
        if not instruction.mode.supports_indexed():
            raise ValueError("Instruction [{}] does not support indexed addressing".format(self.mnemonic))
        # TODO: properly translate what the post-byte code should be
        return CodePackage(op_code=NumericValue(instruction.mode.ind),
                           additional=self.value,
                           post_byte=NumericValue(0x9F),
                           size=instruction.mode.ind_sz)


class ExpressionOperand(Operand):
    def __init__(self, operand_string, mnemonic, value=None):
        super().__init__(mnemonic)
        self.type = OperandType.EXPRESSION
        self.operand_string = operand_string
        match = EXPRESSION_REGEX.match(operand_string)
        if not match:
            raise ValueError("[{}] is not a valid expression".format(operand_string))
        self.left = Value.create_from_str(match.group("left"), mnemonic)
        self.right = Value.create_from_str(match.group("right"), mnemonic)
        self.operation = match.group("operation")
        self.value = NoneValue("")

    def translate(self, instruction):
        return CodePackage()

# E N D   O F   F I L E #######################################################
