param (
    [string]$ENV_TOOL,
    [string]$PYTHON_CMD = "python",
    [string]$PIP_CMD = "pip"
)

# Handle --python3 option
if ($args -contains "--python3") {
    $PYTHON_CMD = "python3"
    $PIP_CMD = "pip3"
}

if ($ENV_TOOL -eq "venv") {
    if (-not (Test-Path ".\.venv")) {
        & $PYTHON_CMD -m venv .\.venv
        Write-Output "Created virtual environment."
    }

    # Activate venv
    .\.venv\Scripts\Activate.ps1
    Write-Output "Activated virtual environment."

    & $PIP_CMD install -U pip pip-tools
    pip-compile scripts\requirements.in
    pip-sync scripts\requirements.txt

} else {
    Write-Output "The selected environment tool is not supported: $ENV_TOOL"
    exit 1
}

# Copy pre-commit config
Copy-Item "scripts\.pre-commit-config-template.yaml" ".pre-commit-config.yaml"
Write-Output "Pre-commit config copied."
