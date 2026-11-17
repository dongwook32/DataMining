"""Recalculate appendix checks from the frozen local inputs without editing them."""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from core.v4 import build_domain_pairs, dictionary_hash
from core.robustness.verify_search_robustness import moving_block_bootstrap_corr
from collector.datalab.datalab_keyword_sets import ANCHOR_GROUP, regime_groups, sub_groups

DATA = ROOT / "data/processed"
BASE = DATA / "phase5_6_artifacts/RUN_PHASE5_6_20261027_184959"
REGIME = DATA / "reactions/phase5_6_train_only_regime_monthly.csv"
MONTH = DATA / "panel/monthly_panel.csv"
SUPP = DATA / "supplemental_validation"
PAIRS = [
    ("macro", "macro_combined"), ("macro", "macro_interest"), ("macro", "macro_inflation"),
    ("realestate", "realestate"), ("aichip", "aichip"), ("market", "market"),
    ("earnings", "earnings"), ("capital", "capital"),
]


def sha256(path):
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest().upper()


def check_model():
    meta = json.loads((BASE / "core_meta.json").read_text(encoding="utf-8"))
    assert dictionary_hash() == meta["dictionary_sha256"]
    assert meta["counts"]["duplicate_article_id_removed"] == 0
    assert meta["vocab_size"] == 22193
    assert meta["n_fit_sample"] == 144000
    assert sha256(DATA / "corpus/news_corpus.parquet") == (
        "D351C7807D5CFE89DE40186A10396FDC6A4C24C73BDB4CBD917935A585B3BC36"
    )
    assert sha256(MONTH) == "B12ADD8D7083953893D2D7B10A0DB037C830CE4D145D29AA6112E13A60A36C6B"
    assert np.load(BASE / "nmf_H.npy").shape == (14, 22193)
    domain = pd.DataFrame(build_domain_pairs(), columns=["keyword", "domain", "group"])
    assert len(domain) == 139
    domain.to_csv(HERE / "S5_domain_dictionary.csv", index=False, encoding="utf-8-sig")
    requests = {
        "period": ["2016-01-01", "2026-07-31"],
        "time_unit_for_table_13": "date",
        "anchor": ANCHOR_GROUP,
        "regime_groups": regime_groups(),
        "sub_groups": [
            {"regime": regime, **group} for regime, group in sub_groups()
        ],
    }
    for level in ("regime", "sub"):
        daily = pd.read_csv(ROOT / f"data/raw/datalab/datalab_{level}_daily.csv")
        actual = daily[["group", "keywords"]].drop_duplicates().set_index("group")["keywords"].to_dict()
        configured = {
            group["groupName"]: "|".join(group["keywords"])
            for group in requests[f"{level}_groups"]
        }
        assert actual == configured, f"Stored DataLab requests differ for {level}"
    (HERE / "S7_search_groups.json").write_text(
        json.dumps(requests, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("S2-S5 PASS: input hashes, basis dimensions, sample counts, dictionary hash")
    print("S7 PASS: all 7 regime and 28 subgroup definitions match the collected daily CSVs")


def check_monthly():
    data = pd.read_csv(REGIME).merge(pd.read_csv(MONTH), on="month", validate="one_to_one")
    regimes = ("macro", "capital", "realestate", "market", "aichip", "earnings")
    scores = data[[f"z_{regime}" for regime in regimes]]
    active = scores.ge(0.5).sum(axis=1)
    counts = (len(active), int(active.ge(2).sum()), int(active.sum()), int((active - 1).clip(lower=0).sum()))
    assert counts == (67, 39, 112, 49)
    result = sm.OLS(data["kospi_ret_std"], sm.add_constant(scores)).fit(
        cov_type="HAC", cov_kwds={"maxlags": 3}
    )
    np.testing.assert_array_equal(result.params.iloc[1:].round(4), [
        -0.7418, -0.5299, -0.2082, -0.1437, -0.2583, -0.1143,
    ])
    adjusted = multipletests(result.pvalues.iloc[1:], method="holm")[1]
    np.testing.assert_array_equal(adjusted.round(4), [0.0024, 0.0129, 0.3155, 0.3289, 0.3289, 0.5008])
    assert round(result.rsquared, 4) == 0.1619
    print(f"S6 PASS: Table 8 {counts}, Table 10 R2={result.rsquared:.10f}")


def check_weekly():
    week = pd.read_csv(SUPP / "news_search_weekly_panel.csv")
    expected = pd.read_csv(SUPP / "news_search_hac_results.csv")
    assert len(week) == 292
    results = []
    for split, panel in (("Full", week), ("Train", week[week.period == "train"]),
                         ("Eval", week[week.period == "eval"])):
        diff = panel.select_dtypes("number").diff()
        rows = []
        for regime, group in PAIRS:
            for lag in (-1, 0, 1):
                pair = pd.concat([
                    diff[f"news_share_{regime}"], diff[f"search_{group}"].shift(-lag),
                ], axis=1).dropna()
                standardized = (pair - pair.mean()) / pair.std()
                fit = sm.OLS(standardized.iloc[:, 1], sm.add_constant(standardized.iloc[:, 0])).fit(
                    cov_type="HAC", cov_kwds={"maxlags": 4}
                )
                rows.append((regime, f"search_{group}", lag, len(pair), fit.params.iloc[1], fit.pvalues.iloc[1]))
        result = pd.DataFrame(rows, columns=["regime", "search_group", "lag_h", "n", "r", "p"])
        result["adjusted"] = multipletests(result["p"], method="holm")[1]
        check = result.merge(
            expected[expected["split"].str.startswith(split)],
            on=["regime", "search_group", "lag_h"], validate="one_to_one",
        )
        assert len(check) == 24
        np.testing.assert_array_equal(check["n"], check["sample_n"])
        np.testing.assert_array_equal(check["r"].round(4), check["pearson_r"])
        np.testing.assert_allclose(check["adjusted"], check["hac_p_holm"], atol=1e-12, rtol=0)
        results.append((split, len(check), (check["adjusted"] - check["hac_p_holm"]).abs().max()))
    print(f"S7-S8 PASS: 72 HAC tests, max absolute adjusted p differences {results}")


def check_table_14():
    week = pd.read_csv(SUPP / "news_search_weekly_panel.csv")
    diff = week[week["period"].eq("eval")].select_dtypes("number").diff()
    expected = {
        "search_market": ([0.0339, 0.0432, 0.0616], (0.2079, 0.6367)),
        "search_earnings": ([0.0015, 0.0011, 0.0011], (0.2989, 0.5986)),
        "search_macro_interest": ([0.3367, 0.3575, 0.5251], (0.1315, 0.5054)),
    }
    tests = []
    for regime, group in PAIRS:
        for lag in (-1, 0, 1):
            x = diff[f"news_share_{regime}"]
            y = diff[f"search_{group}"].shift(-lag)
            pair = pd.concat([x, y], axis=1).dropna()
            tests.append((f"search_{group}", lag, (pair - pair.mean()) / pair.std()))

    for column, maxlags in enumerate((2, 4, 8)):
        p_values = []
        for _, _, sample in tests:
            fit = sm.OLS(sample.iloc[:, 1], sm.add_constant(sample.iloc[:, 0])).fit(
                cov_type="HAC", cov_kwds={"maxlags": maxlags}
            )
            p_values.append(fit.pvalues.iloc[1])
        for (group, lag, _), adjusted in zip(tests, multipletests(p_values, method="holm")[1]):
            if lag == 0 and group in expected:
                assert round(adjusted, 4) == expected[group][0][column]

    for group, lag, sample in tests:
        if lag == 0 and group in expected:
            interval = moving_block_bootstrap_corr(
                sample.iloc[:, 0].to_numpy(), sample.iloc[:, 1].to_numpy(), block_length=4
            )
            endpoints = tuple(round(interval[key], 4) for key in ("ci95_lower", "ci95_upper"))
            assert endpoints == expected[group][1]
    print("S7 PASS: Table 14 nine Holm p-values and six 4-week bootstrap endpoints")


if __name__ == "__main__":
    check_model()
    check_monthly()
    check_weekly()
    check_table_14()
