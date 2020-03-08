"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from abc import ABC, abstractmethod
from enum import Enum

from cocoasm.values import StringValue, NumericValue

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
    VALUE = 10
    ADDRESS = 11
    STATEMENT_INDEX = 12


class Operand(ABC):
    def __init__(self):
        self.type = OperandType.UNKNOWN
        self.operand_string = None
        self.requires_resolution = False
        self.sub_expression = None

    @classmethod
    def create_from_operand(cls, operand_string):
        try:
            return InherentOperand(operand_string)
        except ValueError:
            pass

        try:
            return ImmediateOperand(operand_string)
        except ValueError:
            pass

    @abstractmethod
    def parse_operand(self, operand):
        pass

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

        try:
            self.sub_expression = StringValue(value)
            return
        except ValueError:
            pass

        self.requires_resolution = True

    def requires_resolution(self):
        return self.requires_resolution


class ExpressionOperand(Operand):
    pass


class InherentOperand(Operand):
    def __init__(self, operand_string):
        super().__init__()
        self.type = OperandType.INHERENT
        self.parse_operand(operand_string)

    def parse_operand(self, operand_string):
        if operand_string:
            raise ValueError("inherent operands do not have values")


class ImmediateOperand(Operand):
    def __init__(self, operand_string):
        super().__init__()
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
        match = IMM_REGEX.match(self.operand_string)
        if not match:
            raise ValueError("operand is not an immediate value")
        self.parsed_value = match.group("value")
        self.parse_sub_expression()


class DirectOperand(Operand):
    pass


class ExtendedOperand(Operand):
    pass

# E N D   O F   F I L E #######################################################
