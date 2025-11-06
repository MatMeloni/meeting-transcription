"""Shim module to expose backend entry-points as python app.py."""

from backend import API_APP, CONFIG, CONTROLLER  # noqa: F401
from backend.cli import run_cli


if __name__ == "__main__":
    run_cli(CONTROLLER)
