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
    "ABX":   {INH: 0x3A, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ADCA":  {INH: 0x00, IMM: 0x89, DIR: 0x99, IND: 0xA9, EXT: 0xB9},
    "ADCB":  {INH: 0x00, IMM: 0xC9, DIR: 0xD9, IND: 0xE9, EXT: 0xF9},
    "ADDA":  {INH: IVLD, IMM: 0x8B, DIR: 0x9B, IND: 0xAB, EXT: 0xBB},
    "ADDB":  {INH: IVLD, IMM: 0xCB, DIR: 0xDB, IND: 0xEB, EXT: 0xFB},
    "ADDD":  {INH: IVLD, IMM: 0xC3, DIR: 0xD3, IND: 0xE3, EXT: 0xF3},
    "ANDA":  {INH: IVLD, IMM: 0x84, DIR: 0x94, IND: 0xA4, EXT: 0xB4},
    "ANDB":  {INH: IVLD, IMM: 0xC4, DIR: 0xD4, IND: 0xE4, EXT: 0xF4},
    "ANDCC": {INH: IVLD, IMM: 0x1C, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ASLA":  {INH: 0x48, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ASLB":  {INH: 0x58, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ASL":   {INH: IVLD, IMM: IVLD, DIR: 0x08, IND: 0x68, EXT: 0x78},
    "ASRA":  {INH: 0x47, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ASRB":  {INH: 0x57, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ASR":   {INH: IVLD, IMM: IVLD, DIR: 0x07, IND: 0x67, EXT: 0x77},
    "BITA":  {INH: IVLD, IMM: 0x85, DIR: 0x95, IND: 0xA5, EXT: 0xB5},
    "BITB":  {INH: IVLD, IMM: 0xC5, DIR: 0xD5, IND: 0xE5, EXT: 0xF5},
    "CLRA":  {INH: 0x4F, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "CLRB":  {INH: 0x5F, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "CLR":   {INH: IVLD, IMM: IVLD, DIR: 0x0F, IND: 0x6F, EXT: 0x7F},
    "CMPA":  {INH: IVLD, IMM: 0x81, DIR: 0x91, IND: 0xA1, EXT: 0xB1},
    "CMPB":  {INH: IVLD, IMM: 0xC1, DIR: 0xD1, IND: 0xE1, EXT: 0xF1},
    "CMPD":  {INH: IVLD, IMM: 0x1083, DIR: 0x1093, IND: 0x10A3, EXT: 0x10B3},
    "CMPS":  {INH: IVLD, IMM: 0x118C, DIR: 0x119C, IND: 0x11AC, EXT: 0x11BC},
    "CMPU":  {INH: IVLD, IMM: 0x1183, DIR: 0x1193, IND: 0x11A3, EXT: 0x11B3},
    "CMPX":  {INH: IVLD, IMM: 0x8C, DIR: 0x9C, IND: 0xAC, EXT: 0xBC},
    "CMPY":  {INH: IVLD, IMM: 0x108C, DIR: 0x109C, IND: 0x10AC, EXT: 0x10BC},
    "COMA":  {INH: 0x43, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "COMB":  {INH: 0x53, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "COM":   {INH: IVLD, IMM: IVLD, DIR: 0x03, IND: 0x63, EXT: 0x73},
    "CWAI":  {INH: IVLD, IMM: 0x3C, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "DAA":   {INH: 0x19, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "DECA":  {INH: 0x4A, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "DECB":  {INH: 0x5A, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "DEC":   {INH: IVLD, IMM: IVLD, DIR: 0x0A, IND: 0x6A, EXT: 0x7A},
    "EORA":  {INH: IVLD, IMM: 0x88, DIR: 0x98, IND: 0xA8, EXT: 0xB8},
    "EORB":  {INH: IVLD, IMM: 0xC8, DIR: 0xD8, IND: 0xE8, EXT: 0xF8},
    "EXG":   {INH: IVLD, IMM: 0x1E, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "INCA":  {INH: 0x4C, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "INCB":  {INH: 0x5C, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "INC":   {INH: IVLD, IMM: IVLD, DIR: 0x0C, IND: 0x6C, EXT: 0x7C},
    "JMP":   {INH: IVLD, IMM: IVLD, DIR: 0x0E, IND: 0x6E, EXT: 0x7E},
    "JSR":   {INH: IVLD, IMM: IVLD, DIR: 0x9D, IND: 0xAD, EXT: 0xBD},
    "LDA":   {INH: IVLD, IMM: 0x86, DIR: 0x96, IND: 0xA6, EXT: 0xB6},
    "LDB":   {INH: IVLD, IMM: 0xC6, DIR: 0xD6, IND: 0xE6, EXT: 0xF6},
    "LDD":   {INH: IVLD, IMM: 0xCC, DIR: 0xDC, IND: 0xEC, EXT: 0xFC},
    "LDS":   {INH: IVLD, IMM: 0x10CE, DIR: 0x10DE, IND: 0x10EE, EXT: 0x10FE},
    "LDU":   {INH: IVLD, IMM: 0xCE, DIR: 0xDE, IND: 0xEE, EXT: 0xFE},
    "LDX":   {INH: IVLD, IMM: 0x8E, DIR: 0x9E, IND: 0xAE, EXT: 0xBE},
    "LDY":   {INH: IVLD, IMM: 0x108E, DIR: 0x109E, IND: 0x10AE, EXT: 0x10BE},
    "LEAS":  {INH: IVLD, IMM: IVLD, DIR: IVLD, IND: 0x32, EXT: IVLD},
    "LEAU":  {INH: IVLD, IMM: IVLD, DIR: IVLD, IND: 0x33, EXT: IVLD},
    "LEAX":  {INH: IVLD, IMM: IVLD, DIR: IVLD, IND: 0x30, EXT: IVLD},
    "LEAY":  {INH: IVLD, IMM: IVLD, DIR: IVLD, IND: 0x31, EXT: IVLD},
    "LSLA":  {INH: 0x48, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "LSLB":  {INH: 0x58, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "LSL":   {INH: IVLD, IMM: IVLD, DIR: 0x08, IND: 0x68, EXT: 0x78},
    "LSRA":  {INH: 0x44, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "LSRB":  {INH: 0x54, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "LSR":   {INH: IVLD, IMM: IVLD, DIR: 0x04, IND: 0x64, EXT: 0x74},
    "MUL":   {INH: 0x3D, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "NEGA":  {INH: 0x40, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "NEGB":  {INH: 0x50, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "NEG":   {INH: IVLD, IMM: IVLD, DIR: 0x00, IND: 0x60, EXT: 0x70},
    "NOP":   {INH: 0x12, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ORA":   {INH: IVLD, IMM: 0x8A, DIR: 0x9A, IND: 0xAA, EXT: 0xBA},
    "ORB":   {INH: IVLD, IMM: 0xCA, DIR: 0xDA, IND: 0xEA, EXT: 0xFA},
    "ORCC":  {INH: IVLD, IMM: 0x1A, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "PSHS":  {INH: IVLD, IMM: 0x34, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "PSHU":  {INH: IVLD, IMM: 0x36, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "PULS":  {INH: IVLD, IMM: 0x35, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "PULU":  {INH: IVLD, IMM: 0x37, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ROLA":  {INH: 0x49, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ROLB":  {INH: 0x59, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ROL":   {INH: IVLD, IMM: IVLD, DIR: 0x09, IND: 0x69, EXT: 0x79},
    "RORA":  {INH: 0x46, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "RORB":  {INH: 0x56, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "ROR":   {INH: IVLD, IMM: IVLD, DIR: 0x06, IND: 0x66, EXT: 0x76},
    "RTI":   {INH: 0x3B, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "RTS":   {INH: 0x39, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "SBCA":  {INH: IVLD, IMM: 0x82, DIR: 0x92, IND: 0xA2, EXT: 0xB2},
    "SBCB":  {INH: IVLD, IMM: 0xC2, DIR: 0xD2, IND: 0xE2, EXT: 0xF2},
    "SEX":   {INH: 0x1D, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "STA":   {INH: IVLD, IMM: IVLD, DIR: 0x97, IND: 0xA7, EXT: 0xB7},
    "STB":   {INH: IVLD, IMM: IVLD, DIR: 0xD7, IND: 0xE7, EXT: 0xF7},
    "STD":   {INH: IVLD, IMM: IVLD, DIR: 0xDD, IND: 0xED, EXT: 0xFD},
    "STS":   {INH: IVLD, IMM: IVLD, DIR: 0x10DF, IND: 0x10EF, EXT: 0x10FF},
    "STU":   {INH: IVLD, IMM: IVLD, DIR: 0xDF, IND: 0xEF, EXT: 0xFF},
    "STX":   {INH: IVLD, IMM: IVLD, DIR: 0x9F, IND: 0xAF, EXT: 0xBF},
    "STY":   {INH: IVLD, IMM: IVLD, DIR: 0x109F, IND: 0x10AF, EXT: 0x10BF},
    "SUBA":  {INH: IVLD, IMM: 0x80, DIR: 0x90, IND: 0xA0, EXT: 0xB0},
    "SUBB":  {INH: IVLD, IMM: 0xC0, DIR: 0xD0, IND: 0xE0, EXT: 0xF0},
    "SUBD":  {INH: IVLD, IMM: 0x83, DIR: 0x93, IND: 0xA3, EXT: 0xB3},
    "SWI":   {INH: 0x3F, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "SWI2":  {INH: 0x103F, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "SWI3":  {INH: 0x113F, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "SYNC":  {INH: 0x13, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "TFR":   {INH: IVLD, IMM: 0x1F, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "TSTA":  {INH: 0x4D, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "TSTB":  {INH: 0x5D, IMM: IVLD, DIR: IVLD, IND: IVLD, EXT: IVLD},
    "TST":   {INH: IVLD, IMM: IVLD, DIR: 0x0D, IND: 0x6D, EXT: 0x7D},
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

# Pattern to parse a single line
ASM_LINE_REGEX = re.compile(
    "(?P<{0}>\\w*)\\s+(?P<{1}>\\w*)\\s+(?P<{2}>[\\w#\\$,\\+-]*)\\s+# (?P<{3}>.*)".format(LABEL, OP, OPERANDS, COMMENT))

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
        self.op_code = 0
        self.comments = ""
        self.size = 0
        self.address = 0
        self.data = None
        self.op = ""
        self.operands = None
        self.comment = ""
        self.mode = ""

    def __str__(self):
        if self.mode != INH and not self.is_pseudo_op():
            format_string = "{:04X} {:4X}   {:02X} {} {} {}  # {}" \
                if self.data < 255 else "{:04X} {:4X} {:04X} {} {} {}  # {}"
            return format_string.format(
                    self.address,
                    self.op_code,
                    self.data,
                    self.label.rjust(15, ' '),
                    self.op.rjust(5, ' '),
                    self.operands.rjust(15, ' '),
                    self.comment.ljust(40, ' '))

        if not self.is_pseudo_op():
            return "{:04X} {:04X} {} {} {} {}  # {}".format(
                    self.address,
                    self.op_code,
                    "".rjust(4, ' '),
                    self.label.rjust(15, ' '),
                    self.op.rjust(5, ' '),
                    self.operands.rjust(15, ' '),
                    self.comment.ljust(40, ' '))
        return ""

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

    def translate(self, symbol_table):
        """
        Translate the text into an actual op code.

        :param symbol_table: the current symbol table
        """
        if self.op in PSEUDO_OPERATIONS:
            return

        if self.op not in OPERATIONS:
            error = "Invalid mnemonic '{}'".format(self.op)
            raise TranslationError(error)

        self.set_addressing_mode()
        self.set_op_code()
        self.set_data(symbol_table)

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
        self.mode = EXT
        if not self.operands:
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
            error = "Invalid addressing mode ({}) for operation {}".format(
                        self.mode, self.op)
            raise TranslationError(error)
        self.size = 1 if self.op_code < 255 else 2

    def set_data(self, symbol_table):
        """
        Sets the data component of the statement. Translates the operands
        into useful data bytes.
        """
        self.data, size = self.get_hex_value(symbol_table)
        self.size += size

    def get_hex_value(self, symbol_table):
        """
        Returns the hex value of the operand, and the number of bytes used to
        represent the hex value. If the operand contains a symbol reference,
        attempts to look up that symbol in the symbol_table.
        """
        stripped_operand = self.operands
        stripped_operand = stripped_operand.replace("#", "")
        stripped_operand = stripped_operand.replace("$", "")
        if stripped_operand in symbol_table:
            hex_value = symbol_table[stripped_operand]
            return hex_value, 1 if hex_value < 256 else 2
        else:
            operand = self.operands
            if operand.startswith("#"):
                operand = operand.replace("#", "")

            if operand.startswith("$"):
                value = operand.replace("$", "")
                hex_value = int(value, 16)
                return hex_value, 1 if hex_value < 256 else 2
            else:
                value = operand
                hex_value = int(value, 10)
                return hex_value, 1 if hex_value < 256 else 2

    def is_empty(self):
        """
        Returns True if there is no label that is contained within the
        statement.
        """
        return self.op == ""

    def get_label(self):
        """
        Returns the label associated with this statement.
        """
        return self.label

    def set_address(self, address):
        """
        Sets the address for the statement.
        :param address: the new address for the statement
        """
        self.address = address

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
    address = 0x6000

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
            statement.translate(symbol_table)
        except TranslationError as error:
            throw_error(error, statement)
        if statement.is_pseudo_op():
            if statement.op == EQU:
                data, size = statement.get_hex_value(symbol_table)
                symbol_table[statement.get_label()] = data
        else:
            label = statement.get_label()
            if label:
                if label in symbol_table:
                    error = {"value": "label [" + label + "] redefined"}
                    throw_error(error, statement)
                symbol_table[label] = index

    # Pass 3: set the address for each operation
    for statement in statements:
        if not statement.is_pseudo_op():
            label = statement.get_label()
            if label:
                symbol_table[label] = address
        statement.set_address(address)
        address += statement.size

    # Check to see if the user wanted to print the symbol table
    if args.s:
        print("-- Symbol Table --")
        for symbol, value in symbol_table.iteritems():
            print("{} ${:4X}".format(symbol.ljust(15, ' '), value))

    # Check to see if the user wanted a print out of the assembly
    if args.p:
        print("-- Assembled Statements --")
        for statement in statements:
            if str(statement) != "":
                print(statement)

# M A I N #####################################################################

if __name__ == "__main__":
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
