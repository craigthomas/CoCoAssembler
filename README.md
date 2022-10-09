# CoCo Assembler and File Utility

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/craigthomas/CoCoAssembler/Build%20Test%20Coverage?style=flat-square)](https://github.com/craigthomas/CoCoAssembler/actions)
[![Codecov](https://img.shields.io/codecov/c/gh/craigthomas/CoCoAssembler?style=flat-square)](https://codecov.io/gh/craigthomas/CoCoAssembler) 
[![Dependencies](https://img.shields.io/librariesio/github/craigthomas/CoCoAssembler?style=flat-square)](https://libraries.io/github/craigthomas/CoCoAssembler)
[![Releases](https://img.shields.io/github/release/craigthomas/CoCoAssembler?style=flat-square)](https://github.com/craigthomas/CoCoAssembler/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)

# Table of Contents

1. [What is it?](#what-is-it)
2. [Requirements](#requirements)
3. [License](#license)
4. [Installing](#installing)
5. [The Assembler](#the-assembler)
   1. [Assembler Usage](#assembler-usage)
      1. [Input File Format](#input-file-format)
      2. [Print Symbol Table](#print-symbol-table)
      3. [Print Assembled Statements](#print-assembled-statements)
      4. [Save to Binary File](#save-to-binary-file)
      5. [Save to Cassette File](#save-to-cassette-file)
      6. [Save to Disk File](#save-to-disk-file)
   2. [Mnemonic Table](#mnemonic-table)
      1. [Mnemonics](#mnemonics)
      2. [Pseudo Operations](#pseudo-operations)
   3. [Addressing Modes](#addressing-modes)
      1. [Inherent](#inherent)
      2. [Immediate](#immediate)
      3. [Extended](#extended)
      4. [Extended Indirect](#extended-indirect)
      5. [Direct](#direct)
      6. [Indexed](#indexed)
      7. [Indexed Indirect](#indexed-indirect)
      8. [Program Counter Relative](#program-counter-relative)
6. [File Utility](#file-utility)
   1. [Listing Files](#listing-files)
   2. [Extracting to Binary File](#extracting-to-binary-file)
   3. [Extracting to Cassette File](#extracting-to-cassette-file)
7. [Common Examples](#common-examples)
   1. [Appending to a Cassette](#appending-to-a-cassette)
   2. [Listing Files in an Image](#listing-files-in-an-image)
   3. [Extracting Binary Files from Cassette Images](#extracting-binary-files-from-cassette-images)
   3. [Extracting Binary Files from Disk Images](#extracting-binary-files-from-disk-images)

# What is it?

This project is an assembler for the Tandy Color Computer 1, 2 and 3 written in Python 3.6+.
More broadly speaking, it is an assembler that targets the Motorola 6809 processor, meaning it 
targets any computer that used the 6809 as it's main CPU (e.g. the 
[Dragon 32 and 64](https://en.wikipedia.org/wiki/Dragon_32/64), 
[Vectrex](https://en.wikipedia.org/wiki/Vectrex), [Thomson TO7](https://en.wikipedia.org/wiki/Thomson_TO7), 
etc). It is intended to be statement compatible with any code written for the EDTASM+ assembler. 
The assembler is capable of taking EDTASM+ assembly language code and translating it into 6809 machine code. 
Current support is for 6809 CPU instructions, but future enhancements will add 6309 instructions.

This project also includes a general purpose file utility, used mainly for manipulating
`CAS`, `DSK`, and `WAV` files. The file utility specifically targets the disk file formats and
cassette formats used by the Color Computer line of personal computers.  

---

# License

This project makes use of an MIT style license. Generally speaking, the license
is extremely permissive, allowing you to copy, modify, distribute, sell, or 
distribute it for personal or commercial purposes. Please see the file called 
[LICENSE](https://github.com/craigthomas/CoCoAssembler/blob/master/LICENSE) 
for more information.

---

# Requirements

The assembler can be run on any OS platform, including but not limited to:

- Windows (XP, Vista, 7, 8, 10, 11, etc)
- Linux (Ubuntu, Debian, Arch, Raspbian, etc)
- Mac (Mojave, Catalina, Big Sur, Monterey, Ventura, etc)

The only requirement is Python 3.6 or greater will need to be installed and
available on the search path, along with the Package Installer for Python (`pip`). 
To download Python, visit the [Downloads](https://www.python.org/downloads/) 
section on the Python website. See the Python installation documentation for more 
information on ensuring the Python interpreter is installed on the search path, 
and that `pip` is installed along with it.

---

# Installing

There is no specific installer that needs to be run in order to install
the assembler. Simply copy the source files to a directory of your choice.
A zipfile containing the latest release of the source files can be downloaded from the 
[Releases](https://github.com/craigthomas/CoCoAssembler/releases) 
section of the code repository. Unzip the contents to a directory of your 
choice. 

Next, you will need to install the required packages for the file:

    pip install -r requirements.txt

---

# The Assembler 

The assembler is contained in a file called `assmbler.py` and can be invoked with:

    python3 assembler.py
    
In general, the assembler recognizes EDTASM+ mnemonics, along with a few other
somewhat standardized mnemonics to make program compilation easier. By default,
the assembler assumes it is assembling statements in 6809 machine code. Future
releases will include a 6309 extension.

---

## Assembler Usage

To run the assembler:

    python3 assembler.py input_file

This will assemble the instructions found in file `input_file` and will generate
the associated Color Computer machine instructions in binary format. You will need
to save the assembled contents to a file to be useful. There are several switches
that are available:

* `--print` - prints out the assembled statements
* `--symbols` - prints out the symbol table
* `--to_bin` - save assembled contents to a binary file
* `--to_cas` - save assembled contents to a cassette file
* `--to_dsk` - save assembled contents to a virtual disk file
* `--name` - saves the program with the specified name on a cassette or virtual disk file

---

### Input File Format

The input file needs to follow the format below:

    LABEL    MNEMONIC    OPERANDS    COMMENT

Where:

* `LABEL` is a 10 character label for the statement
* `MNEMONIC` is a 6809 operation mnemonic from the [Mnemonic Table](#mnemonic-table) below
* `OPERANDS` are registers, values, expressions, or labels
* `COMMENT` is a 40 character comment describing the statement (must have a `;` preceding it)

An example file:

    ; Print HELLO WORLD on the screen
                NAM     HELLO           ; Name of the program
    CHROUT      EQU     $A30A           ; Location of CHROUT routine
    POLCAT      EQU     $A000           ; Location of POLCAT routine
                ORG     $0E00           ; Originate at $0E00
    START       JSR     $A928           ; Clear the screen
                LDX     #MESSAGE        ; Load X index with start of message
    PRINT       LDA     ,X+             ; Load next character of message
                CMPA    #0              ; Check for null terminator
                BEQ     FINISH          ; Done printing, wait for keypress
                JSR     CHROUT          ; Print out the character
                BRA     PRINT           ; Print next char
    MESSAGE     FCC     "HELLO WORLD"
                FDB     $0              ; Null terminator
    FINISH      JSR     [POLCAT]        ; Read keyboard
                BEQ     FINISH          ; No key pressed, wait for keypress
                JMP     $A027           ; Restart BASIC
                END     START

---

### Print Symbol Table

To print the symbol table that is generated during assembly, use the `--symbols` 
switch:

    python3 assembler.py test.asm --symbols

Which will have the following output:

    -- Symbol Table --
    $A30A CHROUT
    $A000 POLCAT
    $0E00 START
    $0E06 PRINT
    $0E11 MESSAGE
    $0E1E FINISH
    
The first column of output is the hex value of the symbol. This may be the address in
memory where the symbol exits if it labels a mnemonic, or it may be the value that the 
symbol is defined as being if it references an `EQU` statement. The second columns is 
the symbol name itself.

---

### Print Assembled Statements

To print out the assembled version of the program, use the `--print` switch:

    python3 assembler.py test.asm --print

Which will have the following output:

    -- Assembled Statements --
    $0000                         NAM HELLO         ; Name of the program
    $0000                CHROUT   EQU $A30A         ; Location of CHROUT routine
    $0000                POLCAT   EQU $A000         ; Location of POLCAT routine
    $0E00                         ORG $0E00         ; Originate at $0E00
    $0E00 BDA928          START   JSR $A928         ; Clear the screen
    $0E03 8E0E11                  LDX #MESSAGE      ; Load X index with start of message
    $0E06 A680            PRINT   LDA ,X+           ; Load next character of message
    $0E08 8100                   CMPA #0            ; Check for null terminator
    $0E0A 2712                    BEQ FINISH        ; Done printing, wait for keypress
    $0E0C BDA30A                  JSR CHROUT        ; Print out the character
    $0E0F 20F5                    BRA PRINT         ; Print next char
    $0E11 48454C4C4F    MESSAGE   FCC "HELLO WORLD" ;
    $0E1C 0000                    FDB $0            ; Null terminator
    $0E1E AD9FA000       FINISH   JSR [POLCAT]      ; Read keyboard
    $0E22 27FA                    BEQ FINISH        ; No key pressed, wait for keypress
    $0E24 7EA027                  JMP $A027         ; Restart BASIC
    $0E27                         END START         ;

A single line of output is composed of 6 columns:

    Line:   $0E00 BDA928          START   JSR $A928         ; Clear the screen
            ----- ------          -----   --- -----         ------------------
    Column:   1     2               3      4    5                   6

The columns are as follows:

1. The offset in hex where the statement occurs (`$0E00`).
2. The machine code generated and truncated to 10 hex characters (`BDA928`).
3. The user-supplied label for the statement (`START`).
4. The instruction mnemonic (`JSR`). 
5. Operands that the instruction processes (`$A928`).
6. The comment string (`Clear the screen`).

---

### Save to Binary File

To save the assembled contents to a binary file, use the `--to_bin` switch:

    python3 assembler.py test.asm --to_bin test.bin
    
The assembled program will be saved to the file `test.bin`. Note that this file
may not be useful on its own, as it does not have any meta information about
where the file should be loaded in memory (pseudo operations `ORG` and `NAM`
will not have any effect on the assembled file).

**NOTE**: If the file `test.bin` exists, it will be erased and overwritten.

---

### Save to Cassette File

To save the assembled contents to a cassette file, use the `--to_cas` switch:

    python3 assembler.py test.asm --to_cas test.cas
    
This will assemble the program and save it to a cassette file called `test.cas`.
The source code must include the `NAM` mnemonic to name the program (e.g. 
`NAM myprog`), or the `--name` switch must be used on the command line (e.g.
`--name myprog`). The program name on the cassette file will be `MYPROG`. 

**NOTE**: if the file `test.cas` exists, assembly will stop and the file will
not be overwritten. If you wish to add the program to `test.cas`, you must 
specify the `--append` flag during assembly:

    python3 assembler.py test.asm --to_cas test.cas --append
    
To load from the cassette file, you must use BASIC's `CLOADM` command as follows:

    CLOADM"MYPROG"

---

### Save to Disk File

To save the assembled contents to a disk file, use the `--to_dsk` switch:

    python3 assembler.py test.asm --to_dsk test.dsk

This will assemble the program and save it to a disk file called `test.dsk`. 
The source code must include the `NAM` mnemonic to name the program on disk (e.g.
`NAM myprog`), or the `--name` switch must be used on the command line (e.g.
`--name myprog`). The program name on the disk file will be `MYPROG.BIN`.

**NOTE**: if the file `test.dsk` exists, assembly will stop and the file will
not be updated. If you wish to add the program to `test.dsk`, you must specify the 
`--append` flag during assembly:

    python3 assembler.py test.asm --to_dsk test.dsk --append

To load from the disk file, you must use Disk Basic's `LOADM` command as follows:

    LOADM"MYPROG.BIN"

---

## Mnemonic Table

Below are the mnemonics that are accepted by the assembler (these mnemonics are 
compatible with EDTASM+ assembler mnemonics). For the mnemonics below, special 
symbols are:

* `A` - 8-bit accumulator register.
* `B` - 8-bit accumulator register.
* `CC` - 8-bit condition code register.
* `D` - 16-bit accumulator register comprised of A and B, with A being high byte, and B being low byte.
* `M` - a memory location with a value between 0 and 65535.
* `S` - 16-bit system stack register.
* `U` - 16-bit user stack register.
* `X` - 16-bit index register.
* `Y` - 16-bit index register.

Note that the operations described below may use different addressing modes for operands (e.g. `LDA` may
use immediate, direct, indexed or extended addressing to load values). See the section below on addressing
modes, and consult the MC6809 datasheet for more information on what addressing modes are applicable,
as well as the number of cycles used to execute each operation.
 
---

### Mnemonics

| Mnemonic | Description                                                                      | Example        |
|----------|----------------------------------------------------------------------------------|----------------|
| `ABX`    | Adds contents of `B` to value in register `X` and stores in `X`.                 | `ABX`          |
| `ADCA`   | Adds contents of `A`, memory value `M`, and carry bit and stores in `A`.         | `ADCA $FFEE`   |
| `ADCB`   | Adds contents of `B`, memory value `M`, and carry bit and stores in `B`.         | `ADCB $FFEF`   |
| `ADDA`   | Adds contents of `A` with memory value `M` and stores in `A`.                    | `ADDA #$03`    |
| `ADDB`   | Adds contents of `B` with memory value `M` and stores in `B`.                    | `ADDB #$90`    |
| `ADDD`   | Adds contents of `D` (`A:B`) with memory value `M:M+1` and stores in `D`.        | `ADDD #$2000`  |
| `ANDA`   | Performs a logical AND on `A` with memory value `M` and stores in `A`.           | `ANDA #$05`    |
| `ANDB`   | Performs a logical AND on `B` with memory value `M` and stores in `B`.           | `ANDB $FFEE`   |
| `ANDCC`  | Performs a logical AND on `CC` with immediate value `M` and stores in `CC`.      | `ANDCC #$01`   |
| `ASLA`   | Shifts bits in `A` left (0 placed in bit 0, bit 7 goes to carry in `CC`).        | `ASLA`         |
| `ASLB`   | Shifts bits in `B` left (0 placed in bit 0, bit 7 goes to carry in `CC`).        | `ASLB`         |
| `ASL`    | Shifts bits in `M` left (0 placed in bit 0, bit 7 goes to carry in `CC`).        | `ASL $0E00`    |
| `ASRA`   | Shifts bits in `A` right (bit 0 goes to carry in `CC`, bit 7 remains same).      | `ASRA`         |
| `ASRB`   | Shifts bits in `B` right (bit 0 goes to carry in `CC`, bit 7 remains same).      | `ASRB`         |
| `ASR`    | Shifts bits in `M` right (bit 0 goes to carry in `CC`, bit 7 remains same).      | `ASR $0E00`    |
| `BCC`    | Branches if carry bit in `CC` is 0.                                              | `BCC CLS`      |
| `BCS`    | Branches if carry bit in `CC` is 1.                                              | `BCS CLS`      |
| `BEQ`    | Branches if zero bit in `CC` is 1.                                               | `BEQ CLS`      |
| `BGE`    | Branches if negative and overflow bits in `CC` are equal.                        | `BGE CLS`      |
| `BGT`    | Branches if negative and overflow bits are equal, and zero bit is zero in `CC`.  | `BGT CLS`      |
| `BHI`    | Branches if carry and zero bit in `CC` are 0.                                    | `BHI CLS`      |
| `BHS`    | Same as `BCC`.                                                                   | `BHS CLS`      |
| `BITA`   | Logically ANDs `A` with memory contents `M` and sets bits in `CC`.               | `BITA #$1E`    |
| `BITB`   | Logically ANDs `B` with memory contents `M` and sets bits in `CC`.               | `BITB #$1E`    |
| `BLE`    | Branches if negative and overflow bits are not equal, or zero bit is 1 in `CC`.  | `BLE CLS`      |
| `BLO`    | Same as `BCS`.                                                                   | `BLO CLS`      |
| `BLS`    | Branches if zero bit is 1, or carry bit is 1 in `CC`.                            | `BLS CLS`      |
| `BLT`    | Branches if negative bit is not equal overflow bit in `CC`.                      | `BLT CLS`      |
| `BMI`    | Branches if negative bit is 1 in `CC`.                                           | `BMI CLS`      |
| `BNE`    | Branches if zero bit is 0 in `CC`.                                               | `BNE CLS`      |
| `BGE`    | Branches if negative bit is 0 in `CC`.                                           | `BGE CLS`      |
| `BRA`    | Branch always.                                                                   | `BRA CLS`      |
| `BRN`    | Branch never - essentially 2-byte `NOP`.                                         | `BRN CLS`      |
| `BSR`    | Saves the value of `PC` on the `S` stack and branches to subroutine.             | `BSR PRINT`    |
| `BVC`    | Branches if overflow bit is 0 in `CC`.                                           | `BVC CLS`      |
| `BVS`    | Branches if overflow bit is 1 in `CC`.                                           | `BVS CLS`      |
| `CLRA`   | Zeroes out the `A` register, and clears `CC`.                                    | `CLRA`         |
| `CLRB`   | Zeroes out the `B` register, and clears `CC`.                                    | `CLRB`         |
| `CLR`    | Zeroes out the memory contents `M` and clears `CC`.                              | `CLR $01E0`    |
| `CMPA`   | Subtract value from `A` register, and sets bits in `CC`.                         | `CMPA #$1E`    |
| `CMPB`   | Subtract value from `B` register, and sets bits in `CC`.                         | `CMPB #$1E`    |
| `CMPD`   | Subtract value from `D` register, and sets bits in `CC`.                         | `CMPD #$1E1F`  |
| `CMPS`   | Subtract value from `S` register, and sets bits in `CC`.                         | `CMPS #$1E1F`  |
| `CMPU`   | Subtract value from `U` register, and sets bits in `CC`.                         | `CMPU #$1E1F`  |
| `CMPX`   | Subtract value from `X` register, and sets bits in `CC`.                         | `CMPX #$1E1F`  |
| `CMPY`   | Subtract value from `Y` register, and sets bits in `CC`.                         | `CMPY #$1E1F`  |
| `COMA`   | Perform logical complement of value in `A` and store in `A`.                     | `COMA`         |
| `COMB`   | Perform logical complement of value in `B` and store in `B`.                     | `COMA`         |
| `COM`    | Perform logical complement of value in memory location `M` and store in `M`.     | `COM $FFEE`    |
| `CWAI`   | Clear `CC` register, push state onto stack, and wait for interrupt.              | `CWAI`         |
| `DAA`    | Perform decimal addition adjust in `A`. Converts to Binary Coded Decimal.        | `DAA`          |
| `DECA`   | Decrement the value in `A` by 1.                                                 | `DECA`         |
| `DECB`   | Decrement the value in `B` by 1.                                                 | `DECB`         |
| `DEC`    | Decrement the value in memory location `M` by 1.                                 | `DEC $FFEE`    |
| `EORA`   | Perform exclusive OR with value in `A`, and store in `A`.                        | `EORA #$1F`    |
| `EORB`   | Perform exclusive OR with value in `B`, and store in `B`.                        | `EORB #$1F`    |
| `EXG`    | Swap values in registers.                                                        | `EXG A,B`      |
| `INCA`   | Increment value in `A` by 1.                                                     | `INCA`         |
| `INCB`   | Increment value in `B` by 1.                                                     | `INCB`         |
| `INC`    | Increment the value in memory location `M` by 1.                                 | `INC $FFEE`    |
| `JMP`    | Unconditional jump to location.                                                  | `JMP $C000`    |
| `JSR`    | Jump to subroutine at the specified location.                                    | `JSR PRINT`    |
| `LBCC`   | Same as `BCC`, except can branch more than -126 and +129 bytes.                  | `LBCC CLS`     |
| `LBCS`   | Same as `BCS`, except can branch more than -126 and +129 bytes.                  | `LBCS CLS`     |
| `LBEQ`   | Same as `BEQ`, except can branch more than -126 and +129 bytes.                  | `LBEQ CLS`     |
| `LBGE`   | Same as `BGE`, except can branch more than -126 and +129 bytes.                  | `LBGE CLS`     |
| `LBGT`   | Same as `BGT`, except can branch more than -126 and +129 bytes.                  | `LBGT CLS`     |
| `LBHI`   | Same as `BHI`, except can branch more than -126 and +129 bytes.                  | `LBHI CLS`     |
| `LBHS`   | Same as `BHS`, except can branch more than -126 and +129 bytes.                  | `LBHS CLS`     |
| `LBLE`   | Same as `BLE`, except can branch more than -126 and +129 bytes.                  | `LBLE CLS`     |
| `LBLO`   | Same as `BLO`, except can branch more than -126 and +129 bytes.                  | `LBLO CLS`     |
| `LBLS`   | Same as `BLS`, except can branch more than -126 and +129 bytes.                  | `LBLS CLS`     |
| `LBLT`   | Same as `BLT`, except can branch more than -126 and +129 bytes.                  | `LBLT CLS`     |
| `LBMI`   | Same as `BMI`, except can branch more than -126 and +129 bytes.                  | `LBMI CLS`     |
| `LBNE`   | Same as `BNE`, except can branch more than -126 and +129 bytes.                  | `LBNE CLS`     |
| `LBPL`   | Same as `BPL`, except can branch more than -126 and +129 bytes.                  | `LBPL CLS`     |
| `LBRA`   | Same as `BRA`, except can branch more than -126 and +129 bytes.                  | `LBRA CLS`     |
| `LBRN`   | Same as `BRN`, except can branch more than -126 and +129 bytes.                  | `LBRN CLS`     |
| `LBSR`   | Same as `BSR`, except can branch more than -126 and +129 bytes.                  | `LBSR CLS`     |
| `LBVC`   | Same as `BVC`, except can branch more than -126 and +129 bytes.                  | `LBVC CLS`     |
| `LBVS`   | Same as `BVS`, except can branch more than -126 and +129 bytes.                  | `LBVS CLS`     |
| `LDA`    | Loads `A` with the specified value.                                              | `LDA #$FE`     |
| `LDB`    | Loads `B` with the specified value.                                              | `LDB #$FE`     |
| `LDD`    | Loads `D` with the specified value.                                              | `LDD #$FEFE`   |
| `LDS`    | Loads `S` with the specified value.                                              | `LDS #$FEFE`   |
| `LDU`    | Loads `U` with the specified value.                                              | `LDU #$FEEE`   |
| `LDX`    | Loads `X` with the specified value.                                              | `LDX #$FEEE`   |
| `LDY`    | Loads `Y` with the specified value.                                              | `LDY #$FEEE`   |
| `LEAS`   | Loads `S` with the address computed from an indexed addressing mode operand.     | `LEAS A,X`     |
| `LEAU`   | Loads `U` with the address computed from an indexed addressing mode operand.     | `LEAU A,X`     |
| `LEAX`   | Loads `X` with the address computed from an indexed addressing mode operand.     | `LEAX A,X`     |
| `LEAY`   | Loads `Y` with the address computed from an indexed addressing mode operand.     | `LEAY A,X`     |
| `LSLA`   | Logically shift bits left in `A`, bit 7 stored in carry of `CC`, bit 0 gets 0.   | `LSLA`         |
| `LSLB`   | Logically shift bits left in `B`, bit 7 stored in carry of `CC`, bit 0 gets 0.   | `LSLB`         |
| `LSL`    | Logically shift bits left in `M`, bit 7 stored in carry of `CC`, bit 0 gets 0.   | `LSL $FFEE`    |
| `LSRA`   | Logically shift bits right in `A`, bit 0 stored in carry of `CC`, bit 7 gets 0.  | `LSRA`         |
| `LSRB`   | Logically shift bits right in `B`, bit 0 stored in carry of `CC`, bit 7 gets 0.  | `LSRB`         |
| `LSR`    | Logically shift bits right in `M`, bit 0 stored in carry of `CC`, bit 7 gets 0.  | `LSR $FFEE`    |
| `MUL`    | Unsigned multiple of `A` and `B`, and stored in `D`.                             | `MUL`          |
| `NEGA`   | Perform twos complement of `A` and store in `A`.                                 | `NEGA`         |
| `NEGB`   | Perform twos complement of `B` and store in `B`.                                 | `NEGB`         |
| `NEG`    | Perform twos complement of `M` and store in `M`.                                 | `NEG $FFEE`    |
| `NOP`    | Do nothing but advance program counter to next memory location.                  | `NOP`          |
| `ORA`    | Perform logical OR of `A` and value, and store in `A`.                           | `ORA #$A1`     |
| `ORB`    | Perform logical OR of `B` and value, and store in `B`.                           | `ORB #$CD`     |
| `ORCC`   | Perform logical OR of `CC` and value, and store in `CC`.                         | `ORCC #$C0`    |
| `PSHS`   | Pushes specified registers onto the `S` stack.                                   | `PSHS A,B,X`   |
| `PSHU`   | Pushes specified registers onto the `U` stack.                                   | `PSHU A,B,X`   |
| `PULS`   | Pulls values from the `S` stack back into their registers.                       | `PULS A,B,X`   |
| `PULU`   | Pulls values from the `U` stack back into their registers.                       | `PULU A,B,X`   |
| `ROLA`   | Rotates bits left in `A`, bit 7 stored in carry, and carry stored in bit 0.      | `ROLA`         |
| `ROLB`   | Rotates bits left in `B`, bit 7 stored in carry, and carry stored in bit 0.      | `ROLB`         |
| `ROL`    | Rotates bits left in `M`, bit 7 stored in carry, and carry stored in bit 0.      | `ROL $FFEE`    |
| `RORA`   | Rotates bits right in `A`, carry stored in bit 7, and bit 0 stored in carry.     | `RORA`         |
| `RORB`   | Rotates bits right in `B`, carry stored in bit 7, and bit 0 stored in carry.     | `RORB`         |
| `ROR`    | Rotates bits right in `M`, carry stored in bit 7, and bit 0 stored in carry.     | `ROL $FFEE`    |
| `RTI`    | Return from interrupt, pops `CC`, then `A`, `B`, `DP`, `X`, `Y`, `U` if `E` set. | `RTI`          |
| `RTS`    | Return from subroutine, pops `PC` from `S` stack.                                | `RTS`          |
| `SBCA`   | Subtract byte and carry from `A` and store in `A`.                               | `SBCA #$C0`    |
| `SBCB`   | Subtract byte and carry from `B` and store in `B`.                               | `SBCB #$C0`    |
| `SEX`    | Sign extend bit 7 from `B` into all of `A` and into negative of `CC`.            | `SEX`          |
| `STA`    | Stores value in `A` at the specified memory location `M`.                        | `STA $FFEE`    |
| `STB`    | Stores value in `B` at the specified memory location `M`.                        | `STB $1EEE`    |
| `STD`    | Stores value in `D` at the specified memory location `M`.                        | `STD $1EEE`    |
| `STS`    | Stores value in `S` at the specified memory location `M`.                        | `STS $1EEE`    |
| `STU`    | Stores value in `U` at the specified memory location `M`.                        | `STU $1EEE`    |
| `STX`    | Stores value in `X` at the specified memory location `M`.                        | `STX $1EEE`    |
| `STY`    | Stores value in `Y` at the specified memory location `M`.                        | `STY $1EEE`    |
| `SUBA`   | Subtracts the 8-bit value from `A` and stores in `A`.                            | `SUBA #$1E`    |
| `SUBB`   | Subtracts the 8-bit value from `B` and stores in `B`.                            | `SUBB #$1E`    |
| `SUBD`   | Subtracts the 16-bit value from `D` and stores in `D`.                           | `SUBB #$1E`    |
| `SWI`    | Push all registers on the stack and branch to subroutine at `$FFFA`.             | `SWI`          |
| `SWI2`   | Push all registers on the stack and branch to subroutine at `$FFF4`.             | `SWI2`         |
| `SWI3`   | Push all registers on the stack and branch to subroutine at `$FFF2`.             | `SWI3`         |
| `SYNC`   | Halt and wait for interrupt.                                                     | `SYNC`         |
| `TFR`    | Transfer source register value to destination register.                          | `TFR A,B`      |
| `TSTA`   | Test value in `A`, and set negative in `CC` and zero in `CC` as required.        | `TSTA`         |
| `TSTB`   | Test value in `B`, and set negative in `CC` and zero in `CC` as required.        | `TSTB`         |
| `TST`    | Test value in `M`, and set negative in `CC` and zero in `CC` as required.        | `TST $FFFE`    |

---

### Pseudo Operations

| Mnemonic  | Description                                                                | Example               |
|-----------|----------------------------------------------------------------------------|-----------------------|
| `FCB`     | Defines a byte constant value. Separate multiple bytes with `,`.           | `FCB $1C,$AA`         |
| `FCC`     | Defines a string constant value enclosed in a matching pair of delimiters. | `FCC "hello"`         |
| `FDB`     | Defines a word constant value. Separate multiple word with `,`.            | `FDB $2000,$CAFE`     |
| `END`     | Defines the end of the program.                                            | `END`                 |
| `EQU`     | Defines a symbol with a set value.                                         | `SCRMEM EQU $1000`    |
| `INCLUDE` | Includes another assembly source file at this location.                    | `INCLUDE globals.asm` |
| `NAM`     | Sets the name for the program when assembled to disk or cassette.          | `NAM myprog`          |
| `ORG`     | Defines where in memory the program should originate at.                   | `ORG $0E00`           |
| `RMB`     | Defines a block of _n_ bytes initialized to a zero value.                  | `RMB $8`              |
| `SETDP`   | Sets the direct page value for the assembler (see notes below).            | `SETDP $0E00`         |

**Notes**

* `SETDP` - this mnemonic is used for memory and instruction optimization by the assembler. For example, 
if `SETDP $0E00` is set, any machine instructions that use `$0EXX` as a memory location will be assembled 
using direct page addressing. Instructions such as `JMP $0E8F` will become `JMP <$8F`. The programmer is 
responsible for loading the direct page register manually - this mnemonic does not output opcodes that
change the direct page register. 

---

## Addressing Modes

The assembler understands several type of addressing modes for each operation. Please note that
you will need to consult the MC6809 Data Sheet for information regarding what operations support which
addressing modes. The different modes are explained below. Again, the discussion below is a simplified 
explanation of the material that exists in the MC6809 Data Sheet.

---

### Inherent

The operation takes no additional information to execute. For example, the decimal additional adjust 
operation requires no additional inputs and is specified with:

    DAA

---

### Immediate

The operation requires a value that is specified directly following the mnemonic. All immediate values
must be prefixed with an `#` symbol. For example, to load the value of `$FE` into register `A`:

    LDA #$FE

---

### Extended

The operation requires a 16-bit address that is used for execution of the instruction. The address
may be specified as a hard-coded value, or as a symbol. For example:

    JMP $FFEE
    BSR POLCAT

---

### Extended Indirect

The operation requires a 16-bit address where the memory contents specify another 16-bit address.
Extended indirect addressing mode is denoted by using square brackets to enclose the operand. For
example:

    JMP [$010E]
    BSR [PRINT]

---

### Direct

Works similarly to extended addressing, however, instead of using a 16-bit value to specify the
address, uses the contents of the direct page `DP` register and an 8-bit value to form the 
full 16-bit address. This addressing mode saves space. Direct addressing also has a lower
clock-cycle count for execution. For example, assuming that the `DP` register is set to `$FF`, then
the following statement:

    JMP $EE

Is equivalent to the extended addressing mode variant of:

    JMP $FFEE

Additionally, the direct addressing mode can be explicitly invoked on the operand by prefixing
the operand with an `<` symbol. For example:

    JMP <PRINT

In general, the assembler will attempt to optimize addressing modes by converting any extended
addressing operands to direct operands wherever possible. By default, the assembler assumes that
the `DP` register will be `$00`. The `SETDP` pseudo operation is used to inform the assembler that 
the direct page content has changed. For all lines following the `SETDP` invocation, the new 
high 8-bit value will be used for optimization. For example:

    SETDP $FF
    JMP $FFEE

The assembler will convert the operand specified in the `JMP` instruction to a direct operand, since
the upper 8-bits of the instruction are `$FF` and the direct page reigster is set to `$FF`. Thus,
the resultant output will be equivalent to:

    JMP $EE

Note that the `SETDP` pseudo operation does not actually modify the contents of `DP` - it is up to the
programmer to manipulate the direct page register prior to using `SETDP`.

---

### Indexed

Works with one of the pointer registers `X`, `Y`, `U`, or `S`. The calculation of the address
required by the operand is relative to the offset as pointed to by the pointer register used.
In the simplest case, the offset is _zero offset_, which is just relative to the pointer 
register itself. For example:

    LDB X

The above statement would load the value from memory pointed to by the `X` pointer register.
If for example, `X` held `$FFEE`, then the load operation would load `B` with the contents in
`$FFEE`. When numeric values are used, then the offset is calculated by taking the pointer 
register and summing the value with the register value. For example:

    LDB -2,X

In this example, if `X` held `$FF02`, the the load operation would load `B` with the contents in
`$FF00`. Note that symbols can also appear:

    LDB ADJ,X

Pointer registers can also be _auto incremented or decremented_ in indexed mode. The register values
are either pre-decremented, or post-incremented. Values can be incremented or decremented by 1 or 2
steps. For example:

    LDB ,X+
    LDB ,X++
    LDB ,-X
    LDB ,--X

The first statement above will load `B` with the value pointed to by `X`, and then increment the
value of the `X` register. The second statement will do the same, but increment the value of `X` twice.
The third statement will decrement `X` prior to the load, and the fourth statement will decrement the
`X` register value twice before the load. 

---

### Indexed Indirect

Similar to extended indirect addressing, indexed statements may also be indirect as well. For example:

    LDB [,X]

---

### Program Counter Relative

In order to support position independent code, a final form of addressing is supported relative to 
the program counter. In this case, instead of the offset being relative to a pointer register, 
the offset is specified relative to the program counter. For example:

    LDA $10,PCR

This will load the value of `A` with the contents of the memory position `$10` bytes above where 
the `PC` is currently pointing. Again, since this is considered to be a form of indexed expression,
indirect addressing based on program counter is also possible:

    LDA [$10,PCR]

---

# File Utility

The file utility included with the assembler package provides a method for manipulating and
extracting information from image files (e.g. `CAS` or `DSK` files). 

---

## Listing Files

To list the files contained within a cassette or disk image, use the `--list` switch:

    python file_util.py --list test.cas
    
The utility will print a list of all the files contained within the image, along with
associated meta-data:

    -- File #1 --
    Filename:   HELLO
    File Type:  Object
    Data Type:  Binary
    Gap Status: No Gaps
    Load Addr:  $0E00
    Exec Addr:  $0E00
    Data Len:   39 bytes

    -- File #2 --
    Filename:   WORLD
    File Type:  Object
    Data Type:  Binary
    Gap Status: No Gaps
    Load Addr:  $0F00
    Exec Addr:  $0F00
    Data Len:   73 bytes

    -- File #3 --
    Filename:   ANOTHER
    File Type:  Object
    Data Type:  Binary
    Gap Status: No Gaps
    Load Addr:  $0C00
    Exec Addr:  $0C00
    Data Len:   24 bytes

---

## Extracting to Binary File

To extract the files from a disk or cassette image, and save each one as a binary, use the
`--to_bin` switch:

    python file_util.py --to_bin test.cas
    
To command will list the files being extracted and their status:

    -- File #1 [HELLO] --
    Saved as HELLO.bin
    -- File #2 [WORLD] --
    Saved as WORLD.bin
    -- File #3 [ANOTHER] --
    Saved as ANOTHER.bin

Note that no meta-data is saved with the extraction (meaning that load addresses, 
and execute addresses are not saved in the resulting `.bin` files). If you only wish to
extract a specific subset of files, you can provide a space-separated, case-insensitive
list of filenames to extract with the `--files` switch:

    python file_util.py --to_bin test.cas --files hello another

Which will result in:

    -- File #1 [HELLO] --
    Saved as HELLO.bin
    -- File #3 [ANOTHER] --
    Saved as ANOTHER.bin

---

## Extracting to Cassette File

To extract the files from a disk image, and save each one as a cassette file, use the
`--to_cas` switch:

    python file_util.py --to_cas test.dsk
    
To command will list the files being extracted and their status:

    -- File #1 [HELLO] --
    Saved as HELLO.cas
    -- File #2 [WORLD] --
    Saved as WORLD.cas
    -- File #3 [ANOTHER] --
    Saved as ANOTHER.cas

If you only wish to extract a specific subset of files, you can provide a space-separated, 
case-insensitive list of filenames to extract with the `--files` switch:

    python file_util.py --to_cas test.dsk --files hello another

Which will result in:

    -- File #1 [HELLO] --
    Saved as HELLO.cas
    -- File #3 [ANOTHER] --
    Saved as ANOTHER.cas

---

# Common Examples

Below are a collection of common examples with their command-line usage.

---

## Appending to a Cassette

To assemble a program called `myprog.asm` and add it to an existing cassette file:

    python assembler.py myprog.asm --cas_file my_cassette.cas --append

---

## Listing Files in an Image

To list the files contained within an container file (such as `CAS` or `DSK` file):

    python file_util.py --list my_cassette.cas
    
This will print out a list of all the file contents on the cassette image 
`my_cassette.cas`. Note that `BIN` or binary only file contents only have a single
program with no meta-information stored in them. As such, no information will be
available for binary file types.

---

## Extracting Binary Files from Cassette Images

To extract all the binary files from a cassette image:

    python file_util.py --to_bin my_cassette.cas
    
Will extract all of the files in the image file `my_cassette.bin` to separate
files ending in a `.bin` extension. No meta-information about the files will
be saved in `.bin` format.

---

## Extracting Binary Files from Disk Images

To extract all the binary files from a disk image:

    python file_util.py --to_bin my_disk.dsk
    
Will extract all of the files in the image file `my_disk.dsk` to separate
files ending in a `.bin` extension. No meta-information about the files will
be saved in `.bin` format.
