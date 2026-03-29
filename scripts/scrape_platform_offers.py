from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
import yaml


HEADERS = {
    "User-Agent": "Mozilla/5.0"
} # 模拟浏览器访问，否则很多网站会拒绝请求


def fetch_text(url: str) -> str:
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    return soup.get_text(" ", strip=True)


def extract_discount_fold(text: str):
    """
    从页面文本中提取类似 1折 / 0.12折
    返回折数，例如 1.0、0.12
    """
    candidates = re.findall(r"(\d+(?:\.\d+)?)折", text)
    if not candidates:
        return None
    vals = [float(x) for x in candidates]
    return min(vals)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/platform_sources.yaml")
    parser.add_argument("--output", default="data/platform_offers.csv")
    args = parser.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    rows = []

    for item in cfg["platforms"]:
        name = item["name"]
        url = item["url"]
        try:
            text = fetch_text(url)
            fold = extract_discount_fold(text)
            rows.append({
                "platform": name,
                "discount_fold": fold if fold is not None else 1.0,
                "source_url": url,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            rows.append({
                "platform": name,
                "discount_fold": 1.0,
                "source_url": url,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    out = pd.DataFrame(rows)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(out)


if __name__ == "__main__":
    main()