# VSETH Rechtssammlung

## Prerequisites

 - make
 - Python 3.10 (for `match`)
 - TexLive
 - latexmk
 - inkscape

## Compilation

Just run `make` in the base directory.

## Adding a new regulation

 1. Create a new XML file. Use `00_example.xml` as a reference.
 2. Check for syntax errors by running `make xx_my_new_regulation.chk`.
 3. If all is well, add the file to `SRCS` in `Makefile`, as well as an entry in `index.xml`.
 4. Compile everything: `make all`.
 5. Report any errors that you cannot fix to https://gitlab.ethz.ch/vseth/0100-Reglemente/reglemente/-/issues
