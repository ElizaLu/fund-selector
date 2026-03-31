from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from .data import pct_to_float


def load_platform_offers(csv_path: str) -> pd.DataFrame:
    p = Path(csv_path)
    if not p.exists():
        return pd.DataFrame(columns=["platform", "discount_factor", "source_url", "updated_at"])

    df = pd.read_csv(p)

    # 推荐你在 CSV 里直接用 discount_factor：
    # 0.10 表示 1折，0.08 表示 0.8折
    if "discount_factor" not in df.columns:
        if "discount_fold" in df.columns:
            # 兼容旧字段：discount_fold 按“几折”理解，1 -> 0.1，8 -> 0.8
            df["discount_factor"] = pd.to_numeric(df["discount_fold"], errors="coerce") / 10.0
        else:
            df["discount_factor"] = 1.0

    df["discount_factor"] = pd.to_numeric(df["discount_factor"], errors="coerce").fillna(1.0)
    return df