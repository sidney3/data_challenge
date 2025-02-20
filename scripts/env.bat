@echo off
setlocal

:: Get first argument (environment tool)
set ENV_TOOL=%1
shift

:: Default Python and PIP commands
set PYTHON_CMD=python
set PIP_CMD=pip

:: Handle --python3 option
:parse_args
if "%~1"=="" goto end_parse_args
if "%~1"=="--python3" (
    set PYTHON_CMD=python3
    set PIP_CMD=pip3
)
shift
goto parse_args

:end_parse_args

:: Check if the environment tool is pyenv
if "%ENV_TOOL%"=="pyenv" (
    for /f "delims=" %%i in ('git rev-parse --show-toplevel') do set REPO_PATH=%%i
    for %%i in (%REPO_PATH%) do set REPO_NAME=%%~ni
    echo %REPO_NAME% %REPO_PATH%

    where pyenv >nul 2>nul
    if %errorlevel% neq 0 (
        echo pyenv is not installed. Please install pyenv-win first.
        exit /b 1
    )

    :: Initialize pyenv (assuming pyenv is already installed via pyenv-win)
    call pyenv init
    call pyenv virtualenv-init

    :: Get the required python version
    for /f "delims=" %%i in ('type scripts\.python-version') do set PYTHON_VERSION=%%i

    pyenv versions --bare | findstr /b "%PYTHON_VERSION%" >nul
    if %errorlevel% neq 0 (
        echo Python version %PYTHON_VERSION% not found, installing...
        pyenv install %PYTHON_VERSION%
    )
    pyenv shell %PYTHON_VERSION%

    set VENV_NAME=%REPO_NAME%
    pyenv virtualenvs | findstr "%VENV_NAME%" >nul
    if %errorlevel% neq 0 (
        echo Creating virtual environment %VENV_NAME%...
        pyenv virtualenv %PYTHON_VERSION% %VENV_NAME%
    )
    pyenv deactivate
    pyenv activate %VENV_NAME%
    echo Activated virtual environment %VENV_NAME%

    %PIP_CMD% install -U pip pip-tools
    pip-compile scripts\requirements.in
    pip-sync scripts\requirements.txt
) else if "%ENV_TOOL%"=="venv" (
    if not exist ".\.venv" (
        %PYTHON_CMD% -m venv .\.venv
        echo Created virtual environment.
    )

    call .\.venv\Scripts\activate
    echo Activated virtual environment.

    %PIP_CMD% install -U pip pip-tools
    pip-compile scripts\requirements.in
    pip-sync scripts\requirements.txt
) else (
    echo The selected environment tool is not supported: %ENV_TOOL%
    exit /b 1
)

:: Copy pre-commit config
copy scripts\.pre-commit-config-template.yaml .pre-commit-config.yaml
