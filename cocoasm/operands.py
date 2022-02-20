"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from abc import ABC, abstractmethod

from cocoasm.values import NoneValue, Value, NumericValue, DirectNumericValue, ExtendedNumericValue
from cocoasm.instruction import CodePackage
from cocoasm.operand_type import OperandType
from cocoasm.exceptions import OperandTypeError, ValueTypeError

# C O N S T A N T S ###########################################################

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
            return ExtendedIndexedOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return IndexedOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return ImmediateOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        try:
            return UnknownOperand(operand_string, instruction)
        except OperandTypeError:
            pass

        raise OperandTypeError("[{}] unknown operand type".format(operand_string))

    def is_unknown(self):
        return self.type == OperandType.UNKNOWN

    def is_relative(self):
        return self.type == OperandType.RELATIVE

    def is_pseudo(self):
        return self.type == OperandType.PSEUDO

    def is_special(self):
        return self.type == OperandType.SPECIAL

    def is_immediate(self):
        return self.type == OperandType.IMMEDIATE

    def is_inherent(self):
        return self.type == OperandType.INHERENT

    def is_extended(self):
        return self.type == OperandType.EXTENDED

    def is_direct(self):
        return self.type == OperandType.DIRECT

    def is_indexed(self):
        return self.type == OperandType.INDEXED

    def is_extended_indexed(self):
        return self.type == OperandType.EXTENDED_INDIRECT

    def resolve_symbols(self, symbol_table):
        """
        Given a symbol table, searches the operands for any symbols, and resolves
        them with values from the symbol table. Returns a (possibly) new Operand
        class type as a result of symbol resolution.

        :param symbol_table: the symbol table to search
        :return: self, or a new Operand class type with a resolved value
        """
        old_value = self.value
        self.value = self.value.resolve(symbol_table)

        if not self.is_unknown():
            return self

        if self.value.is_numeric() and (self.value.is_direct() or old_value.is_explicit_direct()):
            return DirectOperand(self.operand_string, self.instruction, DirectNumericValue(self.value.int))

        return ExtendedOperand(self.operand_string, self.instruction, value=self.value)

    @abstractmethod
    def translate(self):
        """
        Using information contained within the instruction, translate the operand,
        and return a code package containing the equivalent machine code information.

        :return: a CodePackage containing the translated instruction
        """


class BadInstructionOperand(Operand):
    def __init__(self, operand_string, instruction):
        super().__init__(operand_string, instruction)
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
        try:
            self.value = Value.create_from_str(operand_string, instruction)
        except ValueTypeError:
            raise OperandTypeError("[{}] unknown operand type".format(operand_string))

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
        if instruction.is_pseudo_define:
            if self.operand_string.startswith("$") and len(self.operand_string) > 3:
                self.value = ExtendedNumericValue(self.value.int)
            elif self.value.hex_len() == 2:
                self.value = DirectNumericValue(self.value.int)

    def resolve_symbols(self, symbol_table):
        return self

    def translate(self):
        if self.instruction.mnemonic == "FCB":
            return CodePackage(additional=NumericValue(self.value.int, size_hint=2), size=1, max_size=1)

        if self.instruction.mnemonic == "FDB":
            return CodePackage(additional=NumericValue(self.value.int, size_hint=4), size=2, max_size=2)

        if self.instruction.mnemonic == "RMB":
            return CodePackage(
                additional=NumericValue(0, size_hint=self.value.int*2),
                size=self.value.int,
                max_size=self.value.int,
            )

        if self.instruction.mnemonic == "ORG":
            return CodePackage(address=self.value)

        if self.instruction.mnemonic == "FCC":
            return CodePackage(additional=self.value, size=self.value.byte_len(), max_size=self.value.byte_len())

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
        post_byte = 0x00

        if self.instruction.mnemonic == "PSHS" or self.instruction.mnemonic == "PULS":
            if not self.operand_string:
                raise OperandTypeError("one or more registers must be specified")

            registers = self.operand_string.split(",")
            for register in registers:
                if register not in REGISTERS:
                    raise OperandTypeError("[{}] unknown register".format(register))

                post_byte |= 0x06 if register == "D" else 0x00
                post_byte |= 0x01 if register == "CC" else 0x00
                post_byte |= 0x02 if register == "A" else 0x00
                post_byte |= 0x04 if register == "B" else 0x00
                post_byte |= 0x08 if register == "DP" else 0x00
                post_byte |= 0x10 if register == "X" else 0x00
                post_byte |= 0x20 if register == "Y" else 0x00
                post_byte |= 0x40 if register == "U" else 0x00
                post_byte |= 0x80 if register == "PC" else 0x00

        if self.instruction.mnemonic == "EXG" or self.instruction.mnemonic == "TFR":
            registers = self.operand_string.split(",")
            if len(registers) != 2:
                raise OperandTypeError("[{}] requires exactly 2 registers".format(self.instruction.mnemonic))

            if registers[0] not in REGISTERS:
                raise OperandTypeError("[{}] unknown register".format(registers[0]))

            if registers[1] not in REGISTERS:
                raise OperandTypeError("[{}] unknown register".format(registers[1]))

            post_byte |= 0x00 if registers[0] == "D" else 0x00
            post_byte |= 0x00 if registers[1] == "D" else 0x00

            post_byte |= 0x10 if registers[0] == "X" else 0x00
            post_byte |= 0x01 if registers[1] == "X" else 0x00

            post_byte |= 0x20 if registers[0] == "Y" else 0x00
            post_byte |= 0x02 if registers[1] == "Y" else 0x00

            post_byte |= 0x30 if registers[0] == "U" else 0x00
            post_byte |= 0x03 if registers[1] == "U" else 0x00

            post_byte |= 0x40 if registers[0] == "S" else 0x00
            post_byte |= 0x04 if registers[1] == "S" else 0x00

            post_byte |= 0x50 if registers[0] == "PC" else 0x00
            post_byte |= 0x05 if registers[1] == "PC" else 0x00

            post_byte |= 0x80 if registers[0] == "A" else 0x00
            post_byte |= 0x08 if registers[1] == "A" else 0x00

            post_byte |= 0x90 if registers[0] == "B" else 0x00
            post_byte |= 0x09 if registers[1] == "B" else 0x00

            post_byte |= 0xA0 if registers[0] == "CC" else 0x00
            post_byte |= 0x0A if registers[1] == "CC" else 0x00

            post_byte |= 0xB0 if registers[0] == "DP" else 0x00
            post_byte |= 0x0B if registers[1] == "DP" else 0x00

            if post_byte not in \
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

        return CodePackage(
            op_code=NumericValue(self.instruction.mode.imm),
            post_byte=NumericValue(post_byte),
            size=self.instruction.mode.imm_sz,
            max_size=self.instruction.mode.imm_sz,
        )


class RelativeOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.RELATIVE
        if not instruction.is_short_branch and not instruction.is_long_branch:
            raise OperandTypeError("[{}] is not a branch instruction".format(instruction.mnemonic))
        self.operand_string = operand_string
        self.value = value if value else Value.create_from_str(operand_string, instruction)

    def translate(self):
        return CodePackage(
            op_code=NumericValue(self.instruction.mode.rel),
            additional=self.value if self.value.is_address() else NoneValue(),
            size=self.instruction.mode.rel_sz,
            max_size=self.instruction.mode.rel_sz,
        )


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
        return CodePackage(
            op_code=NumericValue(self.instruction.mode.inh),
            size=self.instruction.mode.inh_sz,
            max_size=self.instruction.mode.inh_sz,
        )


class ImmediateOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.IMMEDIATE
        self.operand_string = operand_string
        if value:
            self.value = value
            return
        try:
            self.value = Value.create_from_str(self.operand_string, instruction)
        except ValueTypeError:
            raise OperandTypeError("[{}] is not an immediate value".format(operand_string))
        if not self.value.is_immediate():
            raise OperandTypeError("[{}] is not an immediate value".format(operand_string))

    def translate(self):
        if not self.instruction.mode.imm:
            raise OperandTypeError(
                "Instruction [{}] does not support immediate addressing".format(self.instruction.mnemonic)
            )
        return CodePackage(
            op_code=NumericValue(self.instruction.mode.imm),
            additional=self.value,
            size=self.instruction.mode.imm_sz,
            max_size=self.instruction.mode.imm_sz,
        )


class DirectOperand(Operand):
    def __init__(self, operand_string, instruction, value=None):
        super().__init__(instruction)
        self.type = OperandType.DIRECT
        self.operand_string = operand_string
        if value:
            self.value = value
            return

        self.value = Value.create_from_str(operand_string, instruction)
        if not self.value.is_direct() and not self.value.is_explicit_direct():
            raise OperandTypeError("[{}] is not a direct value".format(self.operand_string))

    def translate(self):
        if not self.instruction.mode.dir:
            raise OperandTypeError(
                "Instruction [{}] does not support direct addressing".format(self.instruction.mnemonic)
            )
        return CodePackage(
            op_code=NumericValue(self.instruction.mode.dir),
            additional=self.value,
            size=self.instruction.mode.dir_sz,
            max_size=self.instruction.mode.dir_sz,
        )


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
            raise OperandTypeError(
                "Instruction [{}] does not support extended addressing".format(self.instruction.mnemonic)
            )
        return CodePackage(
            op_code=NumericValue(self.instruction.mode.ext),
            additional=self.value,
            size=self.instruction.mode.ext_sz,
            max_size=self.instruction.mode.ext_sz,
        )


