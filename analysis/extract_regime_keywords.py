"""월별·연도별 활성 국면 키워드 프로파일링 스크립트.

NMF 토픽의 H 가중치와 keyword_monthly(월별 어휘 빈도)를 결합하여,
각 월에 활성화된(z >= active_z_threshold) 국면들의 핵심 상위 키워드를 추출한다.
산출:
- data/processed/regimes/regime_keywords_monthly.csv
- data/processed/regimes/regime_keywords_yearly.csv
"""

from pathlib import Path
import numpy as np
import pandas as pd

from config import load_config, project_root

ROOT = project_root()
CORPUS_DIR = ROOT / "data" / "processed" / "corpus"
REGIMES_DIR = ROOT / "data" / "processed" / "regimes"

VOCAB_PATH = CORPUS_DIR / "doc_term_vocab.csv"
H_PATH = REGIMES_DIR / "nmf_H.npy"
MAP_PATH = REGIMES_DIR / "topic_regime_map.csv"
REGIME_MONTHLY_PATH = REGIMES_DIR / "regime_monthly.csv"
KEYWORD_MONTHLY_PATH = CORPUS_DIR / "keyword_monthly.csv"

OUT_MONTHLY_PATH = REGIMES_DIR / "regime_keywords_monthly.csv"
OUT_YEARLY_PATH = REGIMES_DIR / "regime_keywords_yearly.csv"


def extract_keywords() -> tuple[pd.DataFrame, pd.DataFrame]:
    cfg = load_config()
    labels: list[str] = list(cfg["regimes"]["labels"])
    slugs: dict[str, str] = dict(cfg["regimes"]["slugs"])
    active_thresh = float(cfg["regimes"].get("active_z_threshold", 0.5))

    # 1. 어휘 및 H 로드
    vocab_df = pd.read_csv(VOCAB_PATH)
    vocab = vocab_df["term"].tolist()
    v_to_idx = {term: i for i, term in enumerate(vocab)}

    H = np.load(H_PATH)

    # 2. 토픽 -> 국면 매핑 로드
    mapping = pd.read_csv(MAP_PATH)
    topic_map: dict[str, list[int]] = {slugs[l]: [] for l in labels}
    for _, row in mapping.iterrows():
        r = row["regime"]
        if r in slugs:
            topic_map[slugs[r]].append(int(row["topic"]))

    H_regimes = {}
    for l in labels:
        s = slugs[l]
        topics = topic_map[s]
        H_regimes[s] = H[topics].sum(axis=0) if topics else np.zeros(H.shape[1])

    # 3. keyword_monthly 로드
    km = pd.read_csv(KEYWORD_MONTHLY_PATH)
    months = km["month"].tolist()
    n_docs = km["_n_docs"].to_numpy(dtype=float)

    km_words = [c for c in km.columns if c not in ["month", "_n_docs"]]
    km_word_indices = [v_to_idx[w] for w in km_words if w in v_to_idx]
    km_word_list = [w for w in km_words if w in v_to_idx]

    km_counts = km[km_word_list].to_numpy(dtype=float)
    km_freq = km_counts / n_docs[:, None]
    mean_freq = km_freq.mean(axis=0)
    mean_freq = np.where(mean_freq == 0, 1e-6, mean_freq)

    # 4. regime_monthly 로드 및 z점수 확인
    reg_df = pd.read_csv(REGIME_MONTHLY_PATH)
    slug_list = [slugs[l] for l in labels]
    share_cols = [f"share_{s}" for s in slug_list]
    shares = reg_df[share_cols].to_numpy(dtype=float)
    std = shares.std(axis=0, ddof=1)
    mean = shares.mean(axis=0)
    z = (shares - mean) / std

    monthly_rows = []
    for m_idx, m in enumerate(months):
        z_m = z[m_idx]
        active_indices = np.where(z_m >= active_thresh)[0]
        active_indices = active_indices[np.argsort(-z_m[active_indices])]

        ratio = km_freq[m_idx] / mean_freq
        for r_idx in active_indices:
            label = labels[r_idx]
            slug = slug_list[r_idx]
            z_val = z_m[r_idx]

            h_vec = H_regimes[slug][km_word_indices]
            score = h_vec * ratio
            top_k_indices = np.argsort(-score)[:7]
            top_words = [km_word_list[i] for i in top_k_indices]

            monthly_rows.append({
                "month": m,
                "year": m[:4],
                "regime": label,
                "slug": slug,
                "z_score": round(float(z_val), 3),
                "top_keywords": ", ".join(top_words),
            })

    out_monthly = pd.DataFrame(monthly_rows)

    # 5. 연도별 집계
    yearly_rows = []
    for year in sorted(list(set(m[:4] for m in months))):
        sub = out_monthly[out_monthly["year"] == year]
        reg_counts = sub["regime"].value_counts()

        y_m_indices = [i for i, m in enumerate(months) if m.startswith(year)]
        y_ratio = km_freq[y_m_indices].mean(axis=0) / mean_freq

        top_regimes_str = ", ".join(f"{r}({c}개월)" for r, c in reg_counts.items())

        regime_keywords_summary = []
        for reg, count in reg_counts.items():
            slug = slugs[reg]
            h_vec = H_regimes[slug][km_word_indices]
            score = h_vec * y_ratio
            top_words = [km_word_list[i] for i in np.argsort(-score)[:5]]
            regime_keywords_summary.append(f"[{reg}] " + ", ".join(top_words))

        yearly_rows.append({
            "year": year,
            "active_months_total": len(sub),
            "top_regimes": top_regimes_str,
            "regime_keywords": " | ".join(regime_keywords_summary),
        })

    out_yearly = pd.DataFrame(yearly_rows)
    return out_monthly, out_yearly


def main() -> None:
    print("국면별 키워드 추출 중...")
    out_monthly, out_yearly = extract_keywords()
    out_monthly.to_csv(OUT_MONTHLY_PATH, index=False, encoding="utf-8-sig")
    out_yearly.to_csv(OUT_YEARLY_PATH, index=False, encoding="utf-8-sig")
    print(f"완료:")
    print(f"  월별 키워드: {OUT_MONTHLY_PATH} ({len(out_monthly)}행)")
    print(f"  연도별 요약: {OUT_YEARLY_PATH} ({len(out_yearly)}행)")


if __name__ == "__main__":
    main()
