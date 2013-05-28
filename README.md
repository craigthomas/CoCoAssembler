# Yet Another Color Computer 3 Assembler / Disassembler 

## What is it?

This project is a Color Computer 3 assembler and disassembler written in
Python.

The Color Computer 3 is the third incarnation of the Tandy Radio Shack 
Color Computer line (TRS-80). The CoCo 3 offered several improvements over the
original CoCo 1 and CoCo 2, most notably the introduction of a memory
management unit (MMU) and a new Advanced Color Video Chip (ACVC) - also known
as the Graphics Interrupt Memory Enhancer (GIME). 

While the official name of the computer was the TRS-80 Color Computer 3,
the Color Computer family was quite different from the line of business 
machines such as the TRS-80 Model I, II, III, and 4. While that family
of computers used a Zilog Z80 microprocessor, the Color Computer family used 
a Motorola 6809E processor running at 0.89 MHz. 

## Current Status - May 27, 2013

The assembler is in its first phases of development, and is subject to
change. Check the documentation below for more information on how to use
it.

## Roadmap

Under construction.

## License

This project makes use of an MIT style license. Please see the file called 
LICENSE for more information.


## Installing

Simply copy the source files to a directory of your choice. In addition to
the source, you will need the following required software packages:

* [Python 2.7+ or 3](http://www.python.org)

I strongly recommend creating a virtual environment using the
[virtualenv](http://pypi.python.org/pypi/virtualenv) builder as well as the
[virtualenvwrapper](https://bitbucket.org/dhellmann/virtualenvwrapper) tools.


## Usage

The assembler is used to transform assembly language statements into 6809E
machine code. A source file of assembly language statments is broken up into a
number of columns:

    LABEL    OPERATION    OPERAND    COMMENT

Where each column contains the following:

* `LABEL` - a label to be applied to the operation or declaraion. A label may be 
composed of any alphanumeric characters, and can be any length. For example,
`START_ROUTINE` or `PRINT_21`.
* `OPERATION` - the operation to execute. For example, `ADDA`, `STX`, `LDY`.
* `OPERAND` - the data to apply to the operation. For example, `#$40`, `[$1234]`.
* `COMMENT` - a textual comment to be applied to the operation, can be any length
and is terminated by a newline character. For example, `Print out a string`.


## Further Documentation

The best documentation is in the code itself. Please feel free to examine the
code and experiment with it.
