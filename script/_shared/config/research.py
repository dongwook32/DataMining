"""Final v4 research design. Keep these constants fixed for paper replication."""
import datetime as dt
from typing import Any

MODEL_SPECS = {
    "h1": [("zero", "Zero 기준선"), ("ar2_exp", "[확장창] AR(2)"), ("news_exp", "[확장창] AR(2)+News"),
           ("ar2_fix", "[고정창] AR(2)"), ("news_fix", "[고정창] AR(2)+News")],
    "h2": [("zero", "Zero-change 기준선"), ("ar1_exp", "[확장창] AR(1)"), ("news_exp", "[확장창] AR(1)+News"),
           ("ar1_fix", "[고정창] AR(1)"), ("news_fix", "[고정창] AR(1)+News")],
}
ACTUAL_COL = {"h1": "actual_kospi_ret", "h2": "actual_base_rate_diff"}

SCRIPT_VERSION = "5.6.0-v4"
KST = dt.timezone(dt.timedelta(hours=9), "KST")
TRAIN_END = "2024-12"
EVAL_START = "2025-01"
EVAL_END = "2026-07"
STUDY_START = "2021-01"
MIN_DF = 200
MAX_DF_RATIO = 0.15
TOP_N_VOCAB = 30_000
N_TOPICS = 14
PER_MONTH_SAMPLE = 3000
SEED = 42
NMF_MAX_ITER = 400
NMF_INIT = "nndsvd"
NMF_SOLVER = "cd"
BATCH = 50_000
MIN_MAP_SHARE = 0.01
MASS_TIE_RATIO = 0.90
TOP_TERMS = 25
EXPECTED_COUNTS = {"raw": 931_709, "train": 643_095, "eval": 288_614, "fit_sample": 144_000}
DOMAIN_SPEC: dict[str, dict[str, Any]] = {
    "macro": {"label": "금리·물가", "sources": [("물가", None), ("금리", None)]},
    "realestate": {"label": "부동산", "sources": [("부동산", None)]},
    "hhdebt": {"label": "가계대출", "sources": [("가계대출", None)]},
    "trade": {"label": "대외통상", "sources": [("대외통상", None)]},
    "aichip": {"label": "AI·반도체", "sources": [("AI반도체", None)]},
    "market": {"label": "시황", "sources": [("증시실적", "국내증시"), ("증시실적", "해외주식")]},
    "earnings": {"label": "기업실적", "sources": [("증시실적", "기업실적")]},
    "capital": {"label": "자본거래", "sources": [("증시실적", "공모주")]},
}
DOMAIN_ORDER = list(DOMAIN_SPEC)
H1_DOMAIN = "hhdebt"
H2_DOMAIN = "macro"
EV_GROUP = "전기차배터리"
