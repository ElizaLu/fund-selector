from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from .data import pct_to_float


def load_platform_offers(csv_path: str) -> pd.DataFrame:
    p = Path(csv_path)
    if not p.exists():
        return pd.DataFrame(columns=["platform", "discount_fold", "source_url", "updated_at"])
    df = pd.read_csv(p)
    if "discount_fold" not in df.columns:
        df["discount_fold"] = 1.0
    return df


def _parse_amount_range(text: str):
    """
    解析类似：
    - 小于100万元
    - 大于等于100万元，小于200万元
    - 大于等于500万元
    返回 (low_yuan, high_yuan)
    """
    s = str(text)

    low = 0.0
    high = float("inf")

    m = re.search(r"大于等于(\d+(?:\.\d+)?)万元", s)
    if m:
        low = float(m.group(1)) * 10000

    m = re.search(r"小于(\d+(?:\.\d+)?)万元", s)
    if m:
        high = float(m.group(1)) * 10000

    m = re.search(r"大于(\d+(?:\.\d+)?)万元", s)
    if m:
        low = max(low, float(m.group(1)) * 10000)

    m = re.search(r"(\d+(?:\.\d+)?)万元以上", s)
    if m:
        low = max(low, float(m.group(1)) * 10000)

    return low, high


def estimate_front_fee(fee_df: pd.DataFrame, amount_yuan: float) -> float:
    """
    估算某个平台/某份费率表下的前端申购费。
    优先读取 '天天基金优惠费率'，其次 '原费率'，再其次 '费用'。
    """
    if fee_df is None or fee_df.empty:
        return float("nan")

    df = fee_df.copy()

    amount_col = None
    for c in ["适用金额", "条件或名称", "条件"]:
        if c in df.columns:
            amount_col = c
            break

    rate_col = None
    for c in ["天天基金优惠费率", "原费率", "费用"]:
        if c in df.columns:
            rate_col = c
            break

    if amount_col is None or rate_col is None:
        return float("nan")

    df["_low"] = 0.0
    df["_high"] = float("inf")
    for i, row in df.iterrows():
        low, high = _parse_amount_range(row[amount_col])
        df.at[i, "_low"] = low
        df.at[i, "_high"] = high

    matched = df[(amount_yuan >= df["_low"]) & (amount_yuan < df["_high"])]
    if matched.empty:
        matched = df

    row = matched.iloc[0]
    rate = row[rate_col]

    # 固定金额
    if isinstance(rate, str) and ("每笔" in rate or "元" in rate and "%" not in rate):
        m = re.search(r"(\d+(?:\.\d+)?)", rate)
        return float(m.group(1)) if m else 0.0

    pct = pct_to_float(rate)
    if pct is None:
        return float("nan")

    return amount_yuan * pct


def best_platform_cost(fee_df: pd.DataFrame, platform_df: pd.DataFrame, amount_yuan: float) -> pd.DataFrame:
# fee_df	某一只基金的费率表	来自 akshare
# platform_df	各平台的折扣信息
    base_fee = estimate_front_fee(fee_df, amount_yuan)
    if pd.isna(base_fee):
        return pd.DataFrame()

    rows = []
    for _, r in platform_df.iterrows():
        fold = float(r.get("discount_fold", 1.0))
        # 1折 => 0.1 倍原费率；0.12折 => 0.012 倍
        factor = fold / 10.0 if fold > 1 else fold
        rows.append({
            "platform": r.get("platform"),
            "discount_fold": fold,
            "estimated_fee": base_fee * factor,
            "source_url": r.get("source_url", ""),
            "updated_at": r.get("updated_at", "") # 更新时间
        })

    out = pd.DataFrame(rows).sort_values("estimated_fee", ascending=True)
    return out