"""
Copyright (C) 2019 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import re

# C O N S T A N T S ###########################################################

# Pattern to recognize a hex value
HEX_REGEX = re.compile(
    r"^\$(?P<value>[0-9a-fA-F]+)"
)

# Pattern to recognize an integer value
INT_REGEX = re.compile(
    r"^(?P<value>[\d]+)"
)

# F U N C T I O N S ###########################################################


def hex_value(value, size=2):
    return value_with_base_to_hex(value, size, 16)


def decimal_value(value, size=2):
    return value_with_base_to_hex(value, size, 10)


def value_with_base_to_hex(value, size, base):
    format_specifier = "{{:0>{}X}}".format(size)

    if not value:
        return ""

    if type(value) is int:
        return format_specifier.format(value)

    data = HEX_REGEX.match(value)
    if data:
        return format_specifier.format(int(data.group("value"), 16))

    data = INT_REGEX.match(value)
    if data:
        return format_specifier.format(int(data.group("value"), 10))

    try:
        return format_specifier.format(int(value, base))
    except ValueError:
        return value

# E N D   O F   F I L E #######################################################
