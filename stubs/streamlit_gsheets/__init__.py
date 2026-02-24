"""Minimal stub for streamlit_gsheets to satisfy import resolution in-editor.

This provides a tiny `GSheetsConnection` class with the methods used
by the project (`read` and `update`). It does not implement real
Google Sheets functionality — use only for editor/linter resolution
when the real package isn't installable.
"""
from typing import Any
import pandas as pd


class GSheetsConnection:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def read(self, worksheet: str, ttl: int = 0) -> pd.DataFrame:
        # Return an empty DataFrame as a safe default for static checks
        return pd.DataFrame()

    def update(self, worksheet: str, data: pd.DataFrame) -> None:
        # No-op stub for editor/linter
        return None
