"""
Copyright (C) 2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
This file contains the main Program class for the CoCo Assembler.
"""
# I M P O R T S ###############################################################

import sys

from cocoasm.exceptions import TranslationError, ParseError, ValueTypeError
from cocoasm.statement import Statement
from cocoasm.values import AddressValue, NoneValue

# C L A S S E S ###############################################################


class Program(object):
    """
    The Program class represents an actual Color Computer program. Each Program
    contains a list of statements. Additionally, a Program keeps track of all
    the user-defined symbols in the program.
    """
    def __init__(self, width=100):
        self.symbol_table = dict()
        self.statements = []
        self.address = 0x0
        self.origin = NoneValue()
        self.name = None
        self.width = width

    def process(self, filename):
        """
        Processes a filename for assembly.

        :param filename: the name of the file to process
        """
        try:
            self.parse(filename)
            self.translate_statements()
        except TranslationError as error:
            self.throw_error(error)
        except ParseError as error:
            self.throw_error(error)

    def parse(self, filename):
        """
        Parses a single file and saves the set of statements.

        :param filename: the name of the file to process
        """
        self.statements = self.parse_file(filename)

    def parse_file(self, filename):
        """
        Parses all of the lines in a file, and transforms each line into
        a Statement. Returns a list of all the statements in the file.

        :param filename: the name of the file to parse
        """
        statements = []
        if not filename:
            return statements

        try:
            with open(filename) as infile:
                for line in infile:
                    statement = Statement(line)
                    if not statement.is_empty and not statement.is_comment_only:
                        statements.append(statement)
        except ParseError as error:
            self.throw_error(error)

        return statements

    def process_mnemonics(self, statements):
        """
        Given a list of statements, processes the mnemonics on each statement, and
        assigns each statement an Instruction object. If the statement is the
        pseudo operation INCLUDE, then it will parse the statements with the
        associated include file.

        :param statements: the list of statements to process
        :return: a list of processed statements
        """
        processed_statements = []
        for statement in statements:
            include = self.process_mnemonics(self.parse_file(statement.get_include_filename()))
            processed_statements.extend(include if include else [statement])
        return processed_statements

    def save_symbol(self, index, statement):
        """
        Checks a statement for a label and saves it to the symbol table, along with
        the index into the list of statements where the label occurs. Will raise a
        TranslationError if the label already exists in the symbol table.

        :param index: the index into the list of statements where the label occurs
        :param statement: the statement with the label
        """
        label = statement.label
        if label:
            if label in self.symbol_table:
                raise TranslationError("Label [" + label + "] redefined", statement)
            if statement.instruction.is_pseudo_define:
                self.symbol_table[label] = statement.operand.value
            else:
                self.symbol_table[label] = AddressValue(index)

    def translate_statements(self):
        """
        Translates all the parsed statements into their respective
        opcodes.
        """
        try:
            self.statements = self.process_mnemonics(self.statements)
            for index, statement in enumerate(self.statements):
                self.save_symbol(index, statement)

            for index, statement in enumerate(self.statements):
                try:
                    statement.resolve_symbols(self.symbol_table)
                except ValueTypeError as error:
                    raise TranslationError(str(error), statement)

            for index, statement in enumerate(self.statements):
                statement.translate()

            while not self.all_sizes_fixed():
                for index, statement in enumerate(self.statements):
                    if not statement.fixed_size:
                        statement.determine_pcr_relative_sizes(self.statements, index)

            address = 0
            for index, statement in enumerate(self.statements):
                address = statement.set_address(address)
                address += statement.code_pkg.size

            for index, statement in enumerate(self.statements):
                statement.fix_addresses(self.statements, index)

            # Update the symbol table with the proper addresses
            for symbol, value in self.symbol_table.items():
                if value.is_address():
                    self.symbol_table[symbol] = self.statements[value.int].code_pkg.address

            # Find the origin and name of the project
            for statement in self.statements:
                if statement.instruction.is_origin:
                    self.origin = statement.code_pkg.address
                if statement.instruction.is_name:
                    self.name = statement.operand.operand_string
        except TranslationError as error:
            self.throw_error(error)

    def get_binary_array(self):
        """
        Returns an array containing the machine code statements for the
        assembled program.

        :return: returns the assembled program bytes
        """
        machine_codes = []
        for statement in self.statements:
            if not statement.is_empty and not statement.is_comment_only:
                for index in range(0, statement.code_pkg.op_code.hex_len(), 2):
                    op_code = statement.code_pkg.op_code.hex()
                    hex_byte = "{}{}".format(op_code[index], op_code[index+1])
                    machine_codes.append(int(hex_byte, 16))
                for index in range(0, statement.code_pkg.post_byte.hex_len(), 2):
                    post_byte = statement.code_pkg.post_byte.hex()
                    hex_byte = "{}{}".format(post_byte[index], post_byte[index + 1])
                    machine_codes.append(int(hex_byte, 16))
                for index in range(0, statement.code_pkg.additional.hex_len(), 2):
                    additional = statement.code_pkg.additional.hex()
                    hex_byte = "{}{}".format(additional[index], additional[index + 1])
                    machine_codes.append(int(hex_byte, 16))
        return machine_codes

    def all_sizes_fixed(self):
        """
        Checks to see if all of the statements have fixed sizes. Returns
        True if all the sizes are fixed, False otherwise.
        """
        for statement in self.statements:
            if not statement.fixed_size:
                return False
        return True

    def print_symbol_table(self):
        """
        Prints out the symbol table and any values contained within it.
        """
        print("-- Symbol Table --")
        for symbol, value in self.symbol_table.items():
            print("${} {}".format(value.hex().ljust(4, ' '), symbol))

    def print_statements(self):
        """
        Prints out the assembled statements.
        """
        print("-- Assembled Statements --")
        for index, statement in enumerate(self.statements):
            print("{}".format(str(statement).ljust(self.width)))

    def throw_error(self, error):
        """
        Prints out an error message.

        :param error: the error message to throw
        """
        print(error.value)
        print("{}".format(str(error.statement).ljust(self.width)))
        sys.exit(1)

# E N D   O F   F I L E #######################################################
