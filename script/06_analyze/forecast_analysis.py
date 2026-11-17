"""Final paper: forecast_analysis. See core/description.md."""
from __future__ import annotations

from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
import statsmodels.api as sm
from config.research import EVAL_END, EVAL_START, STUDY_START
from config.research import ACTUAL_COL, MODEL_SPECS
from util.research import is_nan


def _design(df: pd.DataFrame, ycol: str, xcol: str, ny: int, nx: int, end: int, news: bool) -> tuple[pd.DataFrame, pd.Series]:
    start = max(ny, nx)
    rows = []
    for i in range(start, end):
        r = {"y": df[ycol].iloc[i]}
        for L in range(1, ny + 1):
            r[f"y_lag{L}"] = df[ycol].iloc[i - L]
        if news:
            for L in range(1, nx + 1):
                r[f"x_lag{L}"] = df[xcol].iloc[i - L]
        rows.append(r)
    d = pd.DataFrame(rows)
    return sm.add_constant(d.drop(columns="y"), has_constant="add"), d["y"]


def _predict(df: pd.DataFrame, t: int, ycol: str, xcol: str, ny: int, nx: int, news: bool, end: int) -> float:
    """end=학습에 쓰는 마지막 행의 다음 위치(확장창은 end=t, 고정창은 end=평가 시작 위치)."""
    X, y = _design(df, ycol, xcol, ny, nx, end, news)
    res = sm.OLS(y, X).fit()
    val = float(res.params["const"])
    for L in range(1, ny + 1):
        val += float(res.params[f"y_lag{L}"]) * float(df[ycol].iloc[t - L])
    if news:
        for L in range(1, nx + 1):
            val += float(res.params[f"x_lag{L}"]) * float(df[xcol].iloc[t - L])
    return val


def run_forecasts(df_regime: pd.DataFrame, panel_path: Path, run_id: str, h1_col: str, h2_col: str,
                  ok_h1: bool, ok_h2: bool) -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = pd.read_csv(panel_path, dtype={"month": str})
    df = df_regime.merge(panel[["month", "kospi_ret", "base_rate_diff"]], on="month", how="inner")
    df = df[(df["month"] >= STUDY_START) & (df["month"] <= EVAL_END)].sort_values("month").reset_index(drop=True)
    ev = df[(df["month"] >= EVAL_START) & (df["month"] <= EVAL_END)]["month"].tolist()
    assert len(ev) == 19, f"평가월 {len(ev)}개"
    i0 = int(df.index[df["month"] == EVAL_START][0])
    recs = []
    for m in ev:
        t = int(df.index[df["month"] == m][0])
        a1, a2 = float(df["kospi_ret"].iloc[t]), float(df["base_rate_diff"].iloc[t])
        nan = float("nan")
        p = {
            "h1_ar2_exp": _predict(df, t, "kospi_ret", h1_col, 2, 2, False, t),
            "h1_news_exp": _predict(df, t, "kospi_ret", h1_col, 2, 2, True, t) if ok_h1 else nan,
            "h1_ar2_fix": _predict(df, t, "kospi_ret", h1_col, 2, 2, False, i0),
            "h1_news_fix": _predict(df, t, "kospi_ret", h1_col, 2, 2, True, i0) if ok_h1 else nan,
            "h2_ar1_exp": _predict(df, t, "base_rate_diff", h2_col, 1, 1, False, t),
            "h2_news_exp": _predict(df, t, "base_rate_diff", h2_col, 1, 1, True, t) if ok_h2 else nan,
            "h2_ar1_fix": _predict(df, t, "base_rate_diff", h2_col, 1, 1, False, i0),
            "h2_news_fix": _predict(df, t, "base_rate_diff", h2_col, 1, 1, True, i0) if ok_h2 else nan,
        }
        rec: dict[str, Any] = {
            "run_id": run_id, "forecast_month": m, "last_available_obs_month": df["month"].iloc[t - 1],
            "actual_kospi_ret": a1, "h1_zero_pred": 0.0,
            "h1_ar2_exp_pred": p["h1_ar2_exp"], "h1_news_exp_pred": p["h1_news_exp"],
            "h1_ar2_fix_pred": p["h1_ar2_fix"], "h1_news_fix_pred": p["h1_news_fix"],
            "actual_base_rate_diff": a2, "h2_zero_pred": 0.0,
            "h2_ar1_exp_pred": p["h2_ar1_exp"], "h2_news_exp_pred": p["h2_news_exp"],
            "h2_ar1_fix_pred": p["h2_ar1_fix"], "h2_news_fix_pred": p["h2_news_fix"],
        }
        recs.append(rec)
    out = pd.DataFrame(recs)
    for tag, act in (("h1", "actual_kospi_ret"), ("h2", "actual_base_rate_diff")):
        for name in ("zero", "ar2_exp" if tag == "h1" else "ar1_exp", "news_exp",
                     "ar2_fix" if tag == "h1" else "ar1_fix", "news_fix"):
            out[f"{tag}_{name}_error"] = out[f"{tag}_{name}_pred"] - out[act]
    return out, df


