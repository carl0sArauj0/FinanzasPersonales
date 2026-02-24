"""Runtime stub for streamlit_gsheets used when the real package isn't installed.

This allows the application to run in environments where the external
`streamlit-gsheets` package isn't available. Replace with the real
package when installing from its source.
"""
from typing import Any
import pandas as pd


class GSheetsConnection:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    def read(self, worksheet: str, ttl: int = 0) -> pd.DataFrame:
        return pd.DataFrame()

    def update(self, worksheet: str, data: pd.DataFrame) -> None:
        return None
