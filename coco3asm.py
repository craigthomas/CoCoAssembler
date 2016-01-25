"""
Copyright (C) 2012-2015 Craig Thomas
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

# Illegal addressing mode
ILLEGAL_MODE = 0x00

# Opcode translation based on addressing modes
OPERATIONS = {
    "ABX" : { INH: 0x3A, IMM: 0x00, DIR: 0x00, IND: 0x00, EXT: 0x00 },
    "ADCA": { INH: 0x00, IMM: 0x89, DIR: 0x99, IND: 0xA9, EXT: 0xB9 },
    "ADCB": { INH: 0x00, IMM: 0xC9, DIR: 0xD9, IND: 0xE9, EXT: 0xF9 },
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
    "ABX" : { INH: 0, IMM: 0, DIR: 0, IND: 0, EXT: 0 },
    "ADCA": { INH: 0, IMM: 1, DIR: 1, IND: 1, EXT: 2 },
    "ADCB": { INH: 0, IMM: 1, DIR: 1, IND: 1, EXT: 2 },
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
        self.opcode = ""
        self.comments = ""
        self.size = 0
        self.address = 0
        self.op = ""

    def __str__(self):
        return "{} {} {} {} {}  # {}".format(
                self.address[2:].upper().rjust(4, '0'),
                self.opcode.upper().rjust(4, '0'),
                self.label.rjust(15, ' '),
                self.op.rjust(5, ' '),
                self.operands.rjust(15, ' '),
                self.comment.ljust(40, ' '))

    def parse_line(self, line):
        """
        Parse a line of assembly language text.
        """
        data = ASM_LINE_REGEX.match(line)
        if data:
            self.label = data.group(LABEL)
            self.op = data.group(OP)
            self.operands = data.group(OPERANDS)
            self.comment = data.group(COMMENT)

    def translate(self):
        """
        Translate the text into an actual opcode.
        """
        if self.op in PSEUDO_OPERATIONS:
            return

        if self.op not in OPERATIONS:
            error = "Invalid mnemonic '{}'".format(self.op)
            raise TranslationError(error)

        operation = self.get_operation()
        self.opcode = operation[OP]
        if self.operands:
            operands = self.operands.split(",")

            if len(operands) != operation[OPERANDS]:
                error = "Expected {} operand(s), but got {}".format(
                    operation[OPERANDS], len(operands))
                raise TranslationError(error)

            counter = 0
            for operand_type in [SOURCE, TARGET, NUMERIC]:
                if operation[operand_type] != 0:
                    self.set_value(operand_type, operands[counter])
                    counter += 1

    def get_operation(self):
        """
        Returns the operation dictionary based upon the mnemonic.
        """
        if self.is_pseudo_op():
            return self.op
        return OPERATIONS[self.op]

# F U N C T I O N S ###########################################################

def parse_arguments():
    '''
    Parses the command-line arguments passed to the assembler.
    '''
    parser = argparse.ArgumentParser(description = "Assemble or disassmble "
        "machine language code for the COCO3. See README.md for more "
        "information, and LICENSE for terms of use.")
    parser.add_argument("filename", help = "the name of the file to examine")
    parser.add_argument("-s", action = "store_true", help = "print out the "
        "symbol table")
    parser.add_argument("-p", action = "store_true", help = "print out the "
        "assembled statements when finished")
    parser.add_argument("-o", metavar = "FILE", help = "stores the assembled "
        "program in FILE")
    return parser.parse_args()


def throw_error(error, statement):
    """
    Prints out an error message.

    @param error: the error message to throw
    @type error: Exception

    @param statement: the assembly statement that caused the error
    @type statement: Statement
    """
    print(error["value"])
    print("Line: " + str(statement))
    sys.exit(1)


def read_file(filename):
    '''
    Returns a list of all of the strings contained within the file called
    filename. Each string in the list represents one line of the file.

    @param filename: the name of the file to open
    @type filename: str

    @return: a list of strings read from the file
    @rtype: [ str ]
    '''
    return open(filename).readlines()


def parse_line(line):
    '''
    Parse a line of assembly language text, and return the parts referring
    to the label, the operation, the operand, and the comment. Returns a 
    dictionary with the following fields:

        label - the label applied to the line of code (for example, START)
        op - the operation (for example, ADCA, LDA)
        operand - the operand of the operation (for example, $4000)
        comment - the comment applied to the line

    If the line does not match the column format specified, return an empty
    dictionary.
    
    @param line: the line of code to parse
    @type line: str

    @return: a dictionary containing a breakdown of the line
    @rtype: dict
    '''
    result = dict()
    data = ASM_LINE_REGEX.match(line)
    if data:
        result[LABEL] = data.group(LABEL)
        result[OP] = data.group(OP)
        result[OPERANDS] = data.group(OPERANDS)
        result[COMMENT] = data.group(COMMENT)
    print(result)
    return result 


def translate_addressing_mode(statement):
    '''
    Based upon the operand, determine what the addressing mode should be.

    @param operand: the operand to check
    @type operand: str

    @return: the addressing mode associated with the operand
    @rtype: [ Inherent | Immediate | Direct | Indexed | Extended ]
    '''
    operand = statement[OPERANDS]
    if operand == "":
        return INH
    if operand.startswith("#"):
        return IMM
    if "," in operand:
        return IND
    if operand.startswith("<"):
        return DIR
    if operand.startswith(">"):
        return EXT
    return EXT


def translate_opcode(statement):
    '''
    Translate the opcode mnemonic into a machine language opcode. The
    translation examines the mode of the statement to figure out the
    correct opcode. Will exit with an error on an invalid opcode
    mnemonic, or if there is a problem translating the operand.

    @param statement: the assembly statement containing the operand to
        translate
    @type statement: dict

    @return: the machine language opcode translation of the mnemonic
    @rtype: int
    '''
    operation = statement[OP]
    mode = statement[MODE]

    if operation not in OPERATIONS:
        print("{}  {}  {}  {}".format(statement[LABEL], statement[OP],
           statement[OPERANDS], statement[COMMENT]))
        print("Error: invalid mnemonic '{}'".format(statement[OP]))
        sys.exit(1)
    
    if mode not in OPERATIONS[operation]:
        print("{}  {}  {}  {}".format(statement[LABEL], statement[OP],
           statement[OPERANDS], statement[COMMENT]))
        print("Error: syntax error in operand '{}'".format(statement[OPERANDS]))
        sys.exit(1)

    return OPERATIONS[operation][mode]


def is_pseudo_op(statement):
    '''
    Returns true if the assembly language statement is actually a pseudo op.

    @param statement: the assembly statement containing the operand to
        translate
    @type statement: dict

    @return: True if the statement is a pseudo op, False otherwise
    @rtype: boolean
    '''
    if statement[OP] in PSEUDO_OPERATIONS:
        return True
    return False


def get_hex_value(operand):
    ''' 
    Returns the hex value of the operand, and the number of bytes used to
    represent the hex value. If the operand contains a symbol reference,
    attempts to look up that symbol in the symbol_table.

    @param operand: the operand to decode
    @type operand: str

    @return: a tuple containing the hex value of the statement, and the
        number of bytes taken to store the statement
    @rtype: ( int, int )
    '''
    value = operand
    num_bytes = 0
    hex_value = 0x0

    if operand.startswith("$"):
        value = operand.replace("$", "")
        hex_value = int(value, 16) 
        if len(value) == 1 or len(value) == 2:
            num_bytes = 1
        if len(value) == 3 or len(value) == 4:
            num_bytes = 2
        return (hex_value, num_bytes)


def translate_operand(statement):
    '''
    Translate the operand into a hex value, and record the number of bytes
    taken to represent the operand. Result of the function is a tuple with
    the operand value (in hex), and the number of bytes for the operand.

    @param statement: the assembly statement containing the operand to
        translate
    @type statement: dict

    @return: a tuple containing the hex value of the statement, and the
        number of bytes taken to store the statement
    @rtype: ( int, int )
    '''
    mode = statement[MODE]
    operand = statement[OPERANDS]

    if mode == INH:
        return (0, 0) 

    if mode == IMM:
        operand = operand.replace("#", "")
        return get_hex_value(operand)

    if mode == EXT:
        operand = operand.replace(">", "")
        return get_hex_value(operand)
        

def translate(statement):
    '''
    '''
    if is_pseudo_op(statement):
        pass
    else:
        statement[MODE] = translate_addressing_mode(statement)
        statement[OPCODE] = translate_opcode(statement)
        statement[DATA] = translate_operand(statement)
    print('{}'.format(statement))


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
            

# M A I N #####################################################################

if __name__ == "__main__":
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
