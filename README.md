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
machine code. A source file of assembly language statements is broken up into a
number of columns:

    LABEL    OPERATION    OPERAND    # COMMENT

Where each column contains the following:

* `LABEL` - a label to be applied to the operation or declaraion. A label may be 
composed of any alphanumeric characters, and can be any length.
* `OPERATION` - the operation to execute. 
* `OPERAND` - the data to apply to the operation. 
* `COMMENT` - a textual comment to be applied to the operation, can be any length
and is terminated by a newline character. 

A full example would be:

    BUFFER  EQU     $6100           # START OF BUFFER
    BUFFEND EQU     $7FFF           # END OF BUFFER
    START   LDY     #$0FF00         # LOAD INPUT PIA ADDRESS
            LDX     #BUFFER         # LOAD BUFFER PNTR ADDRESS
    INP000  LDB     #10             # SELECT RIGHT,X
            JSR     $A9A2           # SELECT SUBROUTINE

To run the assembler:

    python coco3asm.py input_file -o output_file

This will assemble the instructions found in file `input_file` and will generate the
associated CoCo machine instructions in binary format in `output_file`. Additional
options include printing the symbol table:

    python coco3asm.py test.asm -s

Which will have the following output:

   -- Symbol Table --
   BUFFER          $6100
   START           $6000
   INP000          $6007
   BUFFEND         $7FFF

Print out the assembled version of the input:

    python chip8asm/chip8asm.py test.asm -p

Which will have the following output:

    -- Assembled Statements --
    6000 108E FF00  START   LDY         #$0FF00  # LOAD INPUT PIA ADDRESS
    6004   8E 6100          LDX         #BUFFER  # LOAD BUFFER PNTR ADDRESS
    6007   C6   0A INP000   LDB             #10  # SELECT RIGHT,X
    6009   BD A9A2          JSR           $A9A2  # SELECT SUBROUTINE

## Further Documentation

The best documentation is in the code itself. Please feel free to examine the
code and experiment with it.
