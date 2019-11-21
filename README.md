# CoCo Assembler

[![Build Status](https://img.shields.io/travis/craigthomas/CoCo3Assembler?style=flat-square)](https://travis-ci.org/craigthomas/CoCo3Assembler) 
[![Codecov](https://img.shields.io/codecov/c/gh/craigthomas/CoCo3Assembler?style=flat-square)](https://codecov.io/gh/craigthomas/CoCo3Assembler) 
[![Dependencies](https://img.shields.io/librariesio/github/craigthomas/CoCo3Assembler?style=flat-square)](https://libraries.io/github/craigthomas/CoCo3Assembler)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://opensource.org/licenses/MIT)

## Table of Contents

1. [What is it?](#what-is-it)
2. [Requirements](#requirements)
3. [License](#license)
4. [Installing](#installing)
5. [Usage](#usage)

## What is it?

This project is an assembler for the Tandy Color Computer 1, 2 and 3 written in Python 3.6. 
It is intended to be statement compatible with any code written for the EDTASM+ assembler.

## Requirements

In order to run the assembler, you will need Python 3.6 or greater. If you
prefer to clone the repository, you will need Git (if you don't want to 
install Git, then check the [Releases](https://github.com/craigthomas/CoCo3Assembler/releases)
section for the newest release of the package that you can download.

## License

This project makes use of an MIT style license. Please see the file called 
LICENSE for more information.

## Installing

To install the source files, download the latest release from the 
[Releases](https://github.com/craigthomas/CoCo3Assembler/releases) 
section of the repository and unzip the contents in a directory of your 
choice. Or, clone the repository in the directory of your choice with:

    git clone https://github.com/craigthomas/Chip8Assembler.git

Next, you will need to install the required packages for the file:

    pip install -r requirements.txt

    
## Usage

To run the assembler:

    python assembler.py input_file --output output_file

This will assemble the instructions found in file `input_file` and will generate
the associated Color Computer machine instructions in binary format in `output_file`.

### Input Format

The input file needs to follow the format below:

    LABEL    MNEMONIC    OPERANDS    COMMENT

Where:

* `LABEL` is a 15 character label for the statement
* `MNEMONIC` is a Chip 8 operation mnemonic from the [Mnemonic Table](#mnemonic-table) below
* `OPERANDS` are registers, values or labels, as described in the [Operands](#operands) section
* `COMMENT` is a 30 character comment describing the statement (must have a `;` preceding it)

An example file:

    # A comment line that contains nothing


### Print Symbol Table

To print the symbol table that is generated during assembly, use the `--symbols` 
switch:

    python assembler.py test.asm --symbols

Which will have the following output:

    -- Symbol Table --


### Print Assembled Statements

To print out the assembled version of the program, use the `--print` switch:

    python assembler.py test.asm --print

Which will have the following output:

    -- Assembled Statements --

With this output, the first column is the offset in hex where the statement starts,
the second column contains the full machine-code operand, the third column is the
user-supplied label for the statement, the forth column is the mnemonic, the fifth
column is the register values of other numeric or label data the operation will
work on, and the fifth column is the comment string.

## Mnemonic Table

### Mnemonics

### Pseudo Operations

### Operands

## Further Documentation

The best documentation is in the code itself. Please feel free to examine the
code and experiment with it.
