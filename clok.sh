#!/usr/bin/env bash

VENV_LOC=".venv_location"
WORKING_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
if [[ ! -f $VENV_LOC ]]; then
  touch $VENV_LOC
  pipenv --venv > $VENV_LOC
fi

VENV="$(cat $VENV_LOC)"
if [[ -f "$VENV/bin/python" ]]; then
  PYTHON="$VENV/bin/python"
elif [[ -f "$VENV/Scripts/python.exe" ]]; then
  PYTHON="$VENV/Scripts/python.exe"
fi


echo "venv_loc: $VENV_LOC"
echo "working_dir: $WORKING_DIR"
echo "venv: $VENV"
echo "python: $PYTHON"
# Call program and forward all command line arguments
$PYTHON  $WORKING_DIR/clok.py "$@"

