"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from abc import ABC, abstractmethod
from enum import Enum

from cocoasm.values import NoneValue, ValueType, Value, NumericValue
from cocoasm.instruction import CodePackage
from cocoasm.exceptions import OperandTypeError, ValueTypeError

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
    r"^>(?P<value>.*)"
)

# Pattern to recognize an indexed value
EXTENDED_INDIRECT_REGEX = re.compile(
    r"^\[(?P<value>.*)\]"
)

# Pattern to recognize invalid characters in an UnknownOperand
UNKNOWN_REGEX = re.compile(
    r","
)

# Recognized register names
REGISTERS = ["A", "B", "D", "X", "Y", "U", "S", "CC", "DP", "PC"]

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
    PSEUDO = 9
    SPECIAL = 10


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
            return PseudoOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return SpecialOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return RelativeOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return InherentOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return ImmediateOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return ExtendedIndexedOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return IndexedOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return UnknownOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        raise OperandTypeError("[{}] unknown operand type".format(operand_string))

    def is_type(self, operand_type):
        """
        Returns True if the type of this operand class is the type being compared.

        :param operand_type: the OperandType to check
        :return: True if the OperandType values match, False otherwise
        """
        return self.type == operand_type

    def resolve_symbols(self, symbol_table):
        """
        Given a symbol table, searches the operands for any symbols, and resolves
        them with values from the symbol table. Returns a (possibly) new Operand
        class type as a result of symbol resolution.

        :param symbol_table: the symbol table to search
        :return: self, or a new Operand class type with a resolved value
        """
        self.value = self.value.resolve(symbol_table)

        if self.value.is_type(ValueType.ADDRESS):
            if self.is_type(OperandType.UNKNOWN):
                return ExtendedOperand(self.operand_string, self.instruction, value=self.value)

        if self.value.is_type(ValueType.NUMERIC):
            if self.is_type(OperandType.UNKNOWN):
                operand = DirectOperand if self.value.hex_len() == 2 else ExtendedOperand
                return operand(self.operand_string, self.instruction, value=self.value)

        return self

    @abstractmethod
    def translate(self):
        """
        Using information contained within the instruction, translate the operand,
        and return a code package containing the equivalent machine code information.

        :return: a CodePackage containing the translated instruction
        """


