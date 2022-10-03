"""
Copyright (C) 2013-2022 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from typing import NamedTuple

from cocoasm.values import Value, NoneValue


# C L A S S E S ###############################################################


class CoCoFile(NamedTuple):
    """
    A CoCoFile stores information relating to a file that should be stored on a
    VirtualFile's filesystem. It includes meta information such as the load point,
    execution point, the name, type, etc.
    """
    name: str = ""
    extension: str = ""
    type: Value = NoneValue()
    load_addr: Value = NoneValue()
    exec_addr: Value = NoneValue()
    data_type: Value = NoneValue()
    gaps: Value = NoneValue()
    ascii: int = 0
    data: list = []
    ignore_gaps: bool = False

    def __str__(self):
        result = "Filename:   {}\n".format(self.name)
        result += "Extension:  {}\n".format(self.extension)
        filetype = "BASIC"
        if self.type.hex() == "01":
            filetype = "Data"
        if self.type.hex() == "02":
            filetype = "Object"
        if self.type.hex() == "03":
            filetype = "Text"
        result += "File Type:  {}\n".format(filetype)

        data_type = "Binary"
        if self.data_type.hex() == "FF":
            data_type = "ASCII"
        result += "Data Type:  {}\n".format(data_type)

        if not self.ignore_gaps:
            gaps = "No Gaps"
            if self.gaps.hex() == "FF":
                gaps = "Gaps"
            result += "Gap Status: {}\n".format(gaps)

        if self.type.hex() == "02":
            result += "Load Addr:  ${}\n".format(self.load_addr.hex(size=4))
            result += "Exec Addr:  ${}\n".format(self.exec_addr.hex(size=4))

        result += "Data Len:   {} bytes".format(len(self.data))
        return result


# E N D   O F   F I L E #######################################################
