"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from typing import NamedTuple

# C L A S S E S ###############################################################


class AssemblerState(NamedTuple):
    origin: int = 0x0
    direct_page: int = 0x0

# E N D  O F  F I L E #########################################################
