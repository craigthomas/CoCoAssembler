"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import argparse
import sys

from cocoasm.exceptions import TranslationError, ParseError
from cocoasm.program import Program
from cocoasm.virtualfiles.virtual_file import VirtualFileType, VirtualFile
from cocoasm.virtualfiles.source_file import SourceFile, SourceFileType
from cocoasm.virtualfiles.coco_file import CoCoFile

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


def throw_error(error):
    """
    Prints out an error message.

    :param error: the error message to throw
    """
    print(error.value)
    print("{}".format(str(error.statement)))
    sys.exit(1)


def main(args):
    """
    Runs the assembler with the specified arguments.

    :param args: the command-line arguments
    """
    source_file = SourceFile(args.filename)
    source_file.read_file()
    program = Program()

    try:
        program.process(source_file.get_buffer())
    except TranslationError as error:
        throw_error(error)
    except ParseError as error:
        throw_error(error)

    coco_file = CoCoFile(
        name=program.name or args.name,
        load_addr=program.origin,
        exec_addr=program.origin,
        data=program.get_binary_array()
    )

    if args.symbols:
        print("-- Symbol Table --")
        for symbol in program.get_symbol_table():
            print(symbol)

    if args.print:
        print("-- Assembled Statements --")
        for statement in program.get_statements():
            print(statement)

    if args.bin_file:
        try:
            virtual_file = VirtualFile(
                SourceFile(args.bin_file, file_type=SourceFileType.BINARY),
                VirtualFileType.BINARY
            )
            virtual_file.open_virtual_file()
            virtual_file.add_coco_file(coco_file)
            virtual_file.save_virtual_file(append_mode=args.append)
        except Exception as error:
            print("Unable to save binary file:")
            print(error)

    if args.cas_file:
        if not coco_file.name:
            print("No name for the program specified, not creating cassette file")
            return
        try:
            virtual_file = VirtualFile(
                SourceFile(args.cas_file, file_type=SourceFileType.BINARY),
                VirtualFileType.CASSETTE
            )
            virtual_file.open_virtual_file()
            virtual_file.add_coco_file(coco_file)
            virtual_file.save_virtual_file(append_mode=args.append)
        except Exception as error:
            print("Unable to save cassette file:")
            print(error)

# M A I N #####################################################################


if __name__ == '__main__':
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
