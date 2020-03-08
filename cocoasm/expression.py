"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

# C O N S T A N T S ###########################################################

# Patten to recognize an expression
EXPR_REGEX = re.compile(
    r"^(?P<left>[\d\w]+)(?P<operation>[\+\-\/\*])(?P<right>[\d\w]+)"
)

# C L A S S E S  ##############################################################


class Expression(object):
    """
    Represents an expression that occurs between two values.
    """
    def __init__(self, expression):
        self.left = None
        self.right = None
        self.operation = None
        self.parse_expression(expression)

    def parse_expression(self, expression):
        match = EXPR_REGEX.match(expression)
        if not match:
            raise ValueError("invalid expression")
        self.left = match.group("left")
        self.right = match.group("right")
        self.operation = match.group("operation")

# E N D   O F   F I L E #######################################################
