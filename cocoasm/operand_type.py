"""
Copyright (C) 2026 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from enum import Enum

# C L A S S E S ###############################################################


class OperandType(Enum):
    """
    The OperandType enumeration stores what kind of operand we have parsed.
    """
    UNKNOWN = 0
    INHERENT = 1
    IMMEDIATE = 2
    INDEXED = 3
    EXTENDED_INDIRECT = 4
    EXTENDED = 5
    EXPLICIT_EXTENDED = 6
    DIRECT = 7
    EXPLICIT_DIRECT = 8
    RELATIVE = 9
    SYMBOL = 10
    PSEUDO = 11
    SPECIAL = 12
    MACRO_SYMBOL = 13

# E N D   O F   F I L E #######################################################
