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
    def __init__(self, instruction, value=None):
        self.type = OperandType.UNKNOWN
        self.operand_string = ""
        self.instruction = instruction
        self.requires_resolution = False
        self.value = value if value else NoneValue(None)
        self.left = NoneValue(None)
        self.right = NoneValue(None)
        self.operation = ""

    @classmethod
    def create_from_str(cls, operand_string, instruction):
        try:
            return RelativeOperand(operand_string, instruction)
        except ValueError:
            pass

        try:
            return InherentOperand(operand_string, instruction)
        except ValueError:
            pass

        try:
            return ImmediateOperand(operand_string, instruction)
        except ValueError:
            pass

        try:
            return DirectOperand(operand_string, instruction)
        except ValueError:
            pass

        try:
            return ExtendedOperand(operand_string, instruction)
        except ValueError:
            pass

        try:
            return ExtendedIndexedOperand(operand_string, instruction)
        except ValueError:
            pass

        try:
            return IndexedOperand(operand_string, instruction)
        except ValueError:
            pass

        try:
            return ExpressionOperand(operand_string, instruction)
        except ValueError:
            pass

        try:
            return UnknownOperand(operand_string, instruction)
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
                return ExtendedOperand(self.operand_string, self.instruction, value=self.value)
            return self

        if symbol.is_type(ValueType.NUMERIC):
            self.value = copy(symbol)
            if self.value.hex_len() == 2:
                return DirectOperand(self.operand_string, self.instruction, value=self.value)
            return ExtendedOperand(self.operand_string, self.instruction, value=self.value)

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
                return DirectOperand(self.operand_string, self.instruction, value=self.value)
            return ExtendedOperand(self.operand_string, self.instruction, value=self.value)

        raise ValueError("[{}] unresolved expression".format(self.operand_string))

    @staticmethod
    def get_symbol(symbol_label, symbol_table):
        if symbol_label not in symbol_table:
            raise ValueError("[{}] not in symbol table".format(symbol_label))
        return symbol_table[symbol_label]

    @abstractmethod
    def translate(self):
        """
        Using information contained within the instruction, translate the operand,
        and return a code package containing the equivalent machine code information.

        :return: a CodePackage containing the translated instruction
        """


class UnknownOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.operand_string = operand_string
        self.value = value if value else Value.create_from_str(operand_string, instruction)

    def translate(self):
        return CodePackage(additional=self.value)


class RelativeOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.RELATIVE
        if not instruction.is_short_branch and not instruction.is_long_branch:
            raise ValueError("[{}] is not a branch instruction".format(instruction.mnemonic))
        self.operand_string = operand_string
        self.value = value if value else Value.create_from_str(operand_string, instruction)

    def translate(self):
        code_pkg = CodePackage()
        code_pkg.op_code = NumericValue(self.instruction.mode.rel)
        if self.value.is_type(ValueType.ADDRESS):
            code_pkg.additional = self.value
        code_pkg.size = self.instruction.mode.rel_sz
        return code_pkg


class InherentOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.INHERENT
        if value:
            raise ValueError("[{}] is not an inherent value".format(value.ascii()))
        if operand_string:
            raise ValueError("[{}] is not an inherent value".format(operand_string))

    def translate(self):
        if not self.instruction.mode.supports_inherent():
            raise ValueError("Instruction [{}] requires an operand".format(self.instruction.mnemonic))
        return CodePackage(op_code=NumericValue(self.instruction.mode.inh), size=self.instruction.mode.inh_sz)


class ImmediateOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.IMMEDIATE
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        match = IMMEDIATE_REGEX.match(operand_string)
        if not match:
            raise ValueError("[{}] is not an immediate value".format(operand_string))
        self.value = Value.create_from_str(match.group("value"), instruction)

    def translate(self):
        if not self.instruction.mode.supports_immediate():
            raise ValueError("Instruction [{}] does not support immediate addressing".format(self.instruction.mnemonic))
        return CodePackage(op_code=NumericValue(self.instruction.mode.imm),
                           additional=self.value,
                           size=self.instruction.mode.imm_sz)


class DirectOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.DIRECT
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        match = DIRECT_REGEX.match(self.operand_string)
        if match:
            self.value = Value.create_from_str(match.group("value")[1:], instruction)
        else:
            self.value = Value.create_from_str(operand_string, instruction)
        if self.value is None or self.value.byte_len() != 1:
            raise ValueError("[{}] is not a direct value".format(operand_string))

    def translate(self):
        if not self.instruction.mode.supports_direct():
            raise ValueError("Instruction [{}] does not support direct addressing".format(self.instruction.mnemonic))
        return CodePackage(op_code=NumericValue(self.instruction.mode.dir),
                           additional=self.value,
                           size=self.instruction.mode.dir_sz)


class ExtendedOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.EXTENDED
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        match = EXTENDED_REGEX.match(self.operand_string)
        if match:
            self.value = Value.create_from_str(match.group("value")[1:], instruction)
        else:
            self.value = Value.create_from_str(operand_string, instruction)
        if self.value is None or self.value.byte_len() != 2:
            raise ValueError("[{}] is not an extended value".format(operand_string))

    def translate(self):
        if not self.instruction.mode.supports_extended():
            raise ValueError("Instruction [{}] does not support extended addressing".format(self.instruction.mnemonic))
        return CodePackage(op_code=NumericValue(self.instruction.mode.ext),
                           additional=self.value,
                           size=self.instruction.mode.ext_sz)


class ExtendedIndexedOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.EXTENDED_INDIRECT
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        match = EXTENDED_INDIRECT_REGEX.match(self.operand_string)
        if not match:
            raise ValueError("[{}] is not an extended indexed value".format(operand_string))
        self.value = Value.create_from_str(match.group("value"), instruction)

    def translate(self):
        pass


class IndexedOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.INDEXED
        self.operand_string = operand_string
        self.right = ""
        self.left = ""
        if "," not in operand_string or instruction.is_string_define:
            raise ValueError("[{}] is not an indexed value".format(operand_string))
        if len(operand_string.split(",")) != 2:
            raise ValueError("[{}] incorrect number of commas in indexed value".format(operand_string))
        self.left, self.right = operand_string.split(",")

    def resolve_symbols(self, symbol_table):
        if self.left != "":
            if self.left != "A" and self.left != "B" and self.left != "D":
                self.left = Value.create_from_str(self.left, self.instruction)
                if self.left.is_type(ValueType.SYMBOL):
                    self.left = self.get_symbol(self.left.ascii(), symbol_table)
        return self

    def translate(self):
        if not self.instruction.mode.supports_indexed():
            raise ValueError("Instruction [{}] does not support indexed addressing".format(self.instruction.mnemonic))
        raw_post_byte = 0x00
        additional = NoneValue()

        # Determine register (if any)
        if "X" in self.right:
            raw_post_byte |= 0x00
        if "Y" in self.right:
            raw_post_byte |= 0x20
        if "U" in self.right:
            raw_post_byte |= 0x40
        if "S" in self.right:
            raw_post_byte |= 0x60

        if self.left == "":
            raw_post_byte |= 0x80
            if "-" in self.right or "+" in self.right:
                if "+" in self.right:
                    raw_post_byte |= 0x00
                if "++" in self.right:
                    raw_post_byte |= 0x01
                if "-" in self.right:
                    raw_post_byte |= 0x02
                if "--" in self.right:
                    raw_post_byte |= 0x03
            else:
                raw_post_byte |= 0x04

        elif self.left == "A" or self.left == "B" or self.left == "D":
            raw_post_byte |= 0x80
            if self.left == "A":
                raw_post_byte |= 0x06
            if self.left == "B":
                raw_post_byte |= 0x05
            if self.left == "D":
                raw_post_byte |= 0x0B

        else:
            if "+" in self.right or "-" in self.right:
                raise ValueError("[{}] invalid indexed expression".format(self.operand_string))
            if type(self.left) == str:
                self.left = NumericValue(self.left)
            if self.left.is_type(ValueType.ADDRESS):
                raise ValueError("[{}] cannot translate address in left hand side".format(self.operand_string))
            numeric = self.left
            if numeric.byte_len() == 2:
                if "PC" in self.right:
                    raw_post_byte |= 0x8D
                    additional = numeric
                else:
                    raw_post_byte |= 0x89
                    additional = numeric
            elif numeric.byte_len() == 1:
                if "PC" in self.right:
                    raw_post_byte |= 0x8C
                    additional = numeric
                else:
                    if numeric.int <= 0x1F:
                        raw_post_byte |= numeric.int
                    else:
                        raw_post_byte |= 0x88
                        additional = numeric

        return CodePackage(op_code=NumericValue(self.instruction.mode.ind),
                           post_byte=NumericValue(raw_post_byte),
                           additional=additional,
                           size=self.instruction.mode.ind_sz)


class ExpressionOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.EXPRESSION
        self.operand_string = operand_string
        match = EXPRESSION_REGEX.match(operand_string)
        if not match:
            raise ValueError("[{}] is not a valid expression".format(operand_string))
        self.left = Value.create_from_str(match.group("left"), instruction)
        self.right = Value.create_from_str(match.group("right"), instruction)
        self.operation = match.group("operation")
        self.value = NoneValue("")

    def translate(self):
        return CodePackage()

# E N D   O F   F I L E #######################################################
