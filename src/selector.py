from __future__ import annotations

import numpy as np
import pandas as pd

from .data import fetch_fee_table, fetch_nav_history, fetch_overview, pct_to_float
from .metrics import (
    annualized_return,
    annualized_volatility,
    max_drawdown,
    monthly_win_rate,
    normalize_rank,
    sharpe_ratio,
    to_returns,
)


def screen_universe(df: pd.DataFrame, include_types: list[str], top_n: int = 200) -> pd.DataFrame:
    x = df.copy()
    if "类型" in x.columns and include_types:
        mask = False
        for t in include_types:
            mask = mask | x["类型"].astype(str).str.contains(t, na=False)
        x = x[mask].copy()

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


def build_one_record(code: str, amount_yuan: float = 100000, min_history_days: int = 252) -> dict | None:
    try:
        ov = fetch_overview(code)
        nav = fetch_nav_history(code)
        fee = fetch_fee_table(code, indicator="申购费率（前端）")
    except Exception:
        return None

    if nav is None or nav.empty or len(nav) < min_history_days:
        return None

    nav = nav.set_index("净值日期")
    nav_series = nav["单位净值"].astype(float)
    ret = to_returns(nav_series)

    info = parse_overview_row(ov)

    # 尽量把“运作成本”拆开
    annual_cost = sum(
        x for x in [info["management_fee"], info["custody_fee"], info["sales_fee"]]
        if x is not None and not np.isnan(x)
    ) if any(v is not None and not np.isnan(v) for v in [info["management_fee"], info["custody_fee"], info["sales_fee"]]) else np.nan

    record = {
        **info,
        "history_days": len(nav),
        "cagr": annualized_return(nav_series),
        "volatility": annualized_volatility(ret),
        "max_drawdown": max_drawdown(nav_series),
        "sharpe": sharpe_ratio(ret),
        "monthly_win_rate": monthly_win_rate(nav_series),
        "annual_cost": annual_cost,
        "front_fee_table_rows": len(fee) if fee is not None else 0,
    }
    return record


def rank_funds(records: list[dict], weights: dict) -> pd.DataFrame:
    df = pd.DataFrame([r for r in records if r is not None]).copy()
    if df.empty:
        return df

    # 费用越低越好，所以单独反向处理
    df["expense_proxy"] = df["annual_cost"].copy()
    df.loc[df["expense_proxy"].isna(), "expense_proxy"] = df["front_fee_max"]

    df["score"] = 0.0
    df["score"] += weights["cagr"] * normalize_rank(df, "cagr", ascending=False)
    df["score"] += weights["sharpe"] * normalize_rank(df, "sharpe", ascending=False)
    df["score"] += weights["max_drawdown"] * normalize_rank(df, "max_drawdown", ascending=False)
    df["score"] += weights["rating"] * normalize_rank(df, "5星评级家数", ascending=False)
    df["score"] += weights["expense"] * normalize_rank(df, "expense_proxy", ascending=True)
    df["score"] += weights["consistency"] * normalize_rank(df, "monthly_win_rate", ascending=False)

    out = df.sort_values("score", ascending=False).reset_index(drop=True)
    return out