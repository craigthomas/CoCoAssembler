"""
Copyright (C) 2026 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
This file contains the main Program class for the CoCo Assembler.
"""
# I M P O R T S ###############################################################

from cocoasm.exceptions import TranslationError, MacroError
from cocoasm.statement import Statement
from cocoasm.values import AddressValue, NoneValue
from cocoasm.virtualfiles.source_file import SourceFile
from cocoasm.macro_types import MACRO_VALUE_STRINGS, MACRO_LABEL_STRINGS

# C L A S S E S ###############################################################


class Program(object):
    """
    The Program class represents an actual Color Computer program. Each Program
    contains a list of statements. Additionally, a Program keeps track of all
    the user-defined symbols in the program.
    """
    def __init__(self):
        self.symbol_table = dict()
        self.statements = []
        self.address = 0x0
        self.origin = NoneValue()
        self.exec_address = None
        self.name = None
        self.macros = dict()

    def process(self, source_file, line_length=0):
        """
        Processes a filename for assembly.

        :param source_file: the source file to process
        :param line_length: the maximum length of a statement when printed
        """
        self.statements = self.parse(source_file, line_length=line_length)
        self.translate_statements()

    @classmethod
    def parse(cls, contents, line_length=0):
        """
        Parses a single file and saves the set of statements.

        :param contents: a list of strings, each string represents one line of assembly
        :param line_length: sets the maximum length of a printed statement
        """
        statements = []
        for line in contents:
            statement = Statement(line, line_length=line_length)
            if not statement.is_empty and not statement.is_comment_only:
                statements.append(statement)
        return statements

    @classmethod
    def process_mnemonics(cls, statements, line_length=0):
        """
        Given a list of statements, processes the mnemonics on each statement, and
        assigns each statement an Instruction object. If the statement is the
        pseudo operation INCLUDE, then it will parse the statements with the
        associated include file. If the statement is the operation MACRO, then
        it will excise the macro code from the list of statements.

        :param statements: the list of statements to process
        :param line_length: sets the maximum length of a printed statement
        :return: a list of processed statements, a list of processed macros
        """
        processed_statements = []
        final_statements = []
        in_macro_definition = False
        macro_label = ""
        macros = dict()

        # Pass 1 - integrate any include files into the current statement list
        for statement in statements:
            include_filename = statement.get_include_filename()
            if include_filename:
                include_source = SourceFile(include_filename)
                include_source.read_file()
                include, included_macros = cls.process_mnemonics(
                    cls.parse(
                        include_source.get_buffer(),
                        line_length=line_length
                    )
                )
                processed_statements.extend(include)
                macros.update(included_macros)
            else:
                processed_statements.extend([statement])

        # Pass 2 - look for any macro definitions and add them to the dictionary of macros
        for statement in processed_statements:
            if statement.instruction.is_start_macro and in_macro_definition:
                raise MacroError(f"Nested macro definition detected in macro [{macro_label}]")
            elif statement.instruction.is_start_macro:
                in_macro_definition = True
                macro_label = statement.label
                if macro_label in macros:
                    raise MacroError(f"Macro [{macro_label}] has multiple definitions")
                macros[macro_label] = []
            elif statement.instruction.is_end_macro:
                in_macro_definition = False
                macro_label = ""
            elif in_macro_definition:
                macros[macro_label].append(statement)
            else:
                final_statements.append(statement)

        if in_macro_definition:
            raise MacroError(f"Macro defined but ENDM not found when parsing macro [{macro_label}]")

        return final_statements, macros

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
                raise TranslationError(f"Label [{label}] redefined", statement)
            if statement.instruction.is_pseudo_define:
                self.symbol_table[label] = statement.operand.value
            else:
                self.symbol_table[label] = AddressValue(index)


    @staticmethod
    def replace_macro_arguments(statement, macro_statement, macro_symbol_counts):
        """
        Replaces the dummy value with the value passed into the macro .

        :param statement: the statement to modify
        :param macro_statement: the statement containing the macro call
        :param macro_symbol_counts: the dictionary of symbols and the number of times they have been called
        :return: a new statement with the replaced macro dummy values
        """
        line = statement.original_line
        observed_macro_symbols = set()
        for index, value in enumerate(MACRO_VALUE_STRINGS):
            line = line.replace(MACRO_VALUE_STRINGS[index], macro_statement.macro_operands[index])
            for macro_symbol in macro_symbol_counts.keys():
                if macro_symbol in line:
                    observed_macro_symbols.add(macro_symbol)
                    macro_count_string = "{:05d}".format(macro_symbol_counts[macro_symbol])
                    new_symbol = macro_symbol.replace(r"\.", "") + macro_count_string
                    line = line.replace(macro_symbol, new_symbol)
        return Statement(line), observed_macro_symbols


    def translate_statements(self):
        """
        Translates all the parsed statements into their respective
        opcodes.
        """
        processed_statements, self.macros = self.process_mnemonics(self.statements)
        self.statements = []

        # Expand macros
        macro_symbol_counts = {key: 0 for key in MACRO_LABEL_STRINGS}
        for statement in processed_statements:
            if statement.instruction.is_macro_call:
                if statement.macro_name and statement.macro_name not in self.macros.keys():
                    raise MacroError(f"No macro named [{statement.macro_name}] has been defined")
                else:
                    observed_macros = set()
                    for macro_statement in self.macros[statement.macro_name]:
                        new_statement, observed_macros = self.replace_macro_arguments(macro_statement, statement, macro_symbol_counts)
                        self.statements.append(new_statement)
                    for macro_symbol in observed_macros:
                        macro_symbol_counts[macro_symbol] += 1
            else:
                self.statements.append(statement)

        # Construct symbol table
        for index, statement in enumerate(self.statements):
            self.save_symbol(index, statement)

        # Resolve symbols
        for index, statement in enumerate(self.statements):
            statement.resolve_symbols(self.symbol_table)

        # Translate each statement to code package
        for index, statement in enumerate(self.statements):
            statement.translate()

        # Calculate the size of each statement
        while not self.all_sizes_fixed():
            for index, statement in enumerate(self.statements):
                if not statement.fixed_size:
                    statement.determine_pcr_relative_sizes(self.statements, index)

        # Figure out approximate address based on code package size
        address = 0
        for index, statement in enumerate(self.statements):
            address = statement.set_address(address)
            address += statement.code_pkg.size

        # Fix relative addressing statements
        for index, statement in enumerate(self.statements):
            statement.fix_addresses(self.statements, index)

        # Update the symbol table with the proper addresses
        for symbol, value in self.symbol_table.items():
            if value.is_address():
                self.symbol_table[symbol] = self.statements[value.int].code_pkg.address

        # Find the origin, exec_address and name of the project
        for statement in self.statements:
            if statement.instruction.is_origin:
                self.origin = statement.code_pkg.address
                if self.exec_address is None:
                    self.exec_address = statement.code_pkg.address
            if statement.instruction.is_name:
                self.name = statement.operand.operand_string
            if statement.instruction.is_end:
                if statement.operand.operand_string:
                    for symbol, value in self.symbol_table.items():
                        if statement.operand.operand_string == symbol:
                            if value.is_numeric():
                                self.exec_address = value

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
                    hex_byte = f"{op_code[index]}{op_code[index+1]}"
                    machine_codes.append(int(hex_byte, 16))
                for index in range(0, statement.code_pkg.post_byte.hex_len(), 2):
                    post_byte = statement.code_pkg.post_byte.hex()
                    hex_byte = f"{post_byte[index]}{post_byte[index + 1]}"
                    machine_codes.append(int(hex_byte, 16))
                for index in range(0, statement.code_pkg.additional.hex_len(), 2):
                    additional = statement.code_pkg.additional.hex()
                    hex_byte = f"{additional[index]}{additional[index + 1]}"
                    machine_codes.append(int(hex_byte, 16))
        return machine_codes

    def all_sizes_fixed(self):
        """
        Checks to see if all the statements have fixed sizes. Returns
        True if all the sizes are fixed, False otherwise.
        """
        for statement in self.statements:
            if not statement.fixed_size:
                return False
        return True

    def get_symbol_table(self):
        """
        Returns a list of strings. Each string contains one entry from the symbol table.
        """
        lines = []
        for symbol, value in self.symbol_table.items():
            lines.append(f"${value.hex().ljust(4, ' ')} {symbol}")
        return lines

    def get_statements(self):
        """
        Returns a list of strings. Each string represents one assembled statement
        """
        return [str(statement) for statement in self.statements]

# E N D   O F   F I L E #######################################################
