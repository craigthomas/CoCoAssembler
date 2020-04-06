"""
Copyright (C) 2019 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import argparse

from cocoasm.program import Program
from fileutil.virtualfiles import BinaryFile

# F U N C T I O N S ###########################################################


def parse_arguments():
    """
    Parses the command-line arguments passed to the assembler.
    """
    parser = argparse.ArgumentParser(
        description="Assembler for the Tandy Color Computer 1, 2, and 3. See README.md for more "
        "information, and LICENSE for terms of use."
    )
    parser.add_argument(
        "filename", help="the assembly language input file"
    )
    parser.add_argument(
        "--symbols", action="store_true", help="print out the symbol table"
    )
    parser.add_argument(
        "--print", action="store_true",
        help="print out the assembled statements when finished"
    )
    parser.add_argument(
        "--bin_file", metavar="BIN_FILE", help="stores the assembled program in a binary BIN_FILE"
    )
    parser.add_argument(
        "--cas_file", metavar="CAS_FILE", help="stores the assembled program in a cassette image CAS_FILE"
    )
    parser.add_argument(
        "--dsk_file", metavar="DSK_FILE", help="stores the assembled program in a disk image DSK_FILE"
    )
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

    if args.bin_file:
        binary_file = BinaryFile()
        binary_file.open_host_file(args.bin_file)
        binary_file.save_file(None, program.get_binary_array())
        binary_file.close_host_file()

# M A I N #####################################################################


if __name__ == '__main__':
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
