'''
Copyright (C) 2012 Craig Thomas
This project uses an MIT style license - see LICENSE for details.

A Color Computer 3 assembler - see the README.md file for details.
'''
# I M P O R T S ###############################################################

import argparse
import re

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
OPERAND = "operand"
COMMENT = "comment"

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
PSEUDO_OPERATIONS = [ END, ORG, EQU, SET, RMB, FCB, FDB, FCC, INCLUDE ]

# Opcode operand requirements based on addressing modes
OPERAND_COUNTS = {
    "ABX" : { INH: 0, IMM: 0, DIR: 0, IND: 0, EXT: 0 },
    "ADCA": { INH: 0, IMM: 1, DIR: 1, IND: 1, EXT: 2 },
    "ADCB": { INH: 0, IMM: 1, DIR: 1, IND: 1, EXT: 2 },
}

# Pattern to parse a single line
ASM_LINE_REGEX = re.compile("(?P<label>\w*)\s+(?P<op>\w*)\s+"
    "(?P<operand>[\w#\$,\+-]*)\s+(?P<comment>.*)")

# F U N C T I O N S ###########################################################

def parse_arguments():
    '''
    Parses the command-line arguments passed to the assembler.
    '''
    parser = argparse.ArgumentParser(description = "Assemble or disassmble "
        "machine language code for the Color Computer 3. See README.md for "
        "more information, and LICENSE for terms of use.")
    parser.add_argument("filename", help = "the name of the file to examine")
    parser.add_argument("-s", action = "store_true", help = "print out the " 
        "symbol table")
    return parser.parse_args()


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
        result[OPERAND] = data.group(OPERAND)
        result[COMMENT] = data.group(COMMENT)
    return result 


def get_addressing_mode(operand):
    '''
    Based upon the operand, determine what the addressing mode should be.

    @param operand: the operand to check
    @type operand: str

    @return: the addressing mode associated with the operand
    @rtype: [ Inherent | Immediate | Direct | Indexed | Extended ]
    '''
    if operand == "":
        return INHERENT
    if operand.startswith("#"):
        return IMMEDIATE
    if "," in operand:
        return INDEXED
    if operand.startswith("<"):
        return DIRECT
    if operand.startswith(">"):
        return EXTENDED


def main(args):
    '''
    Runs the assembler with the specified arguments.
    '''
    lines = read_file(args.filename)
    for line in lines:
        result = parse_line(line)
        print(result)

# M A I N #####################################################################

if __name__ == "__main__":
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
