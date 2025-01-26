#!/bin/bash

if [ "$1" = "venv" ]; then
    if [ ! -d "./.venv" ]; then
        python -m venv .venv
        echo "created virtual environment."
    fi

    source ./.venv/bin/activate
    echo "activated virtual environment."

    pip install -U pip pip-tools
    pip-compile scripts/requirements.in
    pip-sync scripts/requirements.txt
else
    echo "the selected environment tool is not supported: $1."
fi

cp scripts/.pre-commit-config-template.yaml .pre-commit-config.yaml
