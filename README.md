# Fund Selector

A research-oriented **fund selection and ranking system** for quantitative investment analysis.  
This repository combines **market-data ingestion**, **fund-level feature engineering**, **risk-adjusted performance evaluation**, and a **weighted ranking framework** to produce a ranked list of candidate funds.

> The project is intentionally framed as more than a utility script.  
> It is designed as a reproducible decision-support pipeline that can be used to study **selection under uncertainty**, **multi-criteria ranking**, **cost-aware portfolio screening**, and **data-driven financial decision making**.

---

## Why this project is valuable for PhD applications

This repository supports a strong academic narrative in areas such as:

- **Quantitative finance**
- **Machine learning for decision systems**
- **Multi-criteria optimization**
- **Risk-aware asset selection**
- **Financial data engineering**
- **Reproducible empirical research**

For a PhD application, the value of this project is not just in the final ranked output. The stronger contribution is that it shows you can:

- define an evaluation problem,
- build a data pipeline,
- turn raw market information into measurable signals,
- combine multiple objectives into a transparent scoring rule,
- and structure the code so it can be extended into a research benchmark.

---

## Project overview

The current pipeline does the following:

1. fetches a fund universe,
2. screens the universe to keep the most relevant candidates,
3. builds a record for each fund using overview and NAV history,
4. computes performance and risk metrics,
5. estimates cost-related quantities,
6. applies a weighted ranking model,
7. saves the final ranked table to CSV.

This is a useful research pattern because it transforms a noisy practical problem into a **structured ranking task**.

---

## Repository structure

```text
fund-selector/
├── config.yaml
├── requirements.txt
├── run.py
├── src/
│   ├── data.py
│   ├── metrics.py
│   ├── platform_cost.py
│   └── selector.py
└── scripts/
```

---

## Core modules

### `src/data.py`
Data access and preprocessing utilities.  
This module uses **Akshare** to retrieve:

- fund ratings / universe data,
- fund overview data,
- fund NAV history,
- and fee tables.

It also includes parsing helpers for codes, percentages, and numeric conversion.

### `src/metrics.py`
Performance and risk metrics, including:

- annualized return,
- annualized volatility,
- maximum drawdown,
- Sharpe ratio,
- monthly win rate,
- return conversion utilities,
- rank normalization.

### `src/platform_cost.py`
Helpers for reading platform discount / offer information from CSV.

### `src/selector.py`
The main selection logic:

- filters the fund universe,
- extracts overview information,
- computes fund-level records,
- estimates cost proxies,
- and ranks funds using a weighted score.

### `run.py`
The entry script that connects the full workflow and writes the ranked results to disk.

---

## Methodological idea

The project is built around **multi-objective fund selection** rather than a single metric.  
Each candidate fund is evaluated through a combination of:

- **expected historical performance**,
- **risk-adjusted return**,
- **drawdown behavior**,
- **analyst / rating information**,
- **cost sensitivity**,
- and **consistency of monthly performance**.

This is academically useful because it reflects how real decision systems work: they must trade off multiple objectives under uncertainty.

---

## Scoring framework

The current configuration uses a weighted score with components such as:

- `cagr`
- `sharpe`
- `max_drawdown`
- `rating`
- `expense`
- `consistency`

This kind of formulation is attractive in research because it is:

- interpretable,
- configurable,
- easy to ablate,
- and easy to compare against alternative ranking strategies.

---

## Data requirements

The project expects internet-accessible fund data via Akshare and may also rely on local CSV inputs.

Typical inputs include:

- a fund universe with ratings and fee-related fields,
- NAV history for each fund,
- platform offer data in CSV format.

The configuration file currently points to:

- `data/platform_offers.csv`
- `outputs/ranked_funds.csv`

---

## Configuration

The main configuration is stored in `config.yaml`.

It currently controls:

- minimum history length,
- ranking weights,
- holding period,
- investment amount,
- platform offer CSV path,
- and output CSV path.

This is a strong design choice for research code because it separates **experiment settings** from **implementation**.

---

## Installation

Install the dependencies listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

The project currently depends on packages such as:

- `akshare`
- `pandas`
- `numpy`
- `scipy`
- `pyyaml`
- `requests`
- `beautifulsoup4`
- `lxml`
- `scikit-learn`
- `tqdm`

---

## Usage

Run the main pipeline from the repository root:

```bash
python run.py --config config.yaml
```

The script will build fund records, rank the candidates, and save the ranked table to the configured output path.

---

## Output

The output is a ranked CSV table that can be used for:

- further analysis,
- portfolio construction,
- comparison with benchmark strategies,
- or manual fund screening.

Typical columns include:

- fund code,
- fund name,
- fund type,
- composite score,
- fee proxies,
- annualized return,
- Sharpe ratio,
- maximum drawdown,
- and monthly win rate.

---

## Research framing for PhD applications

When describing this project in a CV, statement of purpose, or email to a supervisor, the strongest framing is:

> I built a cost-aware, risk-adjusted fund selection pipeline that integrates market data retrieval, feature engineering, and interpretable ranking to support financial decision making.

That sentence works well because it emphasizes:

- **problem formulation**,
- **method design**,
- **empirical evaluation**,
- and **decision relevance**.

A more technical framing could be:

> The project implements a modular, data-driven ranking system for mutual fund screening, using historical NAV series, fee structures, and rank-normalized performance metrics to produce interpretable candidate rankings.

---

## Why this is more than a trading script

This repository is a good PhD-level portfolio item because it can grow into a research platform for:

- **ablation studies**  
  Compare alternative weighting schemes and metric combinations.

- **benchmarking**  
  Compare against heuristic screening, factor models, or machine-learning rankers.

- **robustness analysis**  
  Test different holding horizons, market regimes, and history-length thresholds.

- **explainability**  
  Study which metrics drive the final ranking and how sensitive results are to each term.

- **decision theory**  
  Reinterpret the ranking as a constrained optimization or utility maximization problem.

---

## Possible extensions

To strengthen the project for academic or PhD use, consider adding:

- a backtesting module,
- train/validation/test splits over time,
- benchmark strategies,
- transaction-cost modeling,
- risk-parity or utility-based ranking,
- factor exposure analysis,
- visualization dashboards,
- experiment logging,
- and reproducible reports.

---

## Suggested wording for academic applications

You can describe the project as:

- “a quantitative fund selection framework”
- “a cost-aware ranking pipeline for asset screening”
- “a reproducible empirical finance system”
- “a multi-criteria decision model for investment selection”
- “a modular research baseline for data-driven portfolio screening”

These phrases sound significantly stronger than “fund selector,” while still being accurate.

---

## Environment

Refer to `requirements.txt` for the exact package list.  
The project may also require:

- internet access for Akshare data retrieval,
- a valid local data directory,
- and CSV inputs for platform offer information.

---

## License

Add a license file before public release.
