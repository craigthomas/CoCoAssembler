"""
Copyright (C) 2019 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import argparse

from cocoasm.program import Program

# F U N C T I O N S ###########################################################


def parse_arguments():
    """
    Parses the command-line arguments passed to the assembler.
    """
    parser = argparse.ArgumentParser(
        description="Assembler for the Tandy Color Computer 1, 2, and 3. See README.md for more "
        "information, and LICENSE for terms of use."
    )
    parser.add_argument("filename", help="the input file")
    parser.add_argument(
        "--symbols", action="store_true", help="print out the symbol table"
    )
    parser.add_argument(
        "--print", action="store_true",
        help="print out the assembled statements when finished"
    )
    parser.add_argument(
        "--output", metavar="FILE", help="stores the assembled program in FILE")
    return parser.parse_args()


def main(args):
    """
    Runs the assembler with the specified arguments.

    :param args: the command-line arguments
    """
    program = Program(args.filename)

    if args.symbols:
        program.print_symbol_table()

    if args.print:
        program.print_statements()

    if args.output:
        program.save_binary_file(args.output)


main(parse_arguments())

# E N D   O F   F I L E #######################################################
