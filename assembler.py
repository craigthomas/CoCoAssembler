"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import argparse

from cocoasm.program import Program
from cocoasm.virtualfiles.virtualfile import CoCoFile
from cocoasm.virtualfiles.binary import BinaryFile
from cocoasm.virtualfiles.cassette import CassetteFile

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
    parser.add_argument(
        "--name", help="the name of the file to be created on the cassette or disk image"
    )
    parser.add_argument(
        "--append", action="store_true", help="appends to an existing cassette or disk file if it exists"
    )
    parser.add_argument(
        "--width", metavar="N", help="the width of the console for printing results (default=100)",
        default=100, type=int,
    )
    return parser.parse_args()


def main(args):
    """
    Runs the assembler with the specified arguments.

    :param args: the command-line arguments
    """
    program = Program(width=args.width)
    program.process(args.filename)
    coco_file = CoCoFile(
        name=program.name or args.name,
        load_addr=program.origin,
        exec_addr=program.origin,
        data=program.get_binary_array()
    )

    if args.symbols:
        program.print_symbol_table()

    if args.print:
        program.print_statements()

    if args.bin_file:
        try:
            binary_file = BinaryFile()
            binary_file.open_host_file_for_write(args.bin_file, append=args.append)
            binary_file.save_to_host_file(coco_file)
            binary_file.close_host_file()
        except ValueError as error:
            print("Unable to save binary file:")
            print(error)

    if args.cas_file:
        if not coco_file.name:
            print("No name for the program specified, not creating cassette file")
            return
        try:
            cas_file = CassetteFile()
            cas_file.open_host_file_for_write(args.cas_file, append=args.append)
            cas_file.save_to_host_file(coco_file)
            cas_file.close_host_file()
        except ValueError as error:
            print("Unable to save cassette file:")
            print(error)

# M A I N #####################################################################


if __name__ == '__main__':
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
