"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from abc import ABC
from enum import Enum

# C L A S S E S  ##############################################################


class SymbolType(Enum):
    UNKNOWN = 0
    ADDRESS = 1
    VALUE = 2


class Symbol(ABC):
    def __init__(self, value):
        self.type = SymbolType.UNKNOWN
        self.value = value

    def __str__(self):
        return self.value

    def is_type(self, symbol_type):
        return self.type == symbol_type


class AddressSymbol(Symbol):
    def __init__(self, value):
        super().__init__(value)
        self.type = SymbolType.ADDRESS


class ValueSymbol(Symbol):
    def __init__(self, value):
        super().__init__(value)
        self.type = SymbolType.VALUE

# E N D   O F   F I L E #######################################################
