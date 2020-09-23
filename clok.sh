#!/usr/bin/env bash


PYTHON_BIN=/home/bigjake/.local/share/virtualenvs/timeclok-zahqZ-lK
# Edit this ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ path to be
# the path of your virtual environments python binary.

WORKING_DIR=~/Projects/timeclok
# Edit this ^^^^^^^^^^^^^^^^^^^^ to be the location of your timeclok directory

# Call program and forward all command line arguments
$PYTHON_BIN/bin/python  $WORKING_DIR/clok.py "$@"

