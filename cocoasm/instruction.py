"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from typing import NamedTuple

from cocoasm.values import NoneValue


# C L A S S E S ###############################################################

class CodePackage(object):
    def __init__(self, op_code=NoneValue(), address=NoneValue(), post_byte=NoneValue(), additional=NoneValue(), size=0, additional_needs_resolution=False):
        self.op_code = op_code
        self.address = address
        self.post_byte = post_byte
        self.additional = additional
        self.size = size
        self.additional_needs_resolution = additional_needs_resolution


class Mode(NamedTuple):
    """
    The Mode class represents a set of addressing modes. Modes supported by the 
    Color Computer are Inherent (inh), Immediate (imm), Direct (dir),
    Indexed (ind), Extended (ext), and Relative (rel). Each instruction may have
    one or more addressing modes (see Instruction class).
    """
    inh: int = None
    inh_sz: int = 0
    imm: int = None
    imm_sz: int = 0
    dir: int = None
    dir_sz: int = 0
    ind: int = None
    ind_sz: int = 0
    ext: int = None
    ext_sz: int = 0
    rel: int = None
    rel_sz: int = 0


class Instruction(NamedTuple):
    """
    The Instruction class represents an operation supported by the Color
    Computer. Each operation has a mnemonic that is the human
    understandable code for the operation, a set of addressing modes
    that the operation supports, whether the mnemonic is a pseudo 
    operation (i.e. only used by the assembler for special directives),
    is a branch instruction, as well as other attributes used for
    translation and parsing.
    """
    mnemonic: str = ""
    mode: Mode = Mode()
    is_pseudo: bool = False
    is_pseudo_define: bool = False
    is_string_define: bool = False
    is_special: bool = False
    is_include: bool = False
    is_short_branch: bool = False
    is_long_branch: bool = False
    is_origin: bool = False
    is_name: bool = False


