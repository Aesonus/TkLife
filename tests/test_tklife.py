try:
    import tomllib
except ImportError:
    import tomli as tomllib

import pathlib

import tklife


def test_version_matches_pyproject():
    """Ensure that the version in __init__.py matches pyproject.toml."""
    pyproject = pathlib.Path("pyproject.toml")
    pyproject_toml = tomllib.loads(pyproject.read_text())
    assert tklife.__version__ == pyproject_toml["tool"]["poetry"]["version"]
