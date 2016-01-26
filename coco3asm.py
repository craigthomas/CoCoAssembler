"""
Copyright (C) 2012-2016 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A Color Computer 3 assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import argparse
import re
import sys

# C O N S T A N T S ###########################################################

# Addressing modes
INH = "Inherent"
IMM = "Immediate"
DIR = "Direct"
IND = "Indexed"
EXT = "Extended"

# Dictionary entries
LABEL = "label"
OP = "op"
OPERANDS = "operands"
COMMENT = "comment"
MODE = "mode"
OPCODE = "opcode"
DATA = "data"
IVLD = 0x01

# Illegal addressing mode
ILLEGAL_MODE = 0x00

# Opcode translation based on addressing modes
OPERATIONS = {
    "ABX":  {INH: 0x3A, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ADCA": {INH: 0x00, IMM: 0x89, DIR: 0x99, IND: 0xA9, EXT: 0xB9},
    "ADCB": {INH: 0x00, IMM: 0xC9, DIR: 0xD9, IND: 0xE9, EXT: 0xF9},
}

# Pseudo operations
END = "END"
ORG = "ORG"
EQU = "EQU"
SET = "SET"
RMB = "RMB"
FCB = "FCB"
FDB = "FDB"
FCC = "FCC"
INCLUDE = "INCLUDE"
PSEUDO_OPERATIONS = [END, ORG, EQU, SET, RMB, FCB, FDB, FCC, INCLUDE]

# Opcode operand requirements based on addressing modes
OPERAND_COUNTS = {
    "ABX": {INH: 0, IMM: 0, DIR: 0, IND: 0, EXT: 0},
    "ADCA": {INH: 0, IMM: 1, DIR: 1, IND: 1, EXT: 2},
    "ADCB": {INH: 0, IMM: 1, DIR: 1, IND: 1, EXT: 2},
}

# Pattern to parse a single line
ASM_LINE_REGEX = re.compile("(?P<" + LABEL + ">\w*)\s+(?P<" + OP + ">\w*)\s+"
    "(?P<" + OPERANDS + ">[\w#\$,\+-]*)\s+(?P<" + COMMENT + ">.*)")

# G L O B A L S ###############################################################

# Stores each of the symbols and their values
symbol_table = dict()


# C L A S S E S  ##############################################################


class TranslationError(Exception):
    """
    Translation errors occur when the translate function is called from
    within the Statement class. Translation errors usually refer to the fact
    that an invalid mnemonic or invalid register was specified.
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Statement:
    """
    The Statement class represents a single line of assembly language. Each
    statement is constructed from a single line that has the following format:

        LABEL   MNEMONIC   OPERANDS    COMMENT

    The statement can be parsed and translated to its COCO machine code
    equivalent.
    """
    def __init__(self):
        self.label = ""
        self.op_code = ""
        self.comments = ""
        self.size = 0
        self.address = 0
        self.op = ""
        self.operands = ""
        self.comment = ""
        self.mode = ""

    def __str__(self):
        return "$-- {} {} {} {}  # {}".format(
                # self.address[2:].upper().rjust(4, '0'),
                hex(self.op_code).rjust(4, '0'),
                self.label.rjust(15, ' '),
                self.op.rjust(5, ' '),
                self.operands.rjust(15, ' '),
                self.comment.ljust(40, ' '))

    def parse_line(self, line):
        """
        Parse a line of assembly language text.

        :param line: the line of assembly language from the source file.
        """
        data = ASM_LINE_REGEX.match(line)
        if data:
            self.label = data.group(LABEL)
            self.op = data.group(OP)
            self.operands = data.group(OPERANDS)
            self.comment = data.group(COMMENT)

    def translate(self):
        """
        Translate the text into an actual op code.
        """
        if self.op in PSEUDO_OPERATIONS:
            return

        if self.op not in OPERATIONS:
            error = "Invalid mnemonic '{}'".format(self.op)
            raise TranslationError(error)

        self.set_addressing_mode()
        self.set_op_code()

    def get_operation(self):
        """
        Returns the operation dictionary item based upon the mnemonic.
        """
        return self.op if self.is_pseudo_op() else OPERATIONS[self.op]

    def is_pseudo_op(self):
        """
        Returns True if the operation is a pseudo operation, False otherwise.
        """
        return self.op in PSEUDO_OPERATIONS

    def set_addressing_mode(self):
        """
        Determines the correct addressing mode based on the operand.
        """
        self.mode = INH
        if self.operands.startswith("#"):
            self.mode = IMM
        if "," in self.operands:
            self.mode = IND
        if self.operands.startswith("<"):
            self.mode = DIR
        if self.operands.startswith(">"):
            self.mode = EXT

    def set_op_code(self):
        """
        Sets the op code for the statement based on the addressing mode
        and the translated op mnemonic. Will raise a TranslationError
        if the specified addressing mode does not exist.
        """
        self.op_code = self.get_operation()[self.mode]
        if self.op_code == IVLD:
            error = "Invalid addressing mode {} for operation {}".format(
                        self.mode, self.op)
            raise TranslationError(error)

    def is_empty(self):
        """
        Returns True if there is no label that is contained within the
        statement.
        """
        return self.op == ""

    def get_label(self):
        """
        Returns the label associated with this statement.
        @return: the label for this statement
        """
        return self.label

# F U N C T I O N S ###########################################################

def parse_arguments():
    """
    Parses the command-line arguments passed to the assembler.
    """
    parser = argparse.ArgumentParser(
            description="Assemble or disassemble machine language code for "
            "the COCO3. See README.md for more information, and LICENSE for "
            "terms of use.")
    parser.add_argument("filename", help="the name of the file to examine")
    parser.add_argument(
            "-s", action="store_true", help="print out the symbol table")
    parser.add_argument(
            "-p", action="store_true", help="print out the assembled "
            "statements when finished")
    parser.add_argument(
            "-o", metavar="FILE", help="stores the assembled program "
            "in FILE")
    return parser.parse_args()


def throw_error(error, statement):
    """
    Prints out an error message.

    @param error: the error message to throw
    @type error: Exception

    @param statement: the assembly statement that caused the error
    @type statement: Statement
    """
    print(error.value)
    print("Line: " + str(statement))
    sys.exit(1)


def main(args):
    """
    Runs the assembler with the specified arguments.

    @param args: the arguments to the main function
    @type: namedtuple
    """
    global symbol_table
    symbol_table = dict()
    statements = []
    address = 0x200

    # Pass 1: parse all of the statements in the file, but do not attempt
    # to resolve any of the labels or locations
    with open(args.filename) as infile:
        for line in infile:
            statement = Statement()
            statement.parse_line(line)
            if not statement.is_empty():
                statements.append(statement)

    # Pass 2: translate the statements into their respective opcodes
    for index in xrange(len(statements)):
        statement = statements[index]
        try:
            statement.translate()
        except TranslationError as error:
            throw_error(error, statement)
        label = statement.get_label()
        if label:
            if label in symbol_table:
                error = {"value": "label [" + label + "] redefined"}
                throw_error(error, statement)
            symbol_table[label] = index

    # Check to see if the user wanted to print the symbol table
    if args.s:
        print("-- Symbol Table --")
        for symbol, value in symbol_table.iteritems():
            print("{} {}".format(symbol, value))

    # Check to see if the user wanted a print out of the assembly
    if args.p:
        print("-- Assembled Statements --")
        for statement in statements:
            print(statement)

# M A I N #####################################################################

if __name__ == "__main__":
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
