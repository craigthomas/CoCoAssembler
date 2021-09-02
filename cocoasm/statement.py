"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from copy import copy

from cocoasm.exceptions import ParseError, TranslationError
from cocoasm.instruction import INSTRUCTIONS, CodePackage
from cocoasm.operands import Operand, OperandType, BadInstructionOperand, ExtendedOperand, DirectOperand
from cocoasm.values import ValueType, NumericValue

# C O N S T A N T S ###########################################################

# Pattern to recognize a blank line
BLANK_LINE_REGEX = re.compile(r"^\s*$")

# Pattern to parse a comment line
COMMENT_LINE_REGEX = re.compile(r"^\s*;\s*(?P<comment>.*)$")

# Pattern to parse a single line
ASM_LINE_REGEX = re.compile(
    r"^(?P<label>[\w@]*)\s+(?P<mnemonic>\w*)\s+(?P<operands>[\w\[\]#$,+-.*@\"]*)\s*[;]*(?P<comment>.*)$"
)

# Pattern to recognize a direct value
DIR_REGEX = re.compile(
    r"^<(?P<value>.*)"
)

# C L A S S E S  ##############################################################


class Statement(object):
    """
    The Statement class represents a single line of assembly language. Each
    statement is constructed from a single line that has the following format:

        LABEL   MNEMONIC   OPERANDS    COMMENT

    The statement can be parsed and translated to its Chip8 machine code
    equivalent.
    """
    def __init__(self, line):
        self.is_empty = True
        self.is_comment_only = False
        self.instruction = None
        self.label = ""
        self.operand = None
        self.original_operand = None
        self.comment = None
        self.mnemonic = ""
        self.state = None
        self.code_pkg = CodePackage()
        self.parse_line(line)

    def __str__(self):
        op_code_string = ""
        op_code_string += self.code_pkg.op_code.hex()
        op_code_string += self.code_pkg.post_byte.hex()
        op_code_string += self.code_pkg.additional.hex()

        return "${} {:.10} {} {} {} ; {}".format(
            self.code_pkg.address.hex(size=4),
            op_code_string.ljust(10, ' '),
            self.label.rjust(10, ' '),
            self.mnemonic.rjust(5, ' '),
            self.original_operand.operand_string.ljust(30, ' '),
            self.comment.ljust(40, ' '),
            # self.operand.type
        )

    def get_include_filename(self):
        """
        Returns the name of the file to include in the current stream of
        statements if the statement is the pseudo op INCLUDE, and there is
        a value for the operand

        :return: the name of the file to include
        """
        return self.operand.operand_string if self.instruction.is_include else None

    def parse_line(self, line):
        """
        Parse a line of assembly language text.

        :param line: the line of text to parse
        """
        if BLANK_LINE_REGEX.search(line):
            return

        data = COMMENT_LINE_REGEX.match(line)
        if data:
            self.is_empty = False
            self.is_comment_only = True
            self.comment = data.group("comment").strip()
            return

        data = ASM_LINE_REGEX.match(line)
        if data:
            self.label = data.group("label") or ""
            self.mnemonic = data.group("mnemonic").upper() or ""
            self.instruction = next((op for op in INSTRUCTIONS if op.mnemonic == self.mnemonic), None)
            self.original_operand = copy(self.operand)
            if not self.instruction:
                self.original_operand = BadInstructionOperand(data.group("operands"), self.instruction)
                self.comment = data.group("comment")
                raise ParseError("[{}] invalid mnemonic".format(self.mnemonic), self)
            if self.instruction.is_string_define:
                original_operand = data.group("operands")
                if data.group("comment"):
                    original_operand = "{} {}".format(data.group("operands"), data.group("comment").strip())
                starting_symbol = original_operand[0]
                ending_location = original_operand.find(starting_symbol, 1)
                self.operand = Operand.create_from_str(original_operand[0:ending_location + 1].strip(), self.instruction)
                self.original_operand = copy(self.operand)
                self.comment = original_operand[ending_location + 2:].strip() or ""
                self.is_empty = False
            else:
                self.operand = Operand.create_from_str(data.group("operands"), self.instruction)
                self.original_operand = copy(self.operand)
                self.comment = data.group("comment").strip() or ""
                self.is_empty = False
            return

        raise ParseError("Could not parse line [{}]".format(line), self)

    def set_address(self, address):
        """
        This function sets the address where this statement should be located
        in memory. If the address is not already set, it will set the address
        and return the address that was set. If the address was already set
        (for example, in an ORG operation), it will return that address
        instead.

        :param address: the address to set for the statement
        :return: the address that was set or returned
        """
        if not self.code_pkg.address.is_type(ValueType.NONE):
            return self.code_pkg.address.int
        self.code_pkg.address = NumericValue(address)
        return self.code_pkg.address.int

    def resolve_symbols(self, symbol_table):
        """
        Resolve any symbols within operands, and check to make sure operand types
        are valid.
        """
        try:
            self.operand = self.operand.resolve_symbols(symbol_table)
            self.check_types()
        except ValueError as error:
            raise TranslationError(str(error), self)

    def translate(self):
        """
        Translate the mnemonic into an actual operation.
        """
        try:
            self.code_pkg = self.operand.translate()
        except ValueError as error:
            raise TranslationError(str(error), self)

    def check_types(self):
        if self.operand.is_type(OperandType.DIRECT):
            if self.operand.value.is_type(ValueType.NUMERIC):
                if self.operand.value.byte_len() == 2:
                    self.operand = ExtendedOperand(
                        self.operand.operand_string,
                        self.operand.instruction,
                        self.operand.value,
                    )
                    return

            # TODO: Add in ability to check direct page register here - extended operands may be direct instead

        if self.operand.is_type(OperandType.EXTENDED):
            if self.operand.value.is_type(ValueType.NUMERIC):
                if self.operand.value.byte_len() == 1:
                    raise TranslationError("[{}] is not an extended value".format(self.operand.operand_string), self)

    def fix_pcr_relative_addresses(self, statements, this_index):
        """
        Once all of the statements have been translated, then we need to
        check whether program counter relative indexed statements can
        be 8-bit, or if they must be 16-bit. This operation changes the
        size of a code package depending on how many steps away a statement
        is. To calculate the relative offset, we use a cheat - since we
        don't yet know how big any of the PCR statements are, we count the
        size of each instruction between the PCR statement using the code
        package's max_size. This tells us potentially how large the statements
        will be. If they are bigger than an 8-bit value, then we can default
        to a 16-bit offset. There may be edge cases where this heuristic may fail,
        most notably when there is a PCR statement that has not yet been resolved
        to be 8-bit, and would change the max_size calculation to be a valid
        8-bit offset value instead.

        :param statements: the full set of statements that make up the program
        :param this_index: the index that this instruction occurs at
        """
        if self.code_pkg.additional_needs_resolution and self.code_pkg.post_byte_choices:
            relative_index = self.code_pkg.additional.int
            if relative_index > this_index:
                total_size = 0
                raw_post_byte = self.code_pkg.post_byte.int
                for x in range(this_index, relative_index):
                    total_size += statements[x].code_pkg.max_size
                if total_size <= 255:
                    self.code_pkg.size += 1
                    raw_post_byte |= self.code_pkg.post_byte_choices[0]
                else:
                    self.code_pkg.size += 2
                    raw_post_byte |= self.code_pkg.post_byte_choices[1]
                self.code_pkg.post_byte = NumericValue(raw_post_byte)
            else:
                total_size = 0
                raw_post_byte = self.code_pkg.post_byte.int
                for x in range(relative_index, this_index):
                    total_size += statements[x].code_pkg.max_size
                if total_size <= 255:
                    self.code_pkg.size += 1
                    raw_post_byte |= self.code_pkg.post_byte_choices[0]
                else:
                    self.code_pkg.size += 2
                    raw_post_byte |= self.code_pkg.post_byte_choices[1]
                self.code_pkg.post_byte = NumericValue(raw_post_byte)

    def fix_addresses(self, statements, this_index):
        """
        Once all of the statements have been translated, all of the addresses
        must be 'fixed'. In particular, branch operations need to know how
        many statements they need to skip ahead or behind, and the address
        at the target statement. This function calculates what the target
        of a branch, jump or subroutine call needs to go to, and inserts
        it in the code package for the assembled instruction.

        :param statements: the full set of statements that make up the program
        :param this_index: the index that this instruction occurs at
        """
        if self.operand.is_type(OperandType.RELATIVE):
            base_value = 0x101 if self.instruction.is_short_branch else 0x10001
            branch_index = self.code_pkg.additional.int
            size_hint = 2 if self.instruction.is_short_branch else 4
            length = 0
            if branch_index < this_index:
                length = 1
                for statement in statements[branch_index:this_index+1]:
                    length += statement.code_pkg.size
                self.code_pkg.additional = NumericValue(base_value - length, size_hint=size_hint)
            else:
                for statement in statements[this_index+1:branch_index]:
                    length += statement.code_pkg.size
                self.code_pkg.additional = NumericValue(length, size_hint=size_hint)
            return

        if self.operand.value.is_type(ValueType.ADDRESS):
            self.code_pkg.additional = statements[self.operand.value.int].code_pkg.address

        if self.code_pkg.additional_needs_resolution:
            start_address = statements[this_index].code_pkg.address
            relative_address = statements[self.code_pkg.additional.int].code_pkg.address
            size_hint = 2
            if relative_address.int > start_address.int:
                jump_amount = relative_address.int - start_address.int
                # Effective address loading is always 16-bit regardless of actual size
                if jump_amount > 255 or self.instruction.mnemonic in ["LEAX", "LEAY", "LEAS", "LEAU"]:
                    size_hint = 4
                self.code_pkg.additional = NumericValue(
                    0x00 + jump_amount - self.code_pkg.size,
                    size_hint=size_hint,
                )
            else:
                jump_amount = start_address.int - relative_address.int
                base_offset = 0x100 if jump_amount <= 255 else 0x10000
                # Effective address loading is always 16-bit regardless of actual size
                if base_offset == 0x10000 or self.instruction.mnemonic in ["LEAX", "LEAY", "LEAS", "LEAU"]:
                    size_hint = 4
                self.code_pkg.additional = NumericValue(
                    base_offset - jump_amount - self.code_pkg.size,
                    size_hint=size_hint,
                )

# E N D   O F   F I L E #######################################################
