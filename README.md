# Fund Selector

A research-oriented fund selection pipeline for quantitative investment analysis.

This project provides a modular workflow for retrieving fund data, engineering fund-level features, evaluating risk-adjusted performance, and ranking candidate funds using a configurable scoring framework.

## Overview

The repository is designed as a practical fund screening system. It combines market-data ingestion, feature computation, cost-related processing, and weighted ranking to produce a ranked list of candidate funds for further analysis.

The workflow is intended to be transparent and easy to extend. It can be used for:

- fund universe screening
- performance and risk evaluation
- cost-aware comparison
- ranking and shortlist generation
- empirical analysis of selection rules

## Main Workflow

The pipeline typically performs the following steps:

1. fetches a fund universe
2. filters the universe to keep relevant candidates
3. collects fund overview information
4. downloads NAV history
5. computes performance and risk metrics
6. estimates cost-related quantities
7. applies a weighted ranking model
8. exports the ranked result to CSV

## Repository Structure

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

## Modules

### `src/data.py`
Data access and preprocessing utilities.

This module handles:
- fund universe and rating data
- fund overview data
- NAV history retrieval
- fee-related data
- parsing helpers for codes, percentages, and numeric values

### `src/metrics.py`
Performance and risk metrics.

Typical utilities include:
- annualized return
- annualized volatility
- maximum drawdown
- Sharpe ratio
- monthly win rate
- return conversion helpers
- rank normalization

### `src/platform_cost.py`
Utilities for reading and processing platform discount or offer information from CSV files.

### `src/selector.py`
Core fund selection logic.

This module is responsible for:
- universe filtering
- fund record construction
- metric aggregation
- cost estimation
- weighted ranking

### `run.py`
Entry point for the full workflow.

It connects the data loading, metric computation, selection, ranking, and export steps into a single executable pipeline.

## Scoring Framework

The ranking system combines multiple factors rather than relying on a single metric. The current configuration includes components such as:

- `cagr`
- `sharpe`
- `max_drawdown`
- `rating`
- `expense`
- `consistency`

The scoring logic is configurable through `config.yaml`, which makes it easy to compare different ranking strategies or adjust the emphasis of each component.

## Data Requirements

The project uses internet-accessible fund data through Akshare and may also rely on local CSV files.

Typical inputs include:
- a fund universe with ratings and fee-related fields
- NAV history for each fund
- platform offer data in CSV format

The default configuration references:
- `data/platform_offers.csv`
- `outputs/ranked_funds.csv`

## Configuration

The main settings are stored in `config.yaml`.

Common configuration items include:
- minimum history length
- ranking weights
- holding period
- investment amount
- platform offer CSV path
- output CSV path

Keeping these parameters in a config file makes it easier to run experiments without changing the source code.

## Installation

Install the required dependencies:

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

## Usage

Run the pipeline from the repository root:

```bash
python run.py --config config.yaml
```

The script will:
- load the configuration
- build fund records
- calculate metrics
- rank the candidate funds
- save the output to the configured CSV path

## Output

The final output is a ranked CSV table that can be used for:

- further analysis
- shortlist creation
- portfolio screening
- benchmark comparison
- manual review

Typical columns may include:
- fund code
- fund name
- fund type
- composite score
- fee proxy fields
- annualized return
- Sharpe ratio
- maximum drawdown
- monthly win rate

## Extending the Project

The current implementation can be extended in several directions:

- add backtesting
- introduce train/validation/test splits over time
- compare alternative ranking rules
- incorporate transaction costs
- test different holding horizons
- analyze factor exposure
- add visualization and reporting
- log experiments for reproducibility

## Notes

- The data source depends on Akshare and external market-data availability.
- Some fields may be unavailable for certain funds or time periods.
- Local CSV inputs should follow the format expected by the code in `src/platform_cost.py`.
- The output directory should exist or be created before running the pipeline.

## License

Add a license file before public release.
