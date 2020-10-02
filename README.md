# CoCo Assembler and File Utility

[![Build Status](https://img.shields.io/travis/craigthomas/CoCoAssembler?style=flat-square)](https://travis-ci.org/craigthomas/CoCoAssembler) 
[![Codecov](https://img.shields.io/codecov/c/gh/craigthomas/CoCoAssembler?style=flat-square)](https://codecov.io/gh/craigthomas/CoCoAssembler) 
[![Dependencies](https://img.shields.io/librariesio/github/craigthomas/CoCoAssembler?style=flat-square)](https://libraries.io/github/craigthomas/CoCoAssembler)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)

# Table of Contents

1. [What is it?](#what-is-it)
2. [Requirements](#requirements)
3. [License](#license)
4. [Installing](#installing)
5. [Assembler](#assembler)
   1. [Assembler Usage](#assembler-usage)
      1. [Input File Format](#input-file-format)
      2. [Print Symbol Table](#print-symbol-table)
      3. [Print Assembled Statements](#print-assembled-statements)
      4. [Save to Binary File](#save-to-binary-file)
      5. [Save to Cassette File](#save-to-cassette-file)
   2. [Mnemonic Table](#mnemonic-table)
      1. [Mnemonics](#mnemonics)
      2. [Pseudo Operations](#pseudo-operations)
   3. [Operands](#operands)
   4. [Addressing Modes](#addressing-modes)
6. [File Utility](#file-utility)
   1. [Listing Files](#listing-files)
   2. [Extracting Binaries](#extracting-binaries)
6. [Common Examples](#common-examples)
   1. [Appending to a Cassette](#appending-to-a-cassette)
   2. [Listing Files in an Image](#listing-files-in-an-image)
   3. [Extracting Binary Files from Cassette Images](#extracting-binary-files-from-cassette-images)

# What is it?

This project is an assembler for the Tandy Color Computer 1, 2 and 3 written in Python 3.6. 
It is intended to be statement compatible with any code written for the EDTASM+ assembler.
The assembler is capable of taking EDTASM+ assembly language code and translating it into
machine code for the Color Computer 1, 2, and 3. Current support is for 6809 CPU instructions,
but future enhancements will add 6309 instructions.

This project also includes a general purpose file utility, used mainly for manipulating
`CAS`, `DSK`, and `WAV` files. 

# Requirements

In order to run the assembler, you will need Python 3.6 or greater. If you
prefer to clone the repository, you will need Git (if you don't want to 
install Git, then check the [Releases](https://github.com/craigthomas/CoCoAssembler/releases)
section for the newest release of the package that you can download).

# License

This project makes use of an MIT style license. Please see the file called 
[LICENSE](https://github.com/craigthomas/CoCoAssembler/blob/master/LICENSE) 
for more information.

# Installing

To install the source files, download the latest release from the 
[Releases](https://github.com/craigthomas/CoCoAssembler/releases) 
section of the repository and unzip the contents in a directory of your 
choice. Or, clone the repository in the directory of your choice with:

    git clone https://github.com/craigthomas/CoCoAssembler.git

Next, you will need to install the required packages for the file:

    pip install -r requirements.txt

    
# Assembler 

The assembler is contained in a file called `assmbler.py` and can be invoked with:

    python assembler.py
    
In general, the assembler recognizes EDTASM+ mnemonics, along with a few other
somewhat standardized mnemonics to make program compilation easier. By default,
the assembler assumes it is assembling statements in 6809 machine code. Future
releases will include a 6309 extension.
 
## Assembler Usage

To run the assembler:

    python assembler.py input_file

This will assemble the instructions found in file `input_file` and will generate
the associated Color Computer machine instructions in binary format. You will need
to save the assembled contents to a file to be useful. There are several switches
that are available:

* `--print` - prints out the assembled statements
* `--symbols` - prints out the symbol table
* `--bin_file` - save assembled contents to a binary file
* `--cas_file` - save assembled contents to a cassette file
* `--dsk_file` - save assembled contents to a virtual disk file
* `--name` - saves the program with the specified name on a cassette or virtual disk file

### Input File Format

The input file needs to follow the format below:

    LABEL    MNEMONIC    OPERANDS    COMMENT

Where:

* `LABEL` is a 10 character label for the statement
* `MNEMONIC` is a 6809 operation mnemonic from the [Mnemonic Table](#mnemonic-table) below
* `OPERANDS` are registers, values, expressions, or labels as described in the [Operands](#operands) section
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
    

### Print Symbol Table

To print the symbol table that is generated during assembly, use the `--symbols` 
switch:

    python assembler.py test.asm --symbols

Which will have the following output:

    -- Symbol Table --
    $A30A CHROUT
    $A000 POLCAT
    $0E00 START
    $0E06 PRINT
    $0E11 MESSAGE
    $0E1E FINISH
    
The first column of output is the hex value of the symbol, the second columns is the symbol name
itself.


### Print Assembled Statements

To print out the assembled version of the program, use the `--print` switch:

    python assembler.py test.asm --print

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


### Save to Binary File

To save the assembled contents to a binary file, use the `--bin_file` switch:

    python assembler.py test.asm --bin_file test.bin
    
The assembled program will be saved to the file `test.bin`. Note that this file
may not be useful on its own, as it does not have any meta information about
where the file should be loaded in memory (pseudo operations `ORG` and `NAM`
will not have any effect on the assembled file).

**NOTE**: If the file `test.bin` exists, it will be erased and overwritten.


### Save to Cassette File

To save the assembled contents to a cassette file, use the `--cas_file` switch:

    python assembler.py test.asm --cas_file test.cas
    
This will assemble the program and save it to a cassette file called `test.cas`.
The source code must include the `NAM` mnemonic to name the program (e.g. 
`NAM myprog`), or the `--name` switch must be used on the command line (e.g.
`--name myprog`). The program name on the cassette file will be `myprog`. 

**NOTE**: if the file `test.cas` exists, assembly will stop and the file will
not be overwritten. If you wish to add the program to `test.cas`, you must 
specify the `--append` flag during compilation:

    python assembler.py test.asm --cas_file test.cas --append
    
This will add the file to the `test.cas` file as an additional binary within
the cassette. To load from the cassette file using BASIC's `CLOADM` command
would be done as follows

    CLOADM"MYPROG"

    
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
 
### Mnemonics

| Mnemonic | Description | Example |
| -------- | ----------- | ------- |
| `ABX`    | Adds contents of `B` to value in register `X` and stores in `X`.           | `ABX`                  |
| `ADCA`   | Adds contents of `A`, memory value `M`, and carry bit and stores in `A`.   | `ADCA $FFEE`           |
| `ADCB`   | Adds contents of `B`, memory value `M`, and carry bit and stores in `B`.   | `ADCB $FFEF`           |
| `ADDA`   | Adds contents of `A` with memory value `M` and stores in `A`.              | `ADDA #$03`            |
| `ADDB`   | Adds contents of `B` with memory value `M` and stores in `B`.              | `ADDB #$90`            |
| `ADDD`   | Adds contents of `D` (`A:B`) with memory value `M:M+1` and stores in `D`.  | `ADDD #$2000`          |
| `ANDA`   | Performs a logical AND on `A` with memory value `M` and stores in `A`.     | `ANDA #$05`            |
| `ANDB`   | Performs a logical AND on `B` with memory value `M` and stores in `B`.     | `ANDB $FFEE`           |
| `ANDCC`  | Performs a logical AND on `CC` with immediate value `M` and stores in `CC`.| `ANDCC #01`            |
| `ASLA`   | Shifts bits in `A` left (0 placed in bit 0, bit 7 goes to carry in `CC`).  | `ASLA`                 |
| `ASLB`   | Shifts bits in `B` left (0 placed in bit 0, bit 7 goes to carry in `CC`).  | `ASLB`                 |
| `ASL`    | Shifts bits in `M` left (0 placed in bit 0, bit 7 goes to carry in `CC`).  | `ASL $0E00`            |
| `ASRA`   | Shifts bits in `A` right (bit 0 goes to carry in `CC`, bit 7 remains same).| `ASRA`                 |
| `ASRB`   | Shifts bits in `B` right (bit 0 goes to carry in `CC`, bit 7 remains same).| `ASRB`                 |
| `ASR`    | Shifts bits in `M` right (bit 0 goes to carry in `CC`, bit 7 remains same).| `ASR $0E00`            |


### Pseudo Operations

| Mnemonic | Description | Example |
| -------- | ----------- | ------- |
| `FCB`    | Defines a single byte constant value.                                      | `FCB $1C`              |
| `FCC`    | Defines a string constant value enclosed in a matching pair of delimiters. | `FCC "hello"`          |
| `FDB`    | Defines a two byte constant value.                                         | `FDB $2000`            |
| `END`    | Defines the end of the program.                                            | `END`                  |
| `EQU`    | Defines a symbol with a set value.                                         | `SCRMEM EQU $1000`     |
| `INCLUDE`| Includes another assembly source file at this location.                    | `INCLUDE globals.asm`  |
| `NAM`    | Sets the name for the program when assembled to disk or cassette.          | `NAM myprog`           |
| `ORG`    | Defines where in memory the program should originate at.                   | `ORG $0E00`            |
| `RMB`    | Defines a block of _n_ bytes initialized to a zero value.                  | `RMB $8`               |
| `SETDP`  | Sets the direct page value for the assembler (see notes below).            | `SETDP $0E00`          |

**Notes**

* `SETDP` - this mnemonic is used for memory and instruction optimization by the assembler. For example, 
if `SETDP $0E00` is set, any machine instructions that use `$0EXX` as a memory location will be assembled 
using direct page addressing. Instructions such as `JMP $0E8F` will become `JMP <$8F`. The programmer is 
responsible for loading the direct page register manually - this mnemonic does not output opcodes that
change the direct page register. 

## Operands

(Under construction)

## Addressing Modes

(Under construction)

# File Utility

The file utility included with the assembler package provides a method for manipulating and
extracting information from image files (e.g. `CAS` or `DSK` files). 

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

## Extracting Binaries

To extract the files from a disk image, and save each one as a binary, use the
`--to_bin` switch:

    python file_util.py --to_bin test.cas
    
To command will list the files being extracted and their status:

    -- File #1 [HELLO] --
    Saved as HELLO.bin
    -- File #2 [WORLD] --
    Saved as WORLD.bin

Note that no meta-data is saved with the extraction (meaning that load addresses, 
and execute addresses are not saved in the resulting `.bin` files).

# Common Examples

Below are a collection of common examples with their command-line usage.

## Appending to a Cassette

To assemble a program called `myprog.asm` and add it to an existing cassette file:

    python assembler.py myprog.asm --cas_file my_cassette.cas --append

## Listing Files in an Image

To list the files contained within an container file (such as `CAS` or `DSK` file):

    python file_util.py --list my_cassette.cas
    
This will print out a list of all the file contents on the cassette image 
`my_cassette.cas`. Note that `BIN` or binary only file contents only have a single
program with no meta-information stored in them. As such, no information will be
available for binary file types.

## Extracting Binary Files from Cassette Images

To extract all the binary files from a cassette image:

    python file_util.py --to_bin my_cassette.cas
    
Will extract all of the files in the image file `my_cassette.bin` to separate
files ending in a `.bin` extension. No meta-information about the files will
be saved in `.bin` format.