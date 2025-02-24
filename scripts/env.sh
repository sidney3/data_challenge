#!/bin/bash

ENV_TOOL=$1
shift

PYTHON_CMD="python"
PIP_CMD="pip"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --python3)
            PYTHON_CMD="python3"
            PIP_CMD="pip3"
            ;;
        *) 
            echo "Unknown python alias: $1"
            ;;
    esac
    shift
done

if [ $ENV_TOOL = "pyenv" ]; then
    REPO_PATH=$(git rev-parse --show-toplevel)
    REPO_NAME=$(basename "$REPO_PATH")
    echo $REPO_NAME $REPO_PATH

    if command -v pyenv 1>/dev/null 2>&1; then
        eval "$(pyenv init --path)"
        eval "$(pyenv init -)"
    else
        echo "pyenv is not installed. install pyenv first."
        exit 1
    fi

    if command -v pyenv virtualenv 1>/dev/null 2>&1; then
        eval "$(pyenv virtualenv-init -)"
    else
        echo "pyenv virtualenv is not installed. install pyenv-virtualenv first."
    fi

    PYTHON_VERSION=$(cat scripts/.python-version)

    # Install python version
    if pyenv versions --bare | grep -q "^${PYTHON_VERSION}$"; then
        echo "python version $PYTHON_VERSION is already installed."
    else
        pyenv install $PYTHON_VERSION
        echo "installed python version $PYTHON_VERSION."
    fi
    pyenv shell $PYTHON_VERSION

    VENV_NAME="$REPO_NAME"
    if pyenv virtualenvs | grep -q $VENV_NAME; then
        echo "virtual environment $VENV_NAME already exists."
    else
        pyenv virtualenv $PYTHON_VERSION $VENV_NAME
        echo "created virtual environment $VENV_NAME."
    fi
    pyenv deactivate
    pyenv activate $VENV_NAME
    echo "activated virtual environment $VENV_NAME."

    $PIP_CMD install -U pip pip-tools
    pip-compile scripts/requirements.in
    pip-sync scripts/requirements.txt
elif [ $ENV_TOOL = "venv" ]; then
    if [ ! -d "./.venv" ]; then
        $PYTHON_CMD -m venv .venv
        echo "created virtual environment."
    fi

    source ./.venv/bin/activate
    echo "activated virtual environment."

    $PIP_CMD install -U pip pip-tools
    pip-compile --verbose scripts/requirements.in
    pip-sync scripts/requirements.txt
else
    echo "the selected environment tool is not supported: $1."
fi

cp scripts/.pre-commit-config-template.yaml .pre-commit-config.yaml
