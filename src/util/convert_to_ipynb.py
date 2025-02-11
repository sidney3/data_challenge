from __future__ import annotations

import json
import re
from itertools import dropwhile

INSTALLS = """
!pip install sortedcontainers uvloop websockets pandas numpy
"""

IMPORTS = """
from __future__ import annotations

import asyncio
import contextlib
import copy
import json
import time
import traceback
import urllib.request
from abc import ABC
from abc import abstractmethod
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any

import nest_asyncio
import uvloop
import websockets
from sortedcontainers import SortedDict

nest_asyncio.apply()
"""

PY_FILES = [
    "src/gt_trading_client/config/order.py",
    "src/gt_trading_client/user_portfolio.py",
    "src/gt_trading_client/raw_orderbook.py",
    "src/gt_trading_client/filtered_orderbook.py",
    "src/gt_trading_client/shared_state.py",
    "src/gt_trading_client/strategy.py",
    "src/gt_trading_client/websocket_client.py",
    "src/gt_trading_client/trading_client.py",
    "src/gt_trading_client/prioritizer.py",
    "src/test_strategy.py",
    "src/main.py",
]


def remove_top_imports(code: str) -> str:
    """
    Removes import statements from the top of a Python script.
    Keeps inline imports inside functions or classes.

    Parameters:
    - code (str): The content of a Python file.

    Returns:
    - str: The cleaned code with top-level imports removed.
    """
    lines = code.splitlines()
    new_lines = []

    for line in lines:
        if (
            not re.match(
                r"^\s*(import|from)\s+[\w\.]+(\s+import\s+\w+(,\s*\w+)*)?", line
            )
        ) and (not re.match(r"^\s*if\s+TYPE_CHECKING\s*:", line)):
            new_lines.append(line)

    new_lines = list(dropwhile(lambda x: x.strip() == "", new_lines))

    return "\n".join(new_lines)


def convert_py_to_ipynb(output_notebook: str = "main.ipynb") -> None:
    """
    Converts all Python source files in a directory into a Jupyter Notebook (.ipynb).

    Parameters:
    - output_notebook (str): The output notebook filename.
    """
    notebook = {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 4}

    notebook["cells"].append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": INSTALLS.splitlines(keepends=True),
        }
    )

    notebook["cells"].append(
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": IMPORTS.splitlines(keepends=True),
        }
    )

    for py_file in PY_FILES:
        with open(py_file, encoding="utf-8") as f:
            code = f.read()

        code = remove_top_imports(code=code)

        notebook["cells"].append(
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": code.splitlines(keepends=True),
            }
        )

    with open(output_notebook, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)

    print(f"Notebook '{output_notebook}' created successfully!")


if __name__ == "__main__":
    convert_py_to_ipynb()
