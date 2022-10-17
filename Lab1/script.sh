#!/usr/bin/env bash
set -e

WORKDIR=$(cd "$(dirname "$0")" && pwd)
export WORKDIR


VENV=$(realpath "$PWD")/venv
if [[ ! -d $VENV ]]; then
    virtualenv -p python3 "$VENV" || python3 -m venv "$VENV"
fi

activate_venv() {
    # shellcheck source=/dev/null
    source "$WORKDIR/venv/bin/activate"
}

# Source code dependencies
echo "Installing dependencies"
activate_venv && pip3 install -r requirements.txt

echo "Starting script"
activate_venv && python3 aws_basic_setup.py
