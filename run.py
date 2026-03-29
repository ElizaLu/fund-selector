from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml
from tqdm import tqdm

from src.data import fetch_universe
from src.platform_cost import load_platform_offers, best_platform_cost
from src.selector import build_one_record, rank_funds, screen_universe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--topn", type=int, default=20)
    parser.add_argument("--amount", type=float, default=None)
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    amount_yuan = args.amount or cfg["holding"]["amount_yuan"]
    include_types = cfg["universe"]["include_types"]
    min_history_days = cfg["universe"]["min_history_days"]
    weights = cfg["scoring"]["weights"]

    universe = fetch_universe()
    universe = screen_universe(universe, include_types=include_types, top_n=200)

    records = []
    for code in tqdm(universe["代码"].tolist(), desc="Building fund records"):
        rec = build_one_record(code, amount_yuan=amount_yuan, min_history_days=min_history_days)
        if rec is not None:
            # 保留原始评分列，方便回溯
            rec["5星评级家数"] = int(universe.loc[universe["代码"] == code, "5星评级家数"].iloc[0]) if "5星评级家数" in universe.columns else None
            rec["fund_code"] = code
            records.append(rec)

    ranked = rank_funds(records, weights=weights)
    if ranked.empty:
        print("No valid funds found.")
        return

    # 平台费率表
    platform_df = load_platform_offers(cfg["platforms_csv"])
    
    out_dir = Path("outputs")
    out_dir.mkdir(exist_ok=True)
    ranked.to_csv(cfg["output_csv"], index=False, encoding="utf-8-sig")

    print("\n=== Top funds ===")
    print(ranked[["code", "name", "type", "score", "cagr", "sharpe", "max_drawdown", "monthly_win_rate"]].head(args.topn).to_string(index=False))

    if not platform_df.empty:
        print("\n=== Cheapest platforms by current discount table ===")
        first_code = ranked.iloc[0]["code"]
        from src.data import fetch_fee_table
        fee_df = fetch_fee_table(first_code, indicator="申购费率（前端）")
        cost_rank = best_platform_cost(fee_df, platform_df, amount_yuan=amount_yuan)
        if not cost_rank.empty:
            print(cost_rank.head(10).to_string(index=False))


if __name__ == "__main__":
    main()