class ExtendedIndexedOperand(Operand):
    def __init__(self, operand_string, instruction):
        super().__init__(instruction)
        self.type = OperandType.EXTENDED_INDIRECT
        self.operand_string = operand_string
        if not (self.operand_string.startswith("[") and self.operand_string.endswith("]")):
            raise OperandTypeError("[{}] is not an extended indexed value".format(operand_string))
        try:
            stripped_operand_string = operand_string[1:-1]
            self.value = Value.create_from_str(stripped_operand_string, self.instruction)
        except ValueTypeError:
            raise OperandTypeError("[{}] is not an extended indexed value".format(operand_string))
        if self.value.is_leftright():
            self.left = self.value.left
            self.right = self.value.right

    def resolve_symbols(self, symbol_table):
        if not self.value.is_none() and not self.value.is_leftright():
            self.value = self.value.resolve(symbol_table)
            return self

        if self.left and self.left != "":
            if self.left != "A" and self.left != "B" and self.left != "D":
                self.left = Value.create_from_str(self.left, self.instruction, default_mode_extended=False)
                if self.left.is_symbol():
                    self.left = self.left.resolve(symbol_table)
                if self.left.is_address_expression() or self.left.is_expression():
                    self.left = self.left.resolve(symbol_table)
        return self

    def translate(self):
        if not self.instruction.mode.ind:
            raise OperandTypeError(
                "Instruction [{}] does not support indexed addressing".format(self.instruction.mnemonic)
            )
        size = self.instruction.mode.ind_sz

        if not type(self.value) == str and self.value.is_address():
            size += 2
            return CodePackage(
                op_code=NumericValue(self.instruction.mode.ind),
                post_byte=NumericValue(0x9F),
                additional=self.value,
                size=size,
                max_size=size,
            )

        if not type(self.value) == str and self.value.is_numeric():
            size += 2
            return CodePackage(
                op_code=NumericValue(self.instruction.mode.ind),
                post_byte=NumericValue(0x9F),
                additional=self.value,
                size=size,
                max_size=size,
            )

        raw_post_byte = 0x80
        post_byte_choices = []
        size = self.instruction.mode.ind_sz
        max_size = size
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
                self.left = Value.create_from_str(self.left)

            if self.left.is_address():
                additional_needs_resolution = True
                self.left = NumericValue(self.left.int)

            if self.left.is_expression():
                additional_needs_resolution = True

            if self.left.is_address_expression():
                additional_needs_resolution = True

            additional = self.left

            if "PCR" in self.right:
                if additional_needs_resolution:
                    raw_post_byte |= 0x00
                    post_byte_choices = [0x9C, 0x9D]
                    max_size += 2
                else:
                    size += 2 if self.left.is_extended() else 1
                    max_size = size
                    raw_post_byte |= 0x9D if self.left.is_extended() else 0x9C
            else:
                size += additional.byte_len()
                max_size = size
                raw_post_byte |= 0x99 if self.left.is_extended() else 0x98

        return CodePackage(
            op_code=NumericValue(self.instruction.mode.ind),
            post_byte=NumericValue(raw_post_byte),
            post_byte_choices=post_byte_choices,
            additional=additional,
            size=size,
            max_size=max_size,
            additional_needs_resolution=additional_needs_resolution,
        )


class IndexedOperand(Operand):
    def __init__(self, operand_string, instruction):
        super().__init__(instruction)
        self.type = OperandType.INDEXED
        self.operand_string = operand_string
        try:
            self.value = Value.create_from_str(self.operand_string, self.instruction)
        except ValueTypeError:
            raise OperandTypeError("[{}] is not an indexed value".format(operand_string))
        if not self.value.is_leftright():
            raise OperandTypeError("[{}] is not an indexed value".format(operand_string))
        self.left = self.value.left
        self.right = self.value.right

    def resolve_symbols(self, symbol_table):
        if self.left != "":
            if self.left not in ["A", "B", "D"]:
                self.left = Value.create_from_str(self.left, self.instruction, default_mode_extended=False)
                if self.left.is_symbol():
                    self.left = self.left.resolve(symbol_table)
                if self.left.is_address_expression() or self.left.is_expression():
                    self.left = self.left.resolve(symbol_table)
        return self

    def translate(self):
        if not self.instruction.mode.ind:
            raise OperandTypeError(
                "Instruction [{}] does not support indexed addressing".format(self.instruction.mnemonic)
            )
        raw_post_byte = 0x00
        post_byte_choices = []
        size = self.instruction.mode.ind_sz
        max_size = size
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

            if self.left.is_address():
                additional_needs_resolution = True
                self.left = NumericValue(self.left.int)

            if self.left.is_expression():
                additional_needs_resolution = True

            if self.left.is_address_expression():
                additional_needs_resolution = True

            additional = self.left

            if "PCR" in self.right:
                if additional_needs_resolution:
                    raw_post_byte |= 0x00
                    post_byte_choices = [0x8C, 0x8D]
                    max_size += 2
                else:
                    size += 2 if self.left.is_extended() else 1
                    max_size = size
                    raw_post_byte |= 0x8D if self.left.is_extended() else 0x8C
            else:
                if additional.int <= 0x1F:
                    raw_post_byte |= additional.int
                else:
                    size += additional.byte_len()
                    max_size = size
                    raw_post_byte |= 0x89 if self.left.is_extended() else 0x88

        return CodePackage(
            op_code=NumericValue(self.instruction.mode.ind),
            post_byte=NumericValue(raw_post_byte),
            additional=additional,
            size=size,
            additional_needs_resolution=additional_needs_resolution,
            post_byte_choices=post_byte_choices,
            max_size=max_size,
        )


# E N D   O F   F I L E #######################################################
