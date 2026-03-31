from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml
from tqdm import tqdm

from src.data import fetch_fee_table, fetch_universe
from src.platform_cost import load_platform_offers
from src.selector import build_one_record, rank_funds, screen_universe


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))

    amount_yuan = cfg["holding"]["amount_yuan"]
    holding_days = cfg["holding"]["days"]
    min_history_days = cfg["universe"]["min_history_days"]
    weights = cfg["scoring"]["weights"]

    universe = fetch_universe()
    universe = screen_universe(universe, top_n=200)

    records = []
    for code in tqdm(universe["代码"].tolist(), desc="Building fund records"):
        rec = build_one_record(code, amount_yuan=amount_yuan, min_history_days=min_history_days)
        if rec is not None:
            rec["5星评级家数"] = (
                int(universe.loc[universe["代码"] == code, "5星评级家数"].iloc[0])
                if "5星评级家数" in universe.columns else None
            )
            rec["fund_code"] = code
            records.append(rec)

    ranked = rank_funds(records, weights=weights, amount_yuan=amount_yuan, holding_days=holding_days)
    if ranked.empty:
        print("No valid funds found.")
        return

    platform_df = load_platform_offers(cfg["platforms_csv"])

    output_path = Path(cfg["output_csv"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ranked.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("\n=== Top funds ===")
    cols = ["code", "name", "type", "score", "front_fee", "annual_cost", "expense_proxy", "cagr", "sharpe", "max_drawdown", "monthly_win_rate"]
    print(ranked[cols].head(args.topn).to_string(index=False))

    print(f"\nSaved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()