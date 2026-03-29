from __future__ import annotations

import numpy as np
import pandas as pd


def annualized_return(nav: pd.Series) -> float:
    nav = nav.dropna()
    if len(nav) < 2:
        return np.nan
    years = (nav.index[-1] - nav.index[0]).days / 365.25
    if years <= 0:
        return np.nan
    return (nav.iloc[-1] / nav.iloc[0]) ** (1 / years) - 1


def annualized_volatility(returns: pd.Series) -> float:
    returns = returns.dropna()
    if len(returns) < 2:
        return np.nan
    return returns.std(ddof=0) * np.sqrt(252)


def max_drawdown(nav: pd.Series) -> float:
    nav = nav.dropna()
    if len(nav) < 2:
        return np.nan
    running_max = nav.cummax()
    dd = nav / running_max - 1.0
    return float(dd.min())


def sharpe_ratio(returns: pd.Series, rf_annual: float = 0.02) -> float:
    returns = returns.dropna()
    if len(returns) < 2:
        return np.nan
    rf_daily = (1 + rf_annual) ** (1 / 252) - 1
    excess = returns - rf_daily
    sd = excess.std(ddof=0)
    if sd == 0 or np.isnan(sd):
        return np.nan
    return float(np.sqrt(252) * excess.mean() / sd)


def monthly_win_rate(nav: pd.Series) -> float:
    nav = nav.dropna()
    if len(nav) < 2:
        return np.nan
    monthly = nav.resample("ME").last().pct_change().dropna()
    if len(monthly) == 0:
        return np.nan
    return float((monthly > 0).mean())


def to_returns(nav: pd.Series) -> pd.Series:
    return nav.pct_change().dropna()


def normalize_rank(df: pd.DataFrame, col: str, ascending: bool = False) -> pd.Series:
    """
    输出 0~1 的分位数排名，越大越好。
    """
    s = df[col]
    if ascending:
        return s.rank(pct=True, ascending=True)
    return s.rank(pct=True, ascending=False)