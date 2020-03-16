"""
Copyright (C) 2019-2020 Craig Thomas

This project uses an MIT style license - see LICENSE for details.
A Color Computer Assembler - see the README.md file for details.
"""
# I M P O R T S ###############################################################

from typing import NamedTuple, Callable

from cocoasm.exceptions import TranslationError
from cocoasm.values import StringValue

# C O N S T A N T S ###########################################################

# Invalid operation
IVLD = 0x01

# Illegal addressing mode
ILLEGAL_MODE = 0x00

# Recognized register names
REGISTERS = ["A", "B", "D", "X", "Y", "U", "S", "CC", "DP", "PC"]


# C L A S S E S ###############################################################

class InstructionBundle(object):
    def __init__(self, op_code=None, address=None, post_byte=None, additional=None):
        self.op_code = op_code
        self.address = address
        self.post_byte = post_byte
        self.additional = additional
        self.branch_index = 0

    def __str__(self):
        return "op_code: {}, address: {}, post_byte: {}, additional: {}".format(
            self.op_code, self.address, self.post_byte, self.additional
        )

    def set_branch_index(self, index):
        self.branch_index = index

    def get_size(self):
        size = 0

        # if self.op_code:
        #     size += int((len(self.get_op_codes()) / 2))

        if self.additional:
            size += int((len(self.additional) / 2))

        # if self.instruction_bundle.post_byte:
        #     self.size += int((len(self.get_post_byte()) / 2))

        return size


