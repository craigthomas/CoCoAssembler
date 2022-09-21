"""
Copyright (C) 2013-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import argparse
import sys

from cocoasm.virtualfiles.source_file import SourceFile, SourceFileType
from cocoasm.virtualfiles.virtual_file import VirtualFile, VirtualFileType

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
        "--to_cas", action="store_true", help="extracts all the files from the host file, and saves them as CAS files"
    )
    parser.add_argument(
        "--files", nargs="+", type=str, help="list of file names to extract"
    )
    return parser.parse_args()


def main(args):
    """
    Runs the file utility with the specified arguments.

    :param args: the command-line arguments
    """
    try:
        files_to_include = [x.upper() for x in args.files] if args.files else None
        virtual_file = VirtualFile(
            SourceFile(args.host_filename, file_type=SourceFileType.BINARY),
        )
        virtual_file.open_virtual_file()

        if args.list:
            for number, file in enumerate(virtual_file.list_files()):
                print("-- File #{} --".format(number + 1))
                print(file)
                print("")
            sys.exit(0)

        if args.to_cas:
            for number, file in enumerate(virtual_file.list_files()):
                filename = file.name.strip().replace("\0", "")
                if files_to_include is None or filename in files_to_include:
                    cas_file_name = "{}.cas".format(filename)
                    print("-- File #{} [{}] --".format(number + 1, filename))
                    target_virtual_file = VirtualFile(
                        SourceFile(cas_file_name, file_type=SourceFileType.BINARY),
                        virtual_file_type=VirtualFileType.CASSETTE
                    )
                    target_virtual_file.open_virtual_file()
                    target_virtual_file.add_coco_file(file)
                    target_virtual_file.save_virtual_file(append_mode=args.append)
                    print("Saved as {}".format(cas_file_name))

        if args.to_bin:
            for number, file in enumerate(virtual_file.list_files()):
                filename = file.name.strip().replace("\0", "")
                if files_to_include is None or filename in files_to_include:
                    bin_file_name = "{}.bin".format(filename)
                    print("-- File #{} [{}] --".format(number + 1, filename))
                    target_virtual_file = VirtualFile(
                        SourceFile(bin_file_name, file_type=SourceFileType.BINARY),
                        virtual_file_type=VirtualFileType.BINARY
                    )
                    target_virtual_file.open_virtual_file()
                    target_virtual_file.add_coco_file(file)
                    target_virtual_file.save_virtual_file(append_mode=args.append)
                    print("Saved as {}".format(bin_file_name))

    except Exception as error:
        raise Exception(error)


# M A I N #####################################################################


if __name__ == '__main__':
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
