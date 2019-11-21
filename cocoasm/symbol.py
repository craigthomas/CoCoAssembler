"""
Copyright (C) 2019 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from cocoasm.helpers import hex_value

# C L A S S E S  ##############################################################


class Symbol(object):
    def __init__(self, label, index):
        self.label = label
        self.index = index
        self.address = ""

    def __str__(self):
        return "{:04d} ${} {}".format(
            self.index,
            hex_value(self.address),
            self.label.upper()
        )

    def set_address(self, address):
        self.address = address

    def get_address(self):
        return self.address

# E N D   O F   F I L E #######################################################
