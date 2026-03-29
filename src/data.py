from __future__ import annotations

import re
import time
from typing import Optional

import akshare as ak
import pandas as pd


def _pause():
    time.sleep(0.35)


def clean_code(x: object) -> str:
    m = re.search(r"\d{6}", str(x))
    if not m:
        raise ValueError(f"Cannot parse fund code from: {x}")
    return m.group(0) # 返回第一个括号里的内容


def pct_to_float(v):
    """
    '1.20%' -> 0.012
    0.0012 -> 0.0012
    '0.12折' -> 0.012
    """
    if v is None:
        return None
    if isinstance(v, float) and pd.isna(v):
        return None
    if isinstance(v, (int, float)):
        return float(v) if abs(v) < 1 else float(v) / 100.0

    s = str(v).strip().replace("—", "").replace("-", "")
    if not s:
        return None

    m = re.search(r"(-?\d+(?:\.\d+)?)\s*%", s) #匹配小数+%
    if m:
        return float(m.group(1)) / 100.0

    m = re.search(r"(-?\d+(?:\.\d+)?)\s*折", s)
    if m:
        return float(m.group(1)) / 10.0

    m = re.search(r"(-?\d+(?:\.\d+)?)", s)
    return float(m.group(1)) if m else None


def fetch_universe() -> pd.DataFrame:
    df = ak.fund_rating_all().copy()
    df["代码"] = df["代码"].astype(str).apply(clean_code)
    return df


def fetch_overview(code: str) -> pd.DataFrame:
    _pause()
    return ak.fund_overview_em(symbol=code).copy() # 因为有时返回的是view，通过代码code查询


def fetch_nav_history(code: str) -> pd.DataFrame:
    _pause()
    df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势").copy()
    df["净值日期"] = pd.to_datetime(df["净值日期"])
    df = df.sort_values("净值日期").reset_index(drop=True)
    return df


def fetch_fee_table(code: str, indicator: str = "申购费率（前端）") -> pd.DataFrame:
    _pause()
    return ak.fund_fee_em(symbol=code, indicator=indicator).copy()