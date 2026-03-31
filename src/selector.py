from __future__ import annotations

import re
import numpy as np
import pandas as pd
import traceback

from .data import fetch_nav_history, fetch_overview, pct_to_float
from .metrics import (
    annualized_return,
    annualized_volatility,
    max_drawdown,
    monthly_win_rate,
    normalize_rank,
    sharpe_ratio,
    to_returns,
)
def screen_universe(df: pd.DataFrame, top_n: int = 200) -> pd.DataFrame:
    x = df.copy()

    if "5星评级家数" in x.columns:
        x["5星评级家数"] = pd.to_numeric(x["5星评级家数"], errors="coerce").fillna(0)

    if "手续费" in x.columns:
        x["手续费_num"] = pd.to_numeric(x["手续费"], errors="coerce")

    sort_cols = [c for c in ["5星评级家数", "手续费_num"] if c in x.columns]
    if sort_cols:
        x = x.sort_values(sort_cols, ascending=[False, True][:len(sort_cols)])

    return x.head(top_n).reset_index(drop=True)


def parse_overview_row(ov: pd.DataFrame) -> dict:
    row = ov.iloc[0].to_dict()

    return {
        "name": row.get("基金简称"),
        "full_name": row.get("基金全称"),
        "code": str(row.get("基金代码", "")).split("（")[0],
        "type": row.get("基金类型"),
        "management_fee": pct_to_float(row.get("管理费率")),
        "custody_fee": pct_to_float(row.get("托管费率")),
        "sales_fee": pct_to_float(row.get("销售服务费率")),
        "front_fee_max": pct_to_float(row.get("最高认购费率")),
        "benchmark": row.get("业绩比较基准"),
        "tracking": row.get("跟踪标的"),
    }

def sum_valid(values):
    valid = []
    for v in values:
        if v is None:
            continue
        try:
            if np.isnan(v):
                continue
        except Exception:
            continue
        valid.append(float(v))
    return sum(valid) if valid else np.nan


import re
import numpy as np

def extract_effective_fee(text):
    if text is None:
        return np.nan

    text = str(text)

    # 1️⃣ 优先找“优惠费率”
    match_discount = re.search(r"优惠费率[:：]?\s*([0-9.]+)%", text)
    if match_discount:
        return float(match_discount.group(1)) / 100

    # 2️⃣ 没有优惠 → 找第一个百分比（通常就是原始费率）
    match_normal = re.search(r"([0-9.]+)%", text)
    if match_normal:
        return float(match_normal.group(1)) / 100

    return np.nan

def build_one_record(code: str, amount_yuan: float = 100000, min_history_days: int = 252) -> dict | None:
    try:
        ov = fetch_overview(code)
        nav = fetch_nav_history(code)
        fee = extract_effective_fee(ov.get("最高认购费率", None))
        # print("最高认购费率:", ov.get("最高认购费率", None))
    except Exception as e:
        print("发生错误：", e)
        traceback.print_exc()
        return None

    if nav is None or nav.empty or len(nav) < min_history_days:
        return None

    nav = nav.set_index("净值日期")
    nav_series = nav["单位净值"].astype(float)
    ret = to_returns(nav_series)

    info = parse_overview_row(ov)

    annual_cost = sum_valid([
        info["management_fee"],
        info["custody_fee"],
        info["sales_fee"],
    ])

    front_fee = fee * amount_yuan

    record = {
        **info,
        "history_days": len(nav),
        "cagr": annualized_return(nav_series),
        "volatility": annualized_volatility(ret),
        "max_drawdown": max_drawdown(nav_series),
        "sharpe": sharpe_ratio(ret),
        "monthly_win_rate": monthly_win_rate(nav_series),
        "annual_cost": annual_cost,
        "front_fee": front_fee,
    }
    return record

def rank_funds(records: list[dict], weights: dict, amount_yuan: float, holding_days: int) -> pd.DataFrame:
    df = pd.DataFrame([r for r in records if r is not None]).copy()
    if df.empty:
        return df

    holding_years = holding_days / 365.25

    df["front_fee"] = pd.to_numeric(df["front_fee"], errors="coerce")
    df["annual_cost"] = pd.to_numeric(df["annual_cost"], errors="coerce")

    # 用于打分的成本代理：买入一次性成本 + 持有期间持续成本
    front_median = df["front_fee"].median(skipna=True)
    annual_median = df["annual_cost"].median(skipna=True)

    df["expense_proxy"] = (
        df["front_fee"].fillna(front_median) +
        df["annual_cost"].fillna(annual_median) * amount_yuan * holding_years
    )

    df["score"] = 0.0
    df["score"] += weights["cagr"] * normalize_rank(df, "cagr", ascending=False)
    df["score"] += weights["sharpe"] * normalize_rank(df, "sharpe", ascending=False)
    df["score"] += weights["max_drawdown"] * normalize_rank(df, "max_drawdown", ascending=False)
    df["score"] += weights["rating"] * normalize_rank(df, "5星评级家数", ascending=False)
    df["score"] += weights["expense"] * normalize_rank(df, "expense_proxy", ascending=True)
    df["score"] += weights["consistency"] * normalize_rank(df, "monthly_win_rate", ascending=False)

    return df.sort_values("score", ascending=False).reset_index(drop=True)