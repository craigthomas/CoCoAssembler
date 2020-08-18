"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import argparse

from cocoasm.virtualfiles.cassette import CassetteFile

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
        "filename", help="the image file to process (DSK, CAS, VDK, etc)"
    )
    parser.add_argument(
        "--list", action="store_true", help="list all of the files on the specified image file"
    )
    return parser.parse_args()


def main(args):
    """
    Runs the file utility with the specified arguments.

    :param args: the command-line arguments
    """
    if args.list:
        file = CassetteFile()
        file.open_host_file_for_read(args.filename)
        if file.is_correct_type():
            print("-- Cassette File Contents --")
            files = file.list_files()
        else:
            print("[{}] is not a cassette file".format(args.filename))

# M A I N #####################################################################


if __name__ == '__main__':
    main(parse_arguments())

# E N D   O F   F I L E #######################################################