INSTRUCTIONS = [
    Instruction(mnemonic="ABX", mode=Mode(inh=0x3A, inh_sz=1)),
    Instruction(mnemonic="ADCA", mode=Mode(imm=0x89, imm_sz=2, dir=0x99, dir_sz=2, ind=0xA9, ind_sz=2, ext=0xB9, ext_sz=3)),
    Instruction(mnemonic="ADCB", mode=Mode(imm=0xC9, imm_sz=2, dir=0xD9, dir_sz=2, ind=0xE9, ind_sz=2, ext=0xF9, ext_sz=3)),
    Instruction(mnemonic="ADDA", mode=Mode(imm=0x8B, imm_sz=2, dir=0x9B, dir_sz=2, ind=0xAB, ind_sz=2, ext=0xBB, ext_sz=3)),
    Instruction(mnemonic="ADDB", mode=Mode(imm=0xCB, imm_sz=2, dir=0xDB, dir_sz=2, ind=0xEB, ind_sz=2, ext=0xFB, ext_sz=3)),
    Instruction(mnemonic="ADDD", mode=Mode(imm=0xC3, imm_sz=3, dir=0xD3, dir_sz=2, ind=0xE3, ind_sz=2, ext=0xF3, ext_sz=3)),
    Instruction(mnemonic="ANDA", mode=Mode(imm=0x84, imm_sz=2, dir=0x94, dir_sz=2, ind=0xA4, ind_sz=2, ext=0xB4, ext_sz=3)),
    Instruction(mnemonic="ANDB", mode=Mode(imm=0xC4, imm_sz=2, dir=0xD4, dir_sz=2, ind=0xE4, ind_sz=2, ext=0xF4, ext_sz=3)),
    Instruction(mnemonic="ANDCC", mode=Mode(imm=0x1C, imm_sz=2)),
    Instruction(mnemonic="ASLA", mode=Mode(inh=0x48, inh_sz=1)),
    Instruction(mnemonic="ASLB", mode=Mode(inh=0x58, inh_sz=1)),
    Instruction(mnemonic="ASL", mode=Mode(dir=0x08, dir_sz=2, ind=0x68, ind_sz=2, ext=0x78, ext_sz=3)),
    Instruction(mnemonic="ASRA", mode=Mode(inh=0x47, inh_sz=1)),
    Instruction(mnemonic="ASRB", mode=Mode(inh=0x57, inh_sz=1)),
    Instruction(mnemonic="ASR", mode=Mode(dir=0x07, dir_sz=2, ind=0x67, ind_sz=2, ext=0x77, ext_sz=3)),
    Instruction(mnemonic="BITA", mode=Mode(imm=0x85, imm_sz=2, dir=0x95, dir_sz=2, ind=0xA5, ind_sz=2, ext=0xB5, ext_sz=3)),
    Instruction(mnemonic="BITB", mode=Mode(imm=0xC5, imm_sz=2, dir=0xD5, dir_sz=2, ind=0xE5, ind_sz=2, ext=0xF5, ext_sz=3)),
    Instruction(mnemonic="CLRA", mode=Mode(inh=0x4F, inh_sz=1)),
    Instruction(mnemonic="CLRB", mode=Mode(inh=0x5F, inh_sz=1)),
    Instruction(mnemonic="CLR", mode=Mode(dir=0x0F, dir_sz=2, ind=0x6F, ind_sz=2, ext=0x7F, ext_sz=3)),
    Instruction(mnemonic="CMPA", mode=Mode(imm=0x81, imm_sz=2, dir=0x91, dir_sz=2, ind=0xA1, ind_sz=2, ext=0xB1, ext_sz=3)),
    Instruction(mnemonic="CMPB", mode=Mode(imm=0xC1, imm_sz=2, dir=0xD1, dir_sz=2, ind=0xE1, ind_sz=2, ext=0xF1, ext_sz=3)),
    Instruction(mnemonic="CMPX", mode=Mode(imm=0x8C, imm_sz=3, dir=0x9C, dir_sz=2, ind=0xAC, ind_sz=2, ext=0xBC, ext_sz=3)),
    Instruction(mnemonic="COMA", mode=Mode(inh=0x43, inh_sz=1)),
    Instruction(mnemonic="COMB", mode=Mode(inh=0x53, inh_sz=1)),
    Instruction(mnemonic="COM", mode=Mode(dir=0x03, dir_sz=2, ind=0x63, ind_sz=2, ext=0x73, ext_sz=3)),
    Instruction(mnemonic="CWAI", mode=Mode(imm=0x3C, imm_sz=2)),
    Instruction(mnemonic="DAA", mode=Mode(inh=0x19, inh_sz=1)),
    Instruction(mnemonic="DECA", mode=Mode(inh=0x4A, inh_sz=1)),
    Instruction(mnemonic="DECB", mode=Mode(inh=0x5A, inh_sz=1)),
    Instruction(mnemonic="DEC", mode=Mode(dir=0x0A, dir_sz=2, ind=0x6A, ind_sz=2, ext=0x7A, ext_sz=3)),
    Instruction(mnemonic="EORA", mode=Mode(imm=0x88, imm_sz=2, dir=0x98, dir_sz=2, ind=0xA8, ind_sz=2, ext=0xB8, ext_sz=3)),
    Instruction(mnemonic="EORB", mode=Mode(imm=0xC8, imm_sz=2, dir=0xD8, dir_sz=2, ind=0xE8, ind_sz=2, ext=0xF8, ext_sz=3)),
    Instruction(mnemonic="EXG", mode=Mode(imm=0x1E, imm_sz=2), is_special=True),
    Instruction(mnemonic="INCA", mode=Mode(inh=0x4C, inh_sz=1)),
    Instruction(mnemonic="INCB", mode=Mode(inh=0x5C, inh_sz=1)),
    Instruction(mnemonic="INC", mode=Mode(dir=0x0C, dir_sz=2, ind=0x6C, ind_sz=2, ext=0x7C, ext_sz=3)),
    Instruction(mnemonic="JMP", mode=Mode(dir=0x0E, dir_sz=2, ind=0x6E, ind_sz=2, ext=0x7E, ext_sz=3)),
    Instruction(mnemonic="JSR", mode=Mode(dir=0x9D, dir_sz=2, ind=0xAD, ind_sz=2, ext=0xBD, ext_sz=3)),
    Instruction(mnemonic="LDA", mode=Mode(imm=0x86, imm_sz=2, dir=0x96, dir_sz=2, ind=0xA6, ind_sz=2, ext=0xB6, ext_sz=3)),
    Instruction(mnemonic="LDB", mode=Mode(imm=0xC6, imm_sz=2, dir=0xD6, dir_sz=2, ind=0xE6, ind_sz=2, ext=0xF6, ext_sz=3)),
    Instruction(mnemonic="LDD", mode=Mode(imm=0xCC, imm_sz=3, dir=0xDC, dir_sz=2, ind=0xEC, ind_sz=2, ext=0xFC, ext_sz=3)),
    Instruction(mnemonic="LDU", mode=Mode(imm=0xCE, imm_sz=3, dir=0xDE, dir_sz=2, ind=0xEE, ind_sz=2, ext=0xFE, ext_sz=3)),
    Instruction(mnemonic="LDX", mode=Mode(imm=0x8E, imm_sz=3, dir=0x9E, dir_sz=2, ind=0xAE, ind_sz=2, ext=0xBE, ext_sz=3)),
    Instruction(mnemonic="LEAS", mode=Mode(ind=0x32, ind_sz=2)),
    Instruction(mnemonic="LEAU", mode=Mode(ind=0x33, ind_sz=2)),
    Instruction(mnemonic="LEAX", mode=Mode(ind=0x30, ind_sz=2)),
    Instruction(mnemonic="LEAY", mode=Mode(ind=0x31, ind_sz=2)),
    Instruction(mnemonic="LSLA", mode=Mode(inh=0x48, inh_sz=1)),
    Instruction(mnemonic="LSLB", mode=Mode(inh=0x58, inh_sz=1)),
    Instruction(mnemonic="LSL", mode=Mode(dir=0x08, dir_sz=2, ind=0x68, ind_sz=2, ext=0x78, ext_sz=3)),
    Instruction(mnemonic="LSRA", mode=Mode(inh=0x44, inh_sz=1)),
    Instruction(mnemonic="LSRB", mode=Mode(inh=0x54, inh_sz=1)),
    Instruction(mnemonic="LSR", mode=Mode(dir=0x04, dir_sz=2, ind=0x64, ind_sz=2, ext=0x74, ext_sz=3)),
    Instruction(mnemonic="MUL", mode=Mode(inh=0x3D, inh_sz=1)),
    Instruction(mnemonic="NEGA", mode=Mode(inh=0x40, inh_sz=1)),
    Instruction(mnemonic="NEGB", mode=Mode(inh=0x50, inh_sz=1)),
    Instruction(mnemonic="NEG", mode=Mode(dir=0x00, dir_sz=2, ind=0x60, ind_sz=2, ext=0x70, ext_sz=3)),
    Instruction(mnemonic="NOP", mode=Mode(inh=0x12, inh_sz=1)),
    Instruction(mnemonic="ORA", mode=Mode(imm=0x8A, imm_sz=2, dir=0x9A, dir_sz=2, ind=0xAA, ind_sz=2, ext=0xBA, ext_sz=3)),
    Instruction(mnemonic="ORB", mode=Mode(imm=0xCA, imm_sz=2, dir=0xDA, dir_sz=2, ind=0xEA, ind_sz=2, ext=0xFA, ext_sz=3)),
    Instruction(mnemonic="ORCC", mode=Mode(imm=0x1A, imm_sz=2)),
    Instruction(mnemonic="PSHS", mode=Mode(imm=0x34, imm_sz=2), is_special=True),
    Instruction(mnemonic="PSHU", mode=Mode(imm=0x36, imm_sz=2)),
    Instruction(mnemonic="PULS", mode=Mode(imm=0x35, imm_sz=2), is_special=True),
    Instruction(mnemonic="PULU", mode=Mode(imm=0x37, imm_sz=2)),
    Instruction(mnemonic="ROLA", mode=Mode(inh=0x49, inh_sz=1)),
    Instruction(mnemonic="ROLB", mode=Mode(inh=0x59, inh_sz=1)),
    Instruction(mnemonic="ROL", mode=Mode(dir=0x09, dir_sz=2, ind=0x69, ind_sz=2, ext=0x79, ext_sz=3)),
    Instruction(mnemonic="RORA", mode=Mode(inh=0x46, inh_sz=1)),
    Instruction(mnemonic="RORB", mode=Mode(inh=0x56, inh_sz=1)),
    Instruction(mnemonic="ROR", mode=Mode(dir=0x06, dir_sz=2, ind=0x66, ind_sz=2, ext=0x76, ext_sz=3)),
    Instruction(mnemonic="RTI", mode=Mode(inh=0x3B, inh_sz=1)),
    Instruction(mnemonic="RTS", mode=Mode(inh=0x39, inh_sz=1)),
    Instruction(mnemonic="SBCA", mode=Mode(imm=0x82, imm_sz=2, dir=0x92, dir_sz=2, ind=0xA2, ind_sz=2, ext=0xB2, ext_sz=3)),
    Instruction(mnemonic="SBCB", mode=Mode(imm=0xC2, imm_sz=2, dir=0xD2, dir_sz=2, ind=0xE2, ind_sz=2, ext=0xF2, ext_sz=3)),
    Instruction(mnemonic="SEX", mode=Mode(inh=0x1D, inh_sz=1)),
    Instruction(mnemonic="STA", mode=Mode(dir=0x97, dir_sz=2, ind=0xA7, ind_sz=2, ext=0xB7, ext_sz=3)),
    Instruction(mnemonic="STB", mode=Mode(dir=0xD7, dir_sz=2, ind=0xE7, ind_sz=2, ext=0xF7, ext_sz=3)),
    Instruction(mnemonic="STD", mode=Mode(dir=0xDD, dir_sz=2, ind=0xED, ind_sz=2, ext=0xFD, ext_sz=3)),
    Instruction(mnemonic="STU", mode=Mode(dir=0xDF, dir_sz=2, ind=0xEF, ind_sz=2, ext=0xFF, ext_sz=3)),
    Instruction(mnemonic="STX", mode=Mode(dir=0x9F, dir_sz=2, ind=0xAF, ind_sz=2, ext=0xBF, ext_sz=3)),
    Instruction(mnemonic="SUBA", mode=Mode(imm=0x80, imm_sz=2, dir=0x90, dir_sz=2, ind=0xA0, ind_sz=2, ext=0xB0, ext_sz=3)),
    Instruction(mnemonic="SUBB", mode=Mode(imm=0xC0, imm_sz=2, dir=0xD0, dir_sz=2, ind=0xE0, ind_sz=2, ext=0xF0, ext_sz=3)),
    Instruction(mnemonic="SUBD", mode=Mode(imm=0x83, imm_sz=3, dir=0x93, dir_sz=2, ind=0xA3, ind_sz=2, ext=0xB3, ext_sz=3)),
    Instruction(mnemonic="SWI", mode=Mode(inh=0x3F, imm_sz=1)),
    Instruction(mnemonic="SYNC", mode=Mode(inh=0x13, imm_sz=1)),
    Instruction(mnemonic="TFR", mode=Mode(imm=0x1F, imm_sz=2), is_special=True),
    Instruction(mnemonic="TSTA", mode=Mode(inh=0x4D, inh_sz=1)),
    Instruction(mnemonic="TSTB", mode=Mode(inh=0x5D, inh_sz=1)),
    Instruction(mnemonic="TST", mode=Mode(dir=0x0D, dir_sz=2, ind=0x6D, ind_sz=2, ext=0x7D, ext_sz=3)),

    # Extended operations
    Instruction(mnemonic="CMPD", mode=Mode(imm=0x1083, imm_sz=4, dir=0x1093, dir_sz=3, ind=0x10A3, ind_sz=3, ext=0x10B3, ext_sz=4)),
    Instruction(mnemonic="CMPS", mode=Mode(imm=0x118C, imm_sz=4, dir=0x119C, dir_sz=3, ind=0x11AC, ind_sz=3, ext=0x11BC, ext_sz=4)),
    Instruction(mnemonic="CMPU", mode=Mode(imm=0x1183, imm_sz=4, dir=0x1193, dir_sz=3, ind=0x11A3, ind_sz=3, ext=0x11B3, ext_sz=4)),
    Instruction(mnemonic="LDS", mode=Mode(imm=0x10CE, imm_sz=4, dir=0x10DE, dir_sz=3, ind=0x10EE, ind_sz=3, ext=0x10FE, ext_sz=4)),
    Instruction(mnemonic="CMPY", mode=Mode(imm=0x108C, imm_sz=4, dir=0x109C, dir_sz=3, ind=0x10AC, ind_sz=3, ext=0x10BC, ext_sz=4)),
    Instruction(mnemonic="LDY", mode=Mode(imm=0x108E, imm_sz=4, dir=0x109E, dir_sz=3, ind=0x10AE, ind_sz=3, ext=0x10BE, ext_sz=4)),
    Instruction(mnemonic="STS", mode=Mode(dir=0x10DF, dir_sz=3, ind=0x10EF, ind_sz=3, ext=0x10FF, ext_sz=4)),
    Instruction(mnemonic="STY", mode=Mode(dir=0x109F, dir_sz=3, ind=0x10AF, ind_sz=3, ext=0x10BF, ext_sz=4)),
    Instruction(mnemonic="SWI2", mode=Mode(inh=0x103F, inh_sz=2)),
    Instruction(mnemonic="SWI3", mode=Mode(inh=0x113F, inh_sz=2)),

    # Short branches
    Instruction(mnemonic="BCC", mode=Mode(rel=0x24, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BCS", mode=Mode(rel=0x25, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BEQ", mode=Mode(rel=0x27, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BGE", mode=Mode(rel=0x2C, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BGT", mode=Mode(rel=0x2E, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BHI", mode=Mode(rel=0x22, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BHS", mode=Mode(rel=0x24, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BLE", mode=Mode(rel=0x2F, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BLO", mode=Mode(rel=0x25, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BLS", mode=Mode(rel=0x23, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BLT", mode=Mode(rel=0x2D, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BMI", mode=Mode(rel=0x2B, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BNE", mode=Mode(rel=0x26, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BPL", mode=Mode(rel=0x2A, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BRA", mode=Mode(rel=0x20, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BRN", mode=Mode(rel=0x21, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BSR", mode=Mode(rel=0x8D, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BVC", mode=Mode(rel=0x28, rel_sz=2), is_short_branch=True),
    Instruction(mnemonic="BVS", mode=Mode(rel=0x29, rel_sz=2), is_short_branch=True),

    # Long branches
    Instruction(mnemonic="LBCC", mode=Mode(rel=0x1024, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBCS", mode=Mode(rel=0x1025, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBEQ", mode=Mode(rel=0x1027, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBGE", mode=Mode(rel=0x102C, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBGT", mode=Mode(rel=0x102E, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBHI", mode=Mode(rel=0x1022, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBHS", mode=Mode(rel=0x1024, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBLE", mode=Mode(rel=0x102F, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBLO", mode=Mode(rel=0x1025, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBLS", mode=Mode(rel=0x1023, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBLT", mode=Mode(rel=0x102D, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBMI", mode=Mode(rel=0x102B, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBNE", mode=Mode(rel=0x1026, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBPL", mode=Mode(rel=0x102A, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBRA", mode=Mode(rel=0x16, rel_sz=3), is_long_branch=True),
    Instruction(mnemonic="LBRN", mode=Mode(rel=0x1021, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBSR", mode=Mode(rel=0x17, rel_sz=3), is_long_branch=True),
    Instruction(mnemonic="LBVC", mode=Mode(rel=0x1028, rel_sz=4), is_long_branch=True),
    Instruction(mnemonic="LBVS", mode=Mode(rel=0x1029, rel_sz=4), is_long_branch=True),

    # Pseudo operations
    Instruction(mnemonic="END", is_pseudo=True),
    Instruction(mnemonic="ORG", is_pseudo=True, is_origin=True),
    Instruction(mnemonic="EQU", is_pseudo=True, is_pseudo_define=True),
    Instruction(mnemonic="SET", is_pseudo=True),
    Instruction(mnemonic="RMB", is_pseudo=True),
    Instruction(mnemonic="FCB", is_pseudo=True),
    Instruction(mnemonic="FDB", is_pseudo=True),
    Instruction(mnemonic="FCC", is_pseudo=True, is_string_define=True),
    Instruction(mnemonic="SETDP", is_pseudo=True),
    Instruction(mnemonic="INCLUDE", is_pseudo=True, is_include=True),
    Instruction(mnemonic="NAM", is_pseudo=True, is_name=True)
]

# E N D   O F   F I L E #######################################################
