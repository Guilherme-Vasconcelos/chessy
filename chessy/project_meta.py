import tomllib
from pathlib import Path
from typing import TypedDict

_project_root = Path(__file__).resolve().parent.parent
# Be careful if changing this, as not all files are present after project is packaged
# (see `poetry build`).
assert (_project_root / "LICENSE.txt").exists()


class _PoetryPyprojectData(TypedDict):
    version: str
    authors: list[str]


class _ToolPyprojectData(TypedDict):
    poetry: _PoetryPyprojectData


class _PyprojectData(TypedDict):
    tool: _ToolPyprojectData


def _read_pyproject() -> _PyprojectData:
    pyproject_path = _project_root / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        toml_data: _PyprojectData = tomllib.load(f)  # type: ignore
        return toml_data


_poetry_data = _read_pyproject()["tool"]["poetry"]


def read_project_version() -> str:
    return _poetry_data["version"]


def read_project_authors() -> list[str]:
    return _poetry_data["authors"]