def cont_metrics(pred: np.ndarray, actual: np.ndarray) -> dict[str, float]:
    if np.isnan(pred).any():
        return {"rmse": float("nan"), "mae": float("nan"), "bias": float("nan")}
    e = pred - actual
    return {"rmse": float(np.sqrt(np.mean(e ** 2))), "mae": float(np.mean(np.abs(e))), "bias": float(np.mean(e))}


def class_metrics(pred: np.ndarray, actual: np.ndarray) -> dict[str, Any] | None:
    if np.isnan(pred).any():
        return None
    pos, neg = actual < 0, actual >= 0
    pp, pn = pred < 0, pred >= 0
    tp, fp = int((pos & pp).sum()), int((neg & pp).sum())
    fn, tn = int((pos & pn).sum()), int((neg & pn).sum())
    n, n_pos, n_neg = len(actual), int(pos.sum()), int(neg.sum())
    ids = (tp + fn == n_pos, tn + fp == n_neg, tp + tn == int((pos & pp).sum() + (neg & pn).sum()),
           tp + tn + fp + fn == n)
    rec = tp / (tp + fn) if (tp + fn) else float("nan")
    prec = tp / (tp + fp) if (tp + fp) else float("nan")
    spec = tn / (tn + fp) if (tn + fp) else float("nan")
    bal = (rec + spec) / 2 if not (is_nan(rec) or is_nan(spec)) else float("nan")
    return {"tp": tp, "tn": tn, "fp": fp, "fn": fn, "hits": tp + tn, "n": n, "n_pos": n_pos, "n_neg": n_neg,
            "recall": rec, "precision": prec, "specificity": spec, "balanced": bal, "identities_ok": all(ids)}


def compute_all_metrics(df_f: pd.DataFrame) -> dict[str, Any]:
    m: dict[str, Any] = {"n": len(df_f)}
    for tag in ("h1", "h2"):
        act = df_f[ACTUAL_COL[tag]].to_numpy()
        for key, _ in MODEL_SPECS[tag]:
            m[f"{tag}_{key}"] = cont_metrics(df_f[f"{tag}_{key}_pred"].to_numpy(), act)
    act1 = df_f["actual_kospi_ret"].to_numpy()
    n = len(df_f)
    m["class"] = {
        "always_pos": class_metrics(np.ones(n), act1), "always_neg": class_metrics(-np.ones(n), act1),
        "exp_base": class_metrics(df_f["h1_ar2_exp_pred"].to_numpy(), act1),
        "exp_news": class_metrics(df_f["h1_news_exp_pred"].to_numpy(), act1),
        "fix_base": class_metrics(df_f["h1_ar2_fix_pred"].to_numpy(), act1),
        "fix_news": class_metrics(df_f["h1_news_fix_pred"].to_numpy(), act1),
    }
    return m