class Mode(NamedTuple):
    """
    The Mode class represents a set of addressing modes. Modes supported by the 
    Color Computer are Inherent (inh), Immediate (imm), Direct (dir),
    Indexed (ind), Extended (ext), and Relative (rel). Each instruction may have
    one or more addressing modes (see Instruction class).
    """
    inh: int = IVLD
    inh_sz: int = 0
    imm: int = IVLD
    imm_sz: int = 0
    dir: int = IVLD
    dir_sz: int = 0
    ind: int = IVLD
    ind_sz: int = 0
    ext: int = IVLD
    ext_sz: int = 0
    rel: int = IVLD
    rel_sz: int = 0

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
    is_short_branch: bool = False
    is_long_branch: bool = False
    func: Callable[..., str] = None

    def is_include(self):
        """
        Returns true if the pseudo operation is an INCLUDE directive,
        false otherwise.

        :return: True if the operation is an INCLUDE operation, False otherwise
        """
        return self.mnemonic == "INCLUDE"

    def is_pseudo(self):
        return self.mnemonic in ["FCC", "FCB", "FDB", "EQU", "INCLUDE", "END", "ORG"]

    def is_pseudo_define(self):
        return self.mnemonic in ["EQU"]

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
            return InstructionBundle(additional=operand.get_hex_value())

        if self.mnemonic == "FDB":
            return InstructionBundle(additional=operand.get_hex_value())

        if self.mnemonic == "EQU":
            return InstructionBundle()

        if self.mnemonic == "ORG":
            return InstructionBundle(address=operand.get_hex_value())

        if self.mnemonic == "FCC":
            return InstructionBundle(additional=operand.get_hex_value())

        if self.mnemonic == "END":
            return InstructionBundle()

    def translate_special(self, operand, statement):
        """
        Translates special non-pseudo operations.

        :param operand: the operand to process
        :param statement: the statement that this operation came from
        """
        instruction_bundle = InstructionBundle()
        instruction_bundle.op_code = statement.get_instruction().mode.imm

        if self.mnemonic == "PSHS" or self.mnemonic == "PULS":
            registers = operand.get_operand_string().split(",")
            instruction_bundle.post_byte = 0x00
            for register in registers:
                if register not in REGISTERS:
                    raise ValueError("unknown register {}".format(register))

                instruction_bundle.post_byte |= 0x06 if register == "D" else 0x00
                instruction_bundle.post_byte |= 0x01 if register == "CC" else 0x00
                instruction_bundle.post_byte |= 0x02 if register == "A" else 0x00
                instruction_bundle.post_byte |= 0x04 if register == "B" else 0x00
                instruction_bundle.post_byte |= 0x08 if register == "DP" else 0x00
                instruction_bundle.post_byte |= 0x10 if register == "X" else 0x00
                instruction_bundle.post_byte |= 0x20 if register == "Y" else 0x00
                instruction_bundle.post_byte |= 0x40 if register == "U" else 0x00
                instruction_bundle.post_byte |= 0x80 if register == "PC" else 0x00
            return instruction_bundle

        if self.mnemonic == "EXG" or self.mnemonic == "TFR":
            registers = operand.get_operand_string().split(",")
            instruction_bundle.post_byte = 0x00
            if len(registers) != 2:
                raise TranslationError("{} requires exactly 2 registers".format(self.mnemonic), statement)

            if registers[0] not in REGISTERS:
                raise TranslationError("unknown register {}".format(registers[0]), statement)

            if registers[1] not in REGISTERS:
                raise TranslationError("unknown register {}".format(registers[1]), statement)

            instruction_bundle.post_byte |= 0x00 if registers[0] == "D" else 0x00
            instruction_bundle.post_byte |= 0x00 if registers[1] == "D" else 0x00

            instruction_bundle.post_byte |= 0x10 if registers[0] == "X" else 0x00
            instruction_bundle.post_byte |= 0x01 if registers[1] == "X" else 0x00

            instruction_bundle.post_byte |= 0x20 if registers[0] == "Y" else 0x00
            instruction_bundle.post_byte |= 0x02 if registers[1] == "Y" else 0x00

            instruction_bundle.post_byte |= 0x30 if registers[0] == "U" else 0x00
            instruction_bundle.post_byte |= 0x03 if registers[1] == "U" else 0x00

            instruction_bundle.post_byte |= 0x40 if registers[0] == "S" else 0x00
            instruction_bundle.post_byte |= 0x04 if registers[1] == "S" else 0x00

            instruction_bundle.post_byte |= 0x50 if registers[0] == "PC" else 0x00
            instruction_bundle.post_byte |= 0x05 if registers[1] == "PC" else 0x00

            instruction_bundle.post_byte |= 0x80 if registers[0] == "A" else 0x00
            instruction_bundle.post_byte |= 0x08 if registers[1] == "A" else 0x00

            instruction_bundle.post_byte |= 0x90 if registers[0] == "B" else 0x00
            instruction_bundle.post_byte |= 0x09 if registers[1] == "B" else 0x00

            instruction_bundle.post_byte |= 0xA0 if registers[0] == "CC" else 0x00
            instruction_bundle.post_byte |= 0x0A if registers[1] == "CC" else 0x00

            instruction_bundle.post_byte |= 0xB0 if registers[0] == "DP" else 0x00
            instruction_bundle.post_byte |= 0x0B if registers[1] == "DP" else 0x00

            if instruction_bundle.post_byte not in [
                    0x01, 0x10, 0x02, 0x20, 0x03, 0x30, 0x04, 0x40,
                    0x05, 0x50, 0x12, 0x21, 0x13, 0x31, 0x14, 0x41,
                    0x15, 0x51, 0x23, 0x32, 0x24, 0x42, 0x25, 0x52,
                    0x34, 0x43, 0x35, 0x53, 0x45, 0x54, 0x89, 0x98,
                    0x8A, 0xA8, 0x8B, 0xB8, 0x9A, 0xA9, 0x9B, 0xB9,
                    0xAB, 0xBA, 0x00, 0x11, 0x22, 0x33, 0x44, 0x55,
                    0x88, 0x99, 0xAA, 0xBB]:
                raise TranslationError("{} of {} to {} not allowed".format(self.mnemonic, registers[0], registers[1]),
                                       statement)

        return instruction_bundle


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
    Instruction(mnemonic="EXG", mode=Mode(imm=0x1E, imm_sz=2)),
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
    Instruction(mnemonic="PSHS", mode=Mode(imm=0x34, imm_sz=2)),
    Instruction(mnemonic="PSHU", mode=Mode(imm=0x36, imm_sz=2)),
    Instruction(mnemonic="PULS", mode=Mode(imm=0x35, imm_sz=2)),
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
    Instruction(mnemonic="TFR", mode=Mode(imm=0x1F, imm_sz=2)),
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
