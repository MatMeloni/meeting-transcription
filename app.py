"""Shim module to expose src.app entry-points as python app.py."""

from src.app import API_APP, CONFIG, ORCHESTRATOR, _running_with_streamlit, main_cli  # noqa: F401


if __name__ == "__main__" and not _running_with_streamlit():
    main_cli(ORCHESTRATOR)