class BadInstructionOperand(Operand):
    def __init__self(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.operand_string = operand_string
        self.original_operand = operand_string

    def translate(self):
        return CodePackage()


class UnknownOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        if UNKNOWN_REGEX.search(operand_string):
            raise OperandTypeError("[{}] invalid operand".format(operand_string))
        try:
            self.value = Value.create_from_str(operand_string, instruction)
        except ValueTypeError:
            self.value = NoneValue()

    def translate(self):
        return CodePackage(additional=self.value)


class PseudoOperand(Operand):
    def __init__(self, operand_string, instruction):
        super().__init__(instruction)
        self.operand_string = operand_string
        self.type = OperandType.PSEUDO
        if not instruction.is_pseudo:
            raise OperandTypeError("[{}] is not a pseudo instruction".format(instruction.mnemonic))
        self.value = NoneValue() if instruction.is_include else Value.create_from_str(operand_string, instruction)

    def resolve_symbols(self, symbol_table):
        return self

    def translate(self):
        if self.instruction.mnemonic == "FCB":
            return CodePackage(additional=self.value, size=1)

        if self.instruction.mnemonic == "FDB":
            return CodePackage(additional=NumericValue(self.value.int, size_hint=4), size=2)

        if self.instruction.mnemonic == "RMB":
            return CodePackage(additional=NumericValue(0, size_hint=self.value.int*2), size=self.value.int)

        if self.instruction.mnemonic == "ORG":
            return CodePackage(address=self.value)

        if self.instruction.mnemonic == "FCC":
            return CodePackage(additional=self.value, size=self.value.byte_len())

        return CodePackage()


class SpecialOperand(Operand):
    def __init__(self, operand_string, instruction):
        super().__init__(instruction)
        self.operand_string = operand_string
        self.type = OperandType.SPECIAL
        if not instruction.is_special:
            raise OperandTypeError("[{}] is not a special instruction".format(instruction.mnemonic))

    def resolve_symbols(self, symbol_table):
        return self

    def translate(self):
        code_pkg = CodePackage()
        code_pkg.op_code = NumericValue(self.instruction.mode.imm)
        code_pkg.size = self.instruction.mode.imm_sz
        code_pkg.post_byte = 0x00

        if self.instruction.mnemonic == "PSHS" or self.instruction.mnemonic == "PULS":
            if not self.operand_string:
                raise OperandTypeError("one or more registers must be specified")

            registers = self.operand_string.split(",")
            for register in registers:
                if register not in REGISTERS:
                    raise OperandTypeError("[{}] unknown register".format(register))

                code_pkg.post_byte |= 0x06 if register == "D" else 0x00
                code_pkg.post_byte |= 0x01 if register == "CC" else 0x00
                code_pkg.post_byte |= 0x02 if register == "A" else 0x00
                code_pkg.post_byte |= 0x04 if register == "B" else 0x00
                code_pkg.post_byte |= 0x08 if register == "DP" else 0x00
                code_pkg.post_byte |= 0x10 if register == "X" else 0x00
                code_pkg.post_byte |= 0x20 if register == "Y" else 0x00
                code_pkg.post_byte |= 0x40 if register == "U" else 0x00
                code_pkg.post_byte |= 0x80 if register == "PC" else 0x00

        if self.instruction.mnemonic == "EXG" or self.instruction.mnemonic == "TFR":
            registers = self.operand_string.split(",")
            if len(registers) != 2:
                raise OperandTypeError("[{}] requires exactly 2 registers".format(self.instruction.mnemonic))

            if registers[0] not in REGISTERS:
                raise OperandTypeError("[{}] unknown register".format(registers[0]))

            if registers[1] not in REGISTERS:
                raise OperandTypeError("[{}] unknown register".format(registers[1]))

            code_pkg.post_byte |= 0x00 if registers[0] == "D" else 0x00
            code_pkg.post_byte |= 0x00 if registers[1] == "D" else 0x00

            code_pkg.post_byte |= 0x10 if registers[0] == "X" else 0x00
            code_pkg.post_byte |= 0x01 if registers[1] == "X" else 0x00

            code_pkg.post_byte |= 0x20 if registers[0] == "Y" else 0x00
            code_pkg.post_byte |= 0x02 if registers[1] == "Y" else 0x00

            code_pkg.post_byte |= 0x30 if registers[0] == "U" else 0x00
            code_pkg.post_byte |= 0x03 if registers[1] == "U" else 0x00

            code_pkg.post_byte |= 0x40 if registers[0] == "S" else 0x00
            code_pkg.post_byte |= 0x04 if registers[1] == "S" else 0x00

            code_pkg.post_byte |= 0x50 if registers[0] == "PC" else 0x00
            code_pkg.post_byte |= 0x05 if registers[1] == "PC" else 0x00

            code_pkg.post_byte |= 0x80 if registers[0] == "A" else 0x00
            code_pkg.post_byte |= 0x08 if registers[1] == "A" else 0x00

            code_pkg.post_byte |= 0x90 if registers[0] == "B" else 0x00
            code_pkg.post_byte |= 0x09 if registers[1] == "B" else 0x00

            code_pkg.post_byte |= 0xA0 if registers[0] == "CC" else 0x00
            code_pkg.post_byte |= 0x0A if registers[1] == "CC" else 0x00

            code_pkg.post_byte |= 0xB0 if registers[0] == "DP" else 0x00
            code_pkg.post_byte |= 0x0B if registers[1] == "DP" else 0x00

            if code_pkg.post_byte not in \
                    [
                        0x01, 0x10, 0x02, 0x20, 0x03, 0x30, 0x04, 0x40,
                        0x05, 0x50, 0x12, 0x21, 0x13, 0x31, 0x14, 0x41,
                        0x15, 0x51, 0x23, 0x32, 0x24, 0x42, 0x25, 0x52,
                        0x34, 0x43, 0x35, 0x53, 0x45, 0x54, 0x89, 0x98,
                        0x8A, 0xA8, 0x8B, 0xB8, 0x9A, 0xA9, 0x9B, 0xB9,
                        0xAB, 0xBA, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55,
                        0x88, 0x99, 0xAA, 0xBB
                    ]:
                raise OperandTypeError(
                    "[{}] of [{}] to [{}] not allowed".format(self.instruction.mnemonic, registers[0], registers[1]))

        code_pkg.post_byte = NumericValue(code_pkg.post_byte)
        return code_pkg


class RelativeOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.RELATIVE
        if not instruction.is_short_branch and not instruction.is_long_branch:
            raise OperandTypeError("[{}] is not a branch instruction".format(instruction.mnemonic))
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
            raise OperandTypeError("[{}] is not an inherent value".format(value.ascii()))
        if operand_string:
            raise OperandTypeError("[{}] is not an inherent value".format(operand_string))

    def translate(self):
        if not self.instruction.mode.inh:
            raise OperandTypeError("Instruction [{}] requires an operand".format(self.instruction.mnemonic))
        return CodePackage(op_code=NumericValue(self.instruction.mode.inh), size=self.instruction.mode.inh_sz)


class ImmediateOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.IMMEDIATE
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        match = IMMEDIATE_REGEX.match(self.operand_string)
        if not match:
            raise OperandTypeError("[{}] is not an immediate value".format(operand_string))
        self.value = Value.create_from_str(match.group("value"), instruction)

    def translate(self):
        if not self.instruction.mode.imm:
            raise OperandTypeError("Instruction [{}] does not support immediate addressing".format(self.instruction.mnemonic))
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
            self.value = Value.create_from_str(match.group("value"), instruction)
        else:
            self.value = Value.create_from_str(operand_string, instruction)

        # If we have a numeric, we can run a check here for direct value size
        if self.value.is_type(ValueType.NUMERIC) and self.value.byte_len() != 1:
            raise OperandTypeError("[{}] is not a direct value".format(self.operand_string))

    def translate(self):
        if not self.instruction.mode.dir:
            raise OperandTypeError("Instruction [{}] does not support direct addressing".format(self.instruction.mnemonic))
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
            self.value = Value.create_from_str(match.group("value"), instruction)
        else:
            self.value = Value.create_from_str(operand_string, instruction)

    def translate(self):
        if not self.instruction.mode.ext:
            raise OperandTypeError("Instruction [{}] does not support extended addressing".format(self.instruction.mnemonic))
        return CodePackage(op_code=NumericValue(self.instruction.mode.ext),
                           additional=self.value,
                           size=self.instruction.mode.ext_sz)


class ExtendedIndexedOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.EXTENDED_INDIRECT
        self.operand_string = operand_string
        self.left = None
        self.right = None
        if value is not None:
            self.value = value
            return
        match = EXTENDED_INDIRECT_REGEX.match(self.operand_string)
        if not match:
            raise OperandTypeError("[{}] is not an extended indexed value".format(operand_string))
        parsed_value = match.group("value")
        if "," not in parsed_value:
            self.value = Value.create_from_str(parsed_value, self.instruction)
        elif len(parsed_value.split(",")) == 2:
            self.left, self.right = parsed_value.split(",")
        else:
            raise OperandTypeError("[{}] incorrect number of commas in extended indexed value".format(operand_string))

    def resolve_symbols(self, symbol_table):
        if not self.value.is_type(ValueType.NONE):
            self.value = self.value.resolve(symbol_table)
            return self

        if self.left and self.left != "":
            if self.left != "A" and self.left != "B" and self.left != "D":
                self.left = Value.create_from_str(self.left, self.instruction)
                if self.left.is_type(ValueType.SYMBOL):
                    self.left = self.left.resolve(symbol_table)
        return self

    def translate(self):
        if not self.instruction.mode.ind:
            raise OperandTypeError("Instruction [{}] does not support indexed addressing".format(self.instruction.mnemonic))
        size = self.instruction.mode.ind_sz

        if not type(self.value) == str and self.value.is_type(ValueType.ADDRESS):
            size += 2
            return CodePackage(
                op_code=NumericValue(self.instruction.mode.ind),
                post_byte=NumericValue(0x9F),
                additional=self.value,
                size=size)

        if not type(self.value) == str and self.value.is_type(ValueType.NUMERIC):
            size += 2
            return CodePackage(
                op_code=NumericValue(self.instruction.mode.ind),
                post_byte=NumericValue(0x9F),
                additional=self.value,
                size=size)

        raw_post_byte = 0x80
        additional = NoneValue()
        additional_needs_resolution = False

        if "X" in self.right:
            raw_post_byte |= 0x00
        if "Y" in self.right:
            raw_post_byte |= 0x20
        if "U" in self.right:
            raw_post_byte |= 0x40
        if "S" in self.right:
            raw_post_byte |= 0x60

        if self.left == "":
            if "-" in self.right or "+" in self.right:
                if self.right == "X+" or self.right == "Y+" or self.right == "U+" or self.right == "S+":
                    raise OperandTypeError("[{}] not allowed as an extended indirect value".format(self.right))
                if self.right == "-X" or self.right == "-Y" or self.right == "-U" or self.right == "-S":
                    raise OperandTypeError("[{}] not allowed as an extended indirect value".format(self.right))
                if "++" in self.right:
                    raw_post_byte |= 0x11
                if "--" in self.right:
                    raw_post_byte |= 0x13
            else:
                raw_post_byte |= 0x14

        elif self.left == "A" or self.left == "B" or self.left == "D":
            if self.left == "A":
                raw_post_byte |= 0x16
            if self.left == "B":
                raw_post_byte |= 0x15
            if self.left == "D":
                raw_post_byte |= 0x1B

        else:
            if "+" in self.right or "-" in self.right:
                raise OperandTypeError("[{}] invalid indexed expression".format(self.operand_string))
            if type(self.left) == str:
                self.left = NumericValue(self.left)
            if self.left.is_type(ValueType.ADDRESS):
                additional_needs_resolution = True
                self.left = NumericValue(self.left.int)
            additional = self.left

            if "PCR" in self.right:
                # TODO: all address symbols resolve to 16-bit offsets, need to find a way to calculate 8-bit offsets
                if additional_needs_resolution:
                    size += 2
                    raw_post_byte |= 0x9D
                else:
                    size += additional.byte_len()
                    raw_post_byte |= 0x9D if additional.byte_len() == 2 else 0x9C
            else:
                size += additional.byte_len()
                raw_post_byte |= 0x99 if additional.byte_len() == 2 else 0x98

        return CodePackage(op_code=NumericValue(self.instruction.mode.ind),
                           post_byte=NumericValue(raw_post_byte),
                           additional=additional,
                           size=size,
                           additional_needs_resolution=additional_needs_resolution)


class IndexedOperand(Operand):
    def __init__(self, operand_string, instruction):
        super().__init__(instruction)
        self.type = OperandType.INDEXED
        self.operand_string = operand_string
        self.right = ""
        self.left = ""
        if "," not in operand_string or instruction.is_string_define:
            raise OperandTypeError("[{}] is not an indexed value".format(operand_string))
        if len(operand_string.split(",")) != 2:
            raise OperandTypeError("[{}] incorrect number of commas in indexed value".format(operand_string))
        self.left, self.right = operand_string.split(",")

    def resolve_symbols(self, symbol_table):
        if self.left != "":
            if self.left != "A" and self.left != "B" and self.left != "D":
                self.left = Value.create_from_str(self.left, self.instruction)
                if self.left.is_type(ValueType.SYMBOL):
                    self.left = self.left.resolve(symbol_table)
        return self

    def translate(self):
        if not self.instruction.mode.ind:
            raise OperandTypeError("Instruction [{}] does not support indexed addressing".format(self.instruction.mnemonic))
        raw_post_byte = 0x00
        size = self.instruction.mode.ind_sz
        additional = NoneValue()
        additional_needs_resolution = False

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
                raise OperandTypeError("[{}] invalid indexed expression".format(self.operand_string))
            if type(self.left) == str:
                self.left = NumericValue(self.left)
            if self.left.is_type(ValueType.ADDRESS):
                additional_needs_resolution = True
                self.left = NumericValue(self.left.int)

            additional = self.left

            if "PCR" in self.right:
                # TODO: all address symbols resolve to 16-bit offsets, need to find a way to calculate 8-bit offsets
                if additional_needs_resolution:
                    size += 2
                    raw_post_byte |= 0x8D
                else:
                    size += additional.byte_len()
                    raw_post_byte |= 0x8D if additional.byte_len() == 2 else 0x8C
            else:
                if additional.int <= 0x1F:
                    raw_post_byte |= additional.int
                else:
                    size += additional.byte_len()
                    raw_post_byte |= 0x89 if additional.byte_len() == 2 else 0x88

        return CodePackage(op_code=NumericValue(self.instruction.mode.ind),
                           post_byte=NumericValue(raw_post_byte),
                           additional=additional,
                           size=size,
                           additional_needs_resolution=additional_needs_resolution)


# E N D   O F   F I L E #######################################################
