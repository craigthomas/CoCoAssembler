"""
Copyright (C) 2019-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

import unittest

from cocoasm.exceptions import TranslationError, ParseError

# C L A S S E S ###############################################################


class TestTranslationError(unittest.TestCase):
    """
    A test class for the TranslationError class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_str_representation_correct(self):
        result = TranslationError("test", "statement")
        self.assertEqual("'test'", str(result))


class TestParseError(unittest.TestCase):
    """
    A test class for the ParseError class.
    """
    def setUp(self):
        """
        Common setup routines needed for all unit tests.
        """
        pass

    def test_str_representation_correct(self):
        result = ParseError("test", "statement")
        self.assertEqual("'test'", str(result))

# M A I N #####################################################################


if __name__ == '__main__':
    unittest.main()

# E N D   O F   F I L E #######################################################
