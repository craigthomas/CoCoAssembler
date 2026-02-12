"""
Copyright (C) 2026 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

from copy import copy

from cocoasm.exceptions import ParseError, TranslationError, OperandTypeError
from cocoasm.instruction import INSTRUCTIONS, CodePackage, MACRO_CALL_INSTRUCTION
from cocoasm.operands import Operand, BadInstructionOperand
from cocoasm.values import NumericValue

# C O N S T A N T S ###########################################################

# Pattern to recognize a blank line
BLANK_LINE_REGEX = re.compile(r"^\s*$")

# Pattern to parse a comment line
COMMENT_LINE_REGEX = re.compile(r"^\s*;\s*(?P<comment>.*)$")

# Pattern to parse a single line
ASM_LINE_REGEX = re.compile(
    r"^(?P<label>[\w@\\.]*)\s+(?P<mnemonic>\w*)\s+(?P<operands>[\w\[\]><'\"@:,.#?$%^&*()=!+\-/\\]*)\s*;*(?P<comment>.*)$"
)

# Pattern to recognize a macro definition
MACRO_DEF_LINE_REGEX = re.compile(
    r"^(?P<label>[\w]+)\s+MACRO\s*;*(?P<comment>.*)$"
)

# Pattern to recognize an end macro definition
MACRO_END_DEF_LINE_REGEX = re.compile(
    r"\s+ENDM\s*;*(?P<comment>.*)$"
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
    def __init__(self, line, line_length=0):
        self.is_empty = True
        self.is_comment_only = False
        self.macro_name = ""
        self.macro_call_regex = None
        self.macro_operands = None
        self.instruction = None
        self.label = ""
        self.operand = None
        self.original_operand = None
        self.comment = None
        self.mnemonic = ""
        self.state = None
        self.fixed_size = True
        self.pcr_size_hint = 2
        self.code_pkg = CodePackage()
        self.original_line = line
        self.line_length = line_length
        self.compile_macro_call_regex()
        self.parse_line(line)

    def __str__(self):
        op_code_string = ""
        op_code_string += self.code_pkg.op_code.hex()
        op_code_string += self.code_pkg.post_byte.hex()
        op_code_string += self.code_pkg.additional.hex()

        address = self.code_pkg.address.hex(size=4)
        op_string = op_code_string.ljust(10, ' ')
        label = self.label.rjust(10, ' ')
        mnemonic = self.mnemonic.rjust(5, ' ')
        original = self.original_operand.operand_string.ljust(30, ' ')
        comment = self.comment.ljust(40, ' ')

        result = f"${address} {op_string:.10} {label} {mnemonic} {original} ; {comment}"

        return result if self.line_length <= 0 else result[:self.line_length]

    def __eq__(self, other):
        return self.is_empty == other.is_empty and \
            self.is_comment_only == other.is_comment_only and \
            self.instruction == other.instruction and \
            self.label == other.label and \
            self.comment == other.comment and \
            self.mnemonic == other.mnemonic and \
            self.state == other.state and \
            self.fixed_size == other.fixed_size and \
            self.pcr_size_hint == other.pcr_size_hint


    def compile_macro_call_regex(self):
        """
        Programmatically construct and then compile the macro call
        regular expression. We do this using a loop since there can be
        up to 36 operands allowed per macro call.
        """
        macro_call_str = r"^(?P<label>\w*)\s+(?P<macro_name>\w+)(\s+)?"
        for x in range(36):
            macro_call_str += rf"(?P<op{x}>[\w\[\]><'\"@:.#?$%^&*()=!+\-/]+)?(,)?"
        macro_call_str += r"$"
        self.macro_call_regex = re.compile(macro_call_str)


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

        data = MACRO_DEF_LINE_REGEX.match(line)
        if data:
            self.is_empty = False
            self.label = data.group("label") or ""
            self.instruction = next((op for op in INSTRUCTIONS if op.mnemonic == "MACRO"), None)
            self.comment = data.group("comment").strip()
            if self.instruction.is_start_macro and not self.label:
                raise ParseError("Macro definition must have a label", line)
            return

        data = MACRO_END_DEF_LINE_REGEX.match(line)
        if data:
            self.is_empty = False
            self.instruction = next((op for op in INSTRUCTIONS if op.mnemonic == "ENDM"), None)
            self.comment = data.group("comment").strip()
            return

        data = ASM_LINE_REGEX.match(line)
        if data:
            self.label = data.group("label") or ""
            self.mnemonic = data.group("mnemonic").upper() or ""
            self.instruction = next((op for op in INSTRUCTIONS if op.mnemonic == self.mnemonic), None)
            self.original_operand = copy(self.operand)
            if not self.instruction:
                # Attempt to parse as a macro call
                macro_data = self.macro_call_regex.match(line)
                if macro_data:
                    self.label = macro_data.group("label") or ""
                    self.macro_name = macro_data.group("macro_name") or ""
                    self.macro_operands = [macro_data.group(f"op{x}") if macro_data.group(f"op{x}") else "" for x in range(36)]
                    self.is_empty = False
                    self.instruction = MACRO_CALL_INSTRUCTION
                    return
                else:
                    self.original_operand = BadInstructionOperand(data.group("operands"), self.instruction)
                    self.comment = data.group("comment")
                    raise ParseError(f"[{self.mnemonic}] invalid mnemonic", line)
            if self.instruction.is_string_define:
                original_operand = data.group("operands")
                if data.group("comment"):
                    original_operand = f'{data.group("operands")} {data.group("comment").strip()}'
                starting_symbol = original_operand[0]
                ending_location = original_operand.find(starting_symbol, 1)
                self.operand = Operand.create_from_str(
                    original_operand[0:ending_location + 1].strip(),
                    self.instruction
                )
                self.original_operand = copy(self.operand)
                self.comment = original_operand[ending_location + 2:].strip() or ""
                self.is_empty = False
            else:
                try:
                    self.operand = Operand.create_from_str(data.group("operands"), self.instruction)
                    self.original_operand = copy(self.operand)
                    self.comment = data.group("comment").strip() or ""
                    self.is_empty = False
                except OperandTypeError as error:
                    raise ParseError(str(error), line)
            return

        raise ParseError("Could not parse line", line)

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
        if not self.code_pkg.address.is_none():
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
        except Exception as error:
            raise TranslationError(str(error), self)

    def translate(self):
        """
        Translate the mnemonic into an actual operation.
        """
        try:
            self.code_pkg = self.operand.translate()
            self.fixed_size = not (self.code_pkg.additional_needs_resolution or self.code_pkg.post_byte_choices)
        except Exception as error:
            raise TranslationError(str(error), self)

    def determine_pcr_relative_sizes(self, statements, this_index):
        """
        Given a PCR relative operation, determine whether we have an 8-bit or 16-bit offset
        from the program counter. Mark the correct size for the statement when complete,
        so that other program counter relative checks can complete.

        :param statements: the full set of statements that make up the program
        :param this_index: the index that this instruction occurs at
        """
        # TODO: implement detection of 5-bit offsets as an optimization
        min_size = 0
        max_size = 0
        positive_range = True

        rel_index = self.code_pkg.additional.int
        if self.operand.left.is_address_expression():
            rel_index = self.operand.left.extract_address_index_from_expression()

        range_count = range(this_index, rel_index)
        if rel_index < this_index:
            positive_range = False
            range_count = range(rel_index, this_index)

        for x in range_count:
            max_size += statements[x].code_pkg.max_size
            min_size += statements[x].code_pkg.size

        raw_post_byte = self.code_pkg.post_byte.int
        max_size += 2
        min_size += 2

        if positive_range:
            if min_size <= 127 and max_size <= 127:
                self.code_pkg.size += 1
                self.code_pkg.max_size = self.code_pkg.size
                self.pcr_size_hint = 2
                self.fixed_size = True
                raw_post_byte |= self.code_pkg.post_byte_choices[0]
                self.code_pkg.post_byte = NumericValue(raw_post_byte)
            elif min_size > 127 and max_size > 127:
                self.code_pkg.size += 2
                self.code_pkg.max_size = self.code_pkg.size
                self.pcr_size_hint = 4
                self.fixed_size = True
                raw_post_byte |= self.code_pkg.post_byte_choices[1]
                self.code_pkg.post_byte = NumericValue(raw_post_byte)
        else:
            if min_size <= 128 and max_size <= 128:
                self.code_pkg.size += 1
                self.code_pkg.max_size = self.code_pkg.size
                self.pcr_size_hint = 2
                self.fixed_size = True
                raw_post_byte |= self.code_pkg.post_byte_choices[0]
                self.code_pkg.post_byte = NumericValue(raw_post_byte)
            elif min_size > 128 and max_size > 128:
                self.code_pkg.size += 2
                self.code_pkg.max_size = self.code_pkg.size
                self.pcr_size_hint = 4
                self.fixed_size = True
                raw_post_byte |= self.code_pkg.post_byte_choices[1]
                self.code_pkg.post_byte = NumericValue(raw_post_byte)

    def fix_addresses(self, statements, this_index):
        """
        Once all the statements have been translated, all the addresses
        must be 'fixed'. In particular, branch operations need to know how
        many statements they need to skip ahead or behind, and the address
        at the target statement. This function calculates what the target
        of a branch, jump or subroutine call needs to go to, and inserts
        it in the code package for the assembled instruction.

        :param statements: the full set of statements that make up the program
        :param this_index: the index that this instruction occurs at
        """
        if self.operand.is_relative():
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

        if self.operand.value.is_address_expression():
            self.code_pkg.additional = self.operand.value.calculate_address_offset(statements)

        if self.operand.value.is_address():
            self.code_pkg.additional = statements[self.operand.value.int].code_pkg.address

        if self.code_pkg.additional_needs_resolution:
            if self.operand.is_indexed() and self.operand.left and self.operand.left.is_address_expression():
                relative_address = self.operand.left.calculate_address_offset(statements).int
            else:
                relative_address = statements[self.code_pkg.additional.int].code_pkg.address.int

            start_address = statements[this_index].code_pkg.address.int
            jump_amount = relative_address - start_address - self.code_pkg.size
            self.code_pkg.additional = NumericValue(jump_amount, size_hint=self.pcr_size_hint)

# E N D   O F   F I L E #######################################################
