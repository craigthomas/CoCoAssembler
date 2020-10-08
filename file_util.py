"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import argparse
import sys

from cocoasm.virtualfiles.binary import BinaryFile
from cocoasm.virtualfiles.cassette import CassetteFile
from cocoasm.virtualfiles.disk import DiskFile

# F U N C T I O N S ###########################################################


def parse_arguments():
    """
    Parses the command-line arguments passed to the assembler.
    """
    parser = argparse.ArgumentParser(
        description="File listing and editing utility. See README.md for more "
        "information, and LICENSE for terms of use."
    )
    parser.add_argument(
        "host_filename", help="the host file to process (DSK, CAS, VDK, etc)"
    )
    parser.add_argument(
        "--append", action="store_true", help="append to host file if it already exists"
    )
    parser.add_argument(
        "--list", action="store_true", help="list all of the files on the specified host file"
    )
    parser.add_argument(
        "--to_bin", action="store_true", help="extracts all the files from the host file, and saves them as BIN files"
    )
    parser.add_argument(
        "--files", nargs="+", type=str, help="list of file names to extract"
    )
    return parser.parse_args()


def open_file(filename):
    """
    Attempts to open the specified filename. Will attempt to open it with all
    known file formats. Will return the opened file, or None if the file
    does not match any known types.

    :param filename: the name of the file to attempt to open
    :return: the opened host file or None
    """
    file = CassetteFile()
    file.open_host_file_for_read(filename)
    if file.is_correct_type():
        return file

    file = DiskFile()
    file.open_host_file_for_read(filename)
    if file.is_correct_type():
        return file

    return None


def main(args):
    """
    Runs the file utility with the specified arguments.

    :param args: the command-line arguments
    """
    host_file = open_file(args.host_filename)
    files_to_include = [x.upper() for x in args.files] if args.files else None
    if not host_file:
        print("Unable to determine file type for file [{}]".format(args.host_filename))
        sys.exit(1)

    if args.list:
        for number, file in enumerate(host_file.list_files()):
            print("-- File #{} --".format(number+1))
            print(file)
        sys.exit(0)

    if args.to_bin:
        for number, file in enumerate(host_file.list_files()):
            filename = file.name.strip().replace("\0", "")
            if files_to_include is None or filename in files_to_include:
                binary_file_name = "{}.bin".format(filename)
                print("-- File #{} [{}] --".format(number+1, filename))
                try:
                    binary_file = BinaryFile()
                    binary_file.open_host_file_for_write(binary_file_name, append=args.append)
                    binary_file.save_to_host_file(file)
                    binary_file.close_host_file()
                    print("Saved as {}".format(binary_file_name))
                except ValueError as error:
                    print("Unable to save binary file [{}]:".format(binary_file_name))
                    print(error)

# M A I N #####################################################################


if __name__ == '__main__':
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
