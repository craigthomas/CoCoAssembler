"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
This file contains the main Program class for the CoCo Assembler.
"""
# I M P O R T S ###############################################################

import sys

from cocoasm.exceptions import TranslationError, ParseError
from cocoasm.statement import Statement
from cocoasm.assembler_state import AssemblerState
from cocoasm.values import AddressValue

# C L A S S E S ###############################################################


class Program(object):
    """
    The Program class represents an actual Color Computer program. Each Program
    contains a list of statements. Additionally, a Program keeps track of all
    the user-defined symbols in the program.
    """
    def __init__(self, filename):
        self.symbol_table = dict()
        self.statements = []
        self.address = 0x0
        self.state = AssemblerState()
        self.process(filename)

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

    @staticmethod
    def parse_file(filename):
        """
        Parses all of the lines in a file, and transforms each line into
        a Statement. Returns a list of all the statements in the file.

        :param filename: the name of the file to parse
        """
        statements = []
        if not filename:
            return statements

        with open(filename) as infile:
            for line in infile:
                statement = Statement(line)
                if not statement.is_empty() and not statement.is_comment_only():
                    statements.append(statement)

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
            statement.match_mnemonic()
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
        label = statement.get_label()
        if label:
            if label in self.symbol_table:
                raise TranslationError("Label [" + label + "] redefined", statement)
            if statement.instruction.is_pseudo_define():
                self.symbol_table[label] = statement.operand.sub_expression
            else:
                self.symbol_table[label] = AddressValue(index)

    def translate_statements(self):
        """
        Translates all the parsed statements into their respective
        opcodes.
        """
        self.statements = self.process_mnemonics(self.statements)
        for index, statement in enumerate(self.statements):
            self.save_symbol(index, statement)

        for index, statement in enumerate(self.statements):
            statement.translate_pseudo(self.symbol_table)

        for index, statement in enumerate(self.statements):
            statement.translate(self.symbol_table)

        address = 0
        for index, statement in enumerate(self.statements):
            address = statement.set_address(address)
            address += statement.get_size()

        for index, statement in enumerate(self.statements):
            statement.fix_addresses(self.statements, index)

    def save_binary_file(self, filename):
        """
        Writes out the assembled statements to the specified file
        name.

        :param filename: the name of the file to save statements
        """
        machine_codes = []
        for statement in self.statements:
            if not statement.is_empty() and not statement.comment_only:
                for index in range(0, len(statement.op_code), 2):
                    machine_codes.append(int(statement.op_code[index:index + 2], 16))
        with open(filename, "wb") as outfile:
            outfile.write(bytearray(machine_codes))

    def print_symbol_table(self):
        """
        Prints out the symbol table and any values contained within it.
        """
        print("-- Symbol Table --")
        for symbol, value in self.symbol_table.items():
            print(value)

    def print_statements(self):
        """
        Prints out the assembled statements.
        """
        print("-- Assembled Statements --")
        for index, statement in enumerate(self.statements):
            print("{}".format(statement))

    @staticmethod
    def throw_error(error):
        """
        Prints out an error message.

        :param error: the error message to throw
        """
        print(error.value)
        print("line: {}".format(str(error.statement)))
        sys.exit(1)

# E N D   O F   F I L E #######################################################
