"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import argparse
import sys

from cocoasm.exceptions import TranslationError, ParseError, MacroError
from cocoasm.program import Program
from cocoasm.virtualfiles.virtual_file import VirtualFileType, VirtualFile
from cocoasm.virtualfiles.source_file import SourceFile, SourceFileType
from cocoasm.virtualfiles.coco_file import CoCoFile
from cocoasm.values import NumericValue

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
        "--print_length", metavar="LEN", help="truncates each assembly line printed to LEN characters",
        default=0, type=int,
    )
    parser.add_argument(
        "--to_bin", metavar="BIN_FILE", help="stores the assembled program in a binary BIN_FILE"
    )
    parser.add_argument(
        "--to_cas", metavar="CAS_FILE", help="stores the assembled program in a cassette image CAS_FILE"
    )
    parser.add_argument(
        "--to_dsk", metavar="DSK_FILE", help="stores the assembled program in a disk image DSK_FILE"
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


def throw_macro_error(error):
    """
    Prints out a macro related error.

    :param error: the error to print
    """
    print(error.value)
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
        program.process(source_file.get_buffer(), line_length=args.print_length)
    except TranslationError as error:
        throw_error(error)
    except ParseError as error:
        throw_error(error)
    except MacroError as error:
        throw_macro_error(error)

    coco_file = CoCoFile(
        name=program.name or args.name,
        load_addr=program.origin,
        exec_addr=program.exec_address,
        data=program.get_binary_array(),
        extension="bin",
        type=NumericValue(0x02),
        data_type=NumericValue(0x00),
    )

    if args.symbols:
        print("-- Symbol Table --")
        for symbol in program.get_symbol_table():
            print(symbol)

    if args.print:
        print("-- Assembled Statements --")
        for statement in program.get_statements():
            print(statement)

    if args.to_bin:
        try:
            virtual_file = VirtualFile(
                SourceFile(args.to_bin, file_type=SourceFileType.BINARY),
                VirtualFileType.BINARY
            )
            virtual_file.open_virtual_file()
            virtual_file.add_coco_file(coco_file)
            virtual_file.save_virtual_file(append_mode=args.append)
        except Exception as error:
            print("Unable to save binary file:")
            print(error)

    if args.to_cas:
        if not coco_file.name:
            print("No name for the program specified, not creating cassette file")
            return
        try:
            virtual_file = VirtualFile(
                SourceFile(args.to_cas, file_type=SourceFileType.BINARY),
                VirtualFileType.CASSETTE
            )
            virtual_file.open_virtual_file()
            virtual_file.add_coco_file(coco_file)
            virtual_file.save_virtual_file(append_mode=args.append)
        except Exception as error:
            print("Unable to save cassette file:")
            print(error)

    if args.to_dsk:
        if not coco_file.name:
            print("No name for the program specified, not creating disk file")
            return
        try:
            virtual_file = VirtualFile(
                SourceFile(args.to_dsk, file_type=SourceFileType.BINARY),
                VirtualFileType.DISK
            )
            virtual_file.open_virtual_file()
            virtual_file.add_coco_file(coco_file)
            virtual_file.save_virtual_file(append_mode=args.append)
        except Exception as error:
            print("Unable to save disk file:")
            print(error)

# M A I N #####################################################################


if __name__ == '__main__':
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
