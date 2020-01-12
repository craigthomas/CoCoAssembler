"""
Copyright (C) 2019 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from typing import NamedTuple, Callable

# C O N S T A N T S ###########################################################

# Invalid operation
IVLD = 0x01

# Illegal addressing mode
ILLEGAL_MODE = 0x00

# Recognized register names
REGISTERS = ["A", "B", "D", "X", "Y", "U", "S", "CC", "DP", "PC"]


# C L A S S E S ###############################################################

class Mode(NamedTuple):
    """
    The Mode class represents a set of addressing modes. Modes supported by the 
    Color Computer are Inherent (inh), Immediate (imm), Direct (dir),
    Indexed (ind), Extended (ext), and Relative (rel). Each instruction may have
    one or more addressing modes (see Instruction class).
    """
    inh: int = IVLD
    imm: int = IVLD
    dir: int = IVLD
    ind: int = IVLD
    ext: int = IVLD
    rel: int = IVLD

    def supports_inherent(self):
        """
        Returns whether the addressing mode is an inherent mode.
        :return: True if the mode is inherent, false otherwise
        """
        return self.inh is not IVLD

    def supports_immediate(self):
        """
        Returns whether the addressing mode is immediate.
        :return: True if the mode is immediate, false otherwise
        """
        return self.imm is not IVLD

    def supports_direct(self):
        """
        Returns whether the addressing mode is direct.
        :return: True if the mode is direct, false otherwise
        """
        return self.dir is not IVLD

    def supports_indexed(self):
        """
        Returns whether the addressing mode is indexed.
        :return: True if the mode is indexed, false otherwise
        """
        return self.ind is not IVLD

    def supports_extended(self):
        """
        Returns whether the addressing mode is extended.
        :return: True if the mode is extended, false otherwise
        """
        return self.ext is not IVLD

    def supports_relative(self):
        """
        Returns whether the addressing mode is relative.

        :return: True if the mode is relative, false otherwise
        """
        return self.rel is not IVLD


class Instruction(NamedTuple):
    """
    The Instruction class represents an operation supported by the Color
    Computer. Each operation has a mnemonic that is the human
    understandable code for the operation, a set of addressing modes
    that the operation supports, whether the mnemonic is a pseudo 
    operation (i.e. only used by the assembler for special directives),
    is a branch instruction, and a function to assist with operation
    translation by the assembler.
    """
    mnemonic: str = ""
    mode: Mode = Mode()
    pseudo: bool = False
    is_branch: bool = False
    func: Callable[..., str] = None

    def is_branch_operation(self):
        """
        Returns whether the instruction is a branch instruction.
        :return: True if the instruction is a branch instruction, False otherwise
        """
        return self.is_branch

    def is_include(self):
        """
        Returns true if the pseudo operation is an INCLUDE directive,
        false otherwise.

        :return: True if the operation is an INCLUDE operation, False otherwise
        """
        return self.mnemonic == "INCLUDE"

    def is_pseudo(self):
        return self.mnemonic in ["FCC", "FCB", "FDB", "EQU", "INCLUDE", "END"]

    def is_special(self):
        return self.mnemonic in ["PULS", "PSHS", "EXG", "TFR"]

    def translate_pseudo(self, label, operand, symbol_table):
        """
        Translates a pseudo operation.

        :param label: the label attached to the pseudo operation
        :param operand: the operand value of the pseudo operation
        :param symbol_table: the current symbol table
        :return: returns the value of the pseudo operation
        """
        if self.mnemonic == "FCB":
            return operand.get_string_value()

        if self.mnemonic == "FDB":
            return operand.get_string_value()

        if self.mnemonic == "EQU":
            symbol_table[label].set_address(operand.get_string_value())

    def translate_special(self, operand):
        """
        Translates special non-pseudo operations.

        :param operand: the operand to process
        """
        post_byte = 0x0
        additional_byte = 0x0

        if self.mnemonic == "PSHS" or self.mnemonic == "PULS":
            registers = operand.get_string_value().split(",")
            for register in registers:
                if register not in REGISTERS:
                    raise ValueError("unknown register {}".format(register))

                post_byte |= 0x06 if register == "D" else 0x00
                post_byte |= 0x01 if register == "CC" else 0x00
                post_byte |= 0x02 if register == "A" else 0x00
                post_byte |= 0x04 if register == "B" else 0x00
                post_byte |= 0x08 if register == "DP" else 0x00
                post_byte |= 0x10 if register == "X" else 0x00
                post_byte |= 0x20 if register == "Y" else 0x00
                post_byte |= 0x40 if register == "U" else 0x00
                post_byte |= 0x80 if register == "PC" else 0x00
            return self.mode.imm, post_byte, additional_byte

        if self.mnemonic == "EXG" or self.mnemonic == "TFR":
            registers = operand.get_string_value().split(",")
            if len(registers) != 2:
                raise ValueError("{} requires exactly 2 registers".format(self.mnemonic))

            if registers[0] not in REGISTERS:
                raise ValueError("unknown register {}".format(registers[0]))

            if registers[1] not in REGISTERS:
                raise ValueError("unknown register {}".format(registers[1]))

            post_byte |= 0x00 if registers[0] == "D" else 0x00
            post_byte |= 0x00 if registers[1] == "D" else 0x00

            post_byte |= 0x10 if registers[0] == "X" else 0x00
            post_byte |= 0x01 if registers[1] == "X" else 0x00

            post_byte |= 0x20 if registers[0] == "Y" else 0x00
            post_byte |= 0x02 if registers[1] == "Y" else 0x00

            post_byte |= 0x30 if registers[0] == "U" else 0x00
            post_byte |= 0x03 if registers[1] == "U" else 0x00

            post_byte |= 0x40 if registers[0] == "S" else 0x00
            post_byte |= 0x04 if registers[1] == "S" else 0x00

            post_byte |= 0x50 if registers[0] == "PC" else 0x00
            post_byte |= 0x05 if registers[1] == "PC" else 0x00

            post_byte |= 0x80 if registers[0] == "A" else 0x00
            post_byte |= 0x08 if registers[1] == "A" else 0x00

            post_byte |= 0x90 if registers[0] == "B" else 0x00
            post_byte |= 0x09 if registers[1] == "B" else 0x00

            post_byte |= 0xA0 if registers[0] == "CC" else 0x00
            post_byte |= 0x0A if registers[1] == "CC" else 0x00

            post_byte |= 0xB0 if registers[0] == "DP" else 0x00
            post_byte |= 0x0B if registers[1] == "DP" else 0x00

            if post_byte not in [0x01, 0x10, 0x02, 0x20, 0x03, 0x30, 0x04, 0x40,
                                 0x05, 0x50, 0x12, 0x21, 0x13, 0x31, 0x14, 0x41,
                                 0x15, 0x51, 0x23, 0x32, 0x24, 0x42, 0x25, 0x52,
                                 0x34, 0x43, 0x35, 0x53, 0x45, 0x54, 0x89, 0x98,
                                 0x8A, 0xA8, 0x8B, 0xB8, 0x9A, 0xA9, 0x9B, 0xB9,
                                 0xAB, 0xBA, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55,
                                 0x88, 0x99, 0xAA, 0xBB]:
                raise ValueError("{} of {} to {} not allowed".format(self.mnemonic, registers[0], registers[1]))

            return self.mode.imm, post_byte, additional_byte

        return None


INSTRUCTIONS = [
    Instruction(mnemonic="ABX", mode=Mode(inh=0x3A)),
    Instruction(mnemonic="ADCA", mode=Mode(inh=0x00, imm=0x89, dir=0x99, ind=0xA9, ext=0xB9)),
    Instruction(mnemonic="ADCB", mode=Mode(inh=0x00, imm=0xC9, dir=0xD9, ind=0xE9, ext=0xF9)),
    Instruction(mnemonic="ADDA", mode=Mode(imm=0x8B, dir=0x9B, ind=0xAB, ext=0xBB)),
    Instruction(mnemonic="ADDB", mode=Mode(imm=0xCB, dir=0xDB, ind=0xEB, ext=0xFB)),
    Instruction(mnemonic="ADDD", mode=Mode(imm=0xC3, dir=0xD3, ind=0xE3, ext=0xF3)),
    Instruction(mnemonic="ANDA", mode=Mode(imm=0x84, dir=0x94, ind=0xA4, ext=0xB4)),
    Instruction(mnemonic="ANDB", mode=Mode(imm=0xC4, dir=0xD4, ind=0xE4, ext=0xF4)),
    Instruction(mnemonic="ANDCC", mode=Mode(imm=0x1C)),
    Instruction(mnemonic="ASLA", mode=Mode(inh=0x48)),
    Instruction(mnemonic="ASLB", mode=Mode(inh=0x58)),
    Instruction(mnemonic="ASL", mode=Mode(dir=0x08, ind=0x68, ext=0x78)),
    Instruction(mnemonic="ASRA", mode=Mode(inh=0x47)),
    Instruction(mnemonic="ASRB", mode=Mode(inh=0x57)),
    Instruction(mnemonic="ASR", mode=Mode(dir=0x07, ind=0x67, ext=0x77)),
    Instruction(mnemonic="BITA", mode=Mode(imm=0x85, dir=0x95, ind=0xA5, ext=0xB5)),
    Instruction(mnemonic="BITB", mode=Mode(imm=0xC5, dir=0xD5, ind=0xE5, ext=0xF5)),
    Instruction(mnemonic="CLRA", mode=Mode(inh=0x4F)),
    Instruction(mnemonic="CLRB", mode=Mode(inh=0x5F)),
    Instruction(mnemonic="CLR", mode=Mode(dir=0x0F, ind=0x6F, ext=0x7F)),
    Instruction(mnemonic="CMPA", mode=Mode(imm=0x81, dir=0x91, ind=0xA1, ext=0xB1)),
    Instruction(mnemonic="CMPB", mode=Mode(imm=0xC1, dir=0xD1, ind=0xE1, ext=0xF1)),
    Instruction(mnemonic="CMPX", mode=Mode(imm=0x8C, dir=0x9C, ind=0xAC, ext=0xBC)),
    Instruction(mnemonic="COMA", mode=Mode(inh=0x43)),
    Instruction(mnemonic="COMB", mode=Mode(inh=0x53)),
    Instruction(mnemonic="COM", mode=Mode(dir=0x03, ind=0x63, ext=0x73)),
    Instruction(mnemonic="CWAI", mode=Mode(imm=0x3C)),
    Instruction(mnemonic="DAA", mode=Mode(inh=0x19)),
    Instruction(mnemonic="DECA", mode=Mode(inh=0x4A)),
    Instruction(mnemonic="DECB", mode=Mode(inh=0x5A)),
    Instruction(mnemonic="DEC", mode=Mode(dir=0x0A, ind=0x6A, ext=0x7A)),
    Instruction(mnemonic="EORA", mode=Mode(imm=0x88, dir=0x98, ind=0xA8, ext=0xB8)),
    Instruction(mnemonic="EORB", mode=Mode(imm=0xC8, dir=0xD8, ind=0xE8, ext=0xF8)),
    Instruction(mnemonic="EXG", mode=Mode(imm=0x1E)),
    Instruction(mnemonic="INCA", mode=Mode(inh=0x4C)),
    Instruction(mnemonic="INCB", mode=Mode(inh=0x5C)),
    Instruction(mnemonic="INC", mode=Mode(dir=0x0C, ind=0x6C, ext=0x7C)),
    Instruction(mnemonic="JMP", mode=Mode(dir=0x0E, ind=0x6E, ext=0x7E)),
    Instruction(mnemonic="JSR", mode=Mode(dir=0x9D, ind=0xAD, ext=0xBD)),
    Instruction(mnemonic="LDA", mode=Mode(imm=0x86, dir=0x96, ind=0xA6, ext=0xB6)),
    Instruction(mnemonic="LDB", mode=Mode(imm=0xC6, dir=0xD6, ind=0xE6, ext=0xF6)),
    Instruction(mnemonic="LDD", mode=Mode(imm=0xCC, dir=0xDC, ind=0xEC, ext=0xFC)),
    Instruction(mnemonic="LDU", mode=Mode(imm=0xCE, dir=0xDE, ind=0xEE, ext=0xFE)),
    Instruction(mnemonic="LDX", mode=Mode(imm=0x8E, dir=0x9E, ind=0xAE, ext=0xBE)),
    Instruction(mnemonic="LEAS", mode=Mode(ind=0x32)),
    Instruction(mnemonic="LEAU", mode=Mode(ind=0x33)),
    Instruction(mnemonic="LEAX", mode=Mode(ind=0x30)),
    Instruction(mnemonic="LEAY", mode=Mode(ind=0x31)),
    Instruction(mnemonic="LSLA", mode=Mode(inh=0x48)),
    Instruction(mnemonic="LSLB", mode=Mode(inh=0x58)),
    Instruction(mnemonic="LSL", mode=Mode(dir=0x08, ind=0x68, ext=0x78)),
    Instruction(mnemonic="LSRA", mode=Mode(inh=0x44)),
    Instruction(mnemonic="LSRB", mode=Mode(inh=0x54)),
    Instruction(mnemonic="LSR", mode=Mode(dir=0x04, ind=0x64, ext=0x74)),
    Instruction(mnemonic="MUL", mode=Mode(inh=0x3D)),
    Instruction(mnemonic="NEGA", mode=Mode(inh=0x40)),
    Instruction(mnemonic="NEGB", mode=Mode(inh=0x50)),
    Instruction(mnemonic="NEG", mode=Mode(dir=0x00, ind=0x60, ext=0x70)),
    Instruction(mnemonic="NOP", mode=Mode(inh=0x12)),
    Instruction(mnemonic="ORA", mode=Mode(imm=0x8A, dir=0x9A, ind=0xAA, ext=0xBA)),
    Instruction(mnemonic="ORB", mode=Mode(imm=0xCA, dir=0xDA, ind=0xEA, ext=0xFA)),
    Instruction(mnemonic="ORCC", mode=Mode(imm=0x1A)),
    Instruction(mnemonic="PSHS", mode=Mode(imm=0x34)),
    Instruction(mnemonic="PSHU", mode=Mode(imm=0x36)),
    Instruction(mnemonic="PULS", mode=Mode(imm=0x35)),
    Instruction(mnemonic="PULU", mode=Mode(imm=0x37)),
    Instruction(mnemonic="ROLA", mode=Mode(inh=0x49)),
    Instruction(mnemonic="ROLB", mode=Mode(inh=0x59)),
    Instruction(mnemonic="ROL", mode=Mode(dir=0x09, ind=0x69, ext=0x79)),
    Instruction(mnemonic="RORA", mode=Mode(inh=0x46)),
    Instruction(mnemonic="RORB", mode=Mode(inh=0x56)),
    Instruction(mnemonic="ROR", mode=Mode(dir=0x06, ind=0x66, ext=0x76)),
    Instruction(mnemonic="RTI", mode=Mode(inh=0x3B)),
    Instruction(mnemonic="RTS", mode=Mode(inh=0x39)),
    Instruction(mnemonic="SBCA", mode=Mode(imm=0x82, dir=0x92, ind=0xA2, ext=0xB2)),
    Instruction(mnemonic="SBCB", mode=Mode(imm=0xC2, dir=0xD2, ind=0xE2, ext=0xF2)),
    Instruction(mnemonic="SEX", mode=Mode(inh=0x1D)),
    Instruction(mnemonic="STA", mode=Mode(dir=0x97, ind=0xA7, ext=0xB7)),
    Instruction(mnemonic="STB", mode=Mode(dir=0xD7, ind=0xE7, ext=0xF7)),
    Instruction(mnemonic="STD", mode=Mode(dir=0xDD, ind=0xED, ext=0xFD)),
    Instruction(mnemonic="STU", mode=Mode(dir=0xDF, ind=0xEF, ext=0xFF)),
    Instruction(mnemonic="STX", mode=Mode(dir=0x9F, ind=0xAF, ext=0xBF)),
    Instruction(mnemonic="SUBA", mode=Mode(imm=0x80, dir=0x90, ind=0xA0, ext=0xB0)),
    Instruction(mnemonic="SUBB", mode=Mode(imm=0xC0, dir=0xD0, ind=0xE0, ext=0xF0)),
    Instruction(mnemonic="SUBD", mode=Mode(imm=0x83, dir=0x93, ind=0xA3, ext=0xB3)),
    Instruction(mnemonic="SWI", mode=Mode(inh=0x3F)),
    Instruction(mnemonic="SYNC", mode=Mode(inh=0x13)),
    Instruction(mnemonic="TFR", mode=Mode(imm=0x1F)),
    Instruction(mnemonic="TSTA", mode=Mode(inh=0x4D)),
    Instruction(mnemonic="TSTB", mode=Mode(inh=0x5D)),
    Instruction(mnemonic="TST", mode=Mode(dir=0x0D, ind=0x6D, ext=0x7D)),

    # Extended operations
    Instruction(mnemonic="CMPD", mode=Mode(imm=0x1083, dir=0x1093, ind=0x10A3, ext=0x10B3)),
    Instruction(mnemonic="CMPS", mode=Mode(imm=0x118C, dir=0x119C, ind=0x11AC, ext=0x11BC)),
    Instruction(mnemonic="CMPU", mode=Mode(imm=0x1183, dir=0x1193, ind=0x11A3, ext=0x11B3)),
    Instruction(mnemonic="LDS", mode=Mode(imm=0x10CE, dir=0x10DE, ind=0x10EE, ext=0x10FE)),
    Instruction(mnemonic="CMPY", mode=Mode(imm=0x108C, dir=0x109C, ind=0x10AC, ext=0x10BC)),
    Instruction(mnemonic="LDY", mode=Mode(imm=0x108E, dir=0x109E, ind=0x10AE, ext=0x10BE)),
    Instruction(mnemonic="STS", mode=Mode(dir=0x10DF, ind=0x10EF, ext=0x10FF)),
    Instruction(mnemonic="STY", mode=Mode(dir=0x109F, ind=0x10AF, ext=0x10BF)),
    Instruction(mnemonic="SWI2", mode=Mode(inh=0x103F)),
    Instruction(mnemonic="SWI3", mode=Mode(inh=0x113F)),

    # Short branches
    Instruction(mnemonic="BCC", mode=Mode(rel=0x24), is_branch=True),
    Instruction(mnemonic="BCS", mode=Mode(rel=0x25), is_branch=True),
    Instruction(mnemonic="BEQ", mode=Mode(rel=0x27), is_branch=True),
    Instruction(mnemonic="BGE", mode=Mode(rel=0x2C), is_branch=True),
    Instruction(mnemonic="BGT", mode=Mode(rel=0x2E), is_branch=True),
    Instruction(mnemonic="BHI", mode=Mode(rel=0x22), is_branch=True),
    Instruction(mnemonic="BHS", mode=Mode(rel=0x24), is_branch=True),
    Instruction(mnemonic="BLE", mode=Mode(rel=0x2F), is_branch=True),
    Instruction(mnemonic="BLO", mode=Mode(rel=0x25), is_branch=True),
    Instruction(mnemonic="BLS", mode=Mode(rel=0x23), is_branch=True),
    Instruction(mnemonic="BLT", mode=Mode(rel=0x2D), is_branch=True),
    Instruction(mnemonic="BMI", mode=Mode(rel=0x2B), is_branch=True),
    Instruction(mnemonic="BNE", mode=Mode(rel=0x26), is_branch=True),
    Instruction(mnemonic="BPL", mode=Mode(rel=0x2A), is_branch=True),
    Instruction(mnemonic="BRA", mode=Mode(rel=0x20), is_branch=True),
    Instruction(mnemonic="BRN", mode=Mode(rel=0x21), is_branch=True),
    Instruction(mnemonic="BSR", mode=Mode(rel=0x8D), is_branch=True),
    Instruction(mnemonic="BVC", mode=Mode(rel=0x28), is_branch=True),
    Instruction(mnemonic="BVS", mode=Mode(rel=0x29), is_branch=True),

    # Long branches
    Instruction(mnemonic="LBCC", mode=Mode(rel=0x1024), is_branch=True),
    Instruction(mnemonic="LBCS", mode=Mode(rel=0x1025), is_branch=True),
    Instruction(mnemonic="LBEQ", mode=Mode(rel=0x1027), is_branch=True),
    Instruction(mnemonic="LBGE", mode=Mode(rel=0x102C), is_branch=True),
    Instruction(mnemonic="LBGT", mode=Mode(rel=0x102E), is_branch=True),
    Instruction(mnemonic="LBHI", mode=Mode(rel=0x1022), is_branch=True),
    Instruction(mnemonic="LBHS", mode=Mode(rel=0x1024), is_branch=True),
    Instruction(mnemonic="LBLE", mode=Mode(rel=0x102F), is_branch=True),
    Instruction(mnemonic="LBLO", mode=Mode(rel=0x1025), is_branch=True),
    Instruction(mnemonic="LBLS", mode=Mode(rel=0x1023), is_branch=True),
    Instruction(mnemonic="LBLT", mode=Mode(rel=0x102D), is_branch=True),
    Instruction(mnemonic="LBMI", mode=Mode(rel=0x102B), is_branch=True),
    Instruction(mnemonic="LBNE", mode=Mode(rel=0x1026), is_branch=True),
    Instruction(mnemonic="LBPL", mode=Mode(rel=0x102A), is_branch=True),
    Instruction(mnemonic="LBRA", mode=Mode(rel=0x1020), is_branch=True),
    Instruction(mnemonic="LBRN", mode=Mode(rel=0x1021), is_branch=True),
    Instruction(mnemonic="LBSR", mode=Mode(rel=0x17), is_branch=True),
    Instruction(mnemonic="LBVC", mode=Mode(rel=0x1028), is_branch=True),
    Instruction(mnemonic="LBVS", mode=Mode(rel=0x1029), is_branch=True),

    # Pseudo operations
    Instruction(mnemonic="END", pseudo=True),
    Instruction(mnemonic="ORG", pseudo=True),
    Instruction(mnemonic="EQU", pseudo=True),
    Instruction(mnemonic="SET", pseudo=True),
    Instruction(mnemonic="RMB", pseudo=True),
    Instruction(mnemonic="FCB", pseudo=True),
    Instruction(mnemonic="FDB", pseudo=True),
    Instruction(mnemonic="FCC", pseudo=True),
    Instruction(mnemonic="SETDP", pseudo=True),
    Instruction(mnemonic="INCLUDE", pseudo=True)
]

# E N D   O F   F I L E #######################################################
