#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"/..
python3 -m venv backend/.venv
. backend/.venv/bin/activate
pip install --upgrade pip
pip install -e "backend[dev]"
echo "Backend virtualenv created in backend/.venv and dependencies installed."
