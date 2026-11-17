"""Final paper: regime_analysis. See core/description.md."""
from __future__ import annotations

from collections import Counter
from typing import Any
import numpy as np
import pandas as pd
from collector.datalab.datalab_keyword_sets import KEYWORD_SETS
from config.research import DOMAIN_ORDER, DOMAIN_SPEC, EV_GROUP, MASS_TIE_RATIO, MIN_MAP_SHARE, TOP_TERMS, TRAIN_END
from util.research import sha256_bytes, text_hash


def build_domain_pairs() -> list[tuple[str, str, str]]:
    """(keyword, domain_slug, group_name). 긴 키워드 우선, 동률은 도메인 순서→키워드 사전순."""
    pairs: list[tuple[str, str, str]] = []
    for slug in DOMAIN_ORDER:
        seen: set[str] = set()
        for key, group_name in DOMAIN_SPEC[slug]["sources"]:
            for group in KEYWORD_SETS[key]:
                if group_name is not None and group["groupName"] != group_name:
                    continue
                for kw in group["keywords"]:
                    if kw not in seen:
                        seen.add(kw)
                        pairs.append((kw, slug, group["groupName"]))
    pairs.sort(key=lambda x: (-len(x[0]), DOMAIN_ORDER.index(x[1]), x[0]))
    return pairs


def dictionary_hash() -> str:
    return text_hash([f"{kw}|{slug}|{grp}" for kw, slug, grp in build_domain_pairs()])


def claim_terms(vocab: list[str]) -> dict[int, tuple[str, str]]:
    """어휘 열 번호 → (도메인, 그룹). 긴 키워드가 먼저 점유하고, 정확 일치 후 부분 일치(길이≥2)."""
    term_pos = {t: i for i, t in enumerate(vocab)}
    claimed: dict[int, tuple[str, str]] = {}
    for kw, slug, grp in build_domain_pairs():
        if kw in term_pos and term_pos[kw] not in claimed:
            claimed[term_pos[kw]] = (slug, grp)
        if len(kw) >= 2:
            for j, term in enumerate(vocab):
                if j not in claimed and kw in term:
                    claimed[j] = (slug, grp)
    return claimed


def map_topics(H: np.ndarray, vocab: list[str]) -> pd.DataFrame:
    """학습 H 행렬과 학습 어휘, 고정 키워드 사전만으로 토픽→국면을 결정한다.

    토픽 번호는 어떤 규칙에도 쓰이지 않는다. 입력은 (H, vocab) 둘뿐이다.
    규칙: 최고 도메인 질량 점유율 < MIN_MAP_SHARE → residual,
          2위/1위 질량비 ≥ MASS_TIE_RATIO → ambiguous, 그 외 → assigned.
    """
    claimed = claim_terms(vocab)
    by_domain: dict[str, list[int]] = {s: [] for s in DOMAIN_ORDER}
    for j, (slug, _grp) in claimed.items():
        by_domain[slug].append(j)
    rows: list[dict[str, Any]] = []
    for k in range(H.shape[0]):
        total = float(H[k].sum()) or 1.0
        masses = {s: float(H[k, idx].sum()) if idx else 0.0 for s, idx in by_domain.items()}
        ranked = sorted(masses.items(), key=lambda x: (-x[1], DOMAIN_ORDER.index(x[0])))
        (best_s, best_m), (second_s, second_m) = ranked[0], ranked[1]
        share = best_m / total
        ratio = second_m / best_m if best_m > 0 else float("nan")
        if best_m <= 0 or share < MIN_MAP_SHARE:
            status, slug_out = "residual", ""
            reason = f"최고 도메인({best_s}) 질량 점유율 {share:.4f} < {MIN_MAP_SHARE}"
        elif ratio >= MASS_TIE_RATIO:
            status, slug_out = "ambiguous", ""
            reason = f"1위 {best_s}/2위 {second_s} 질량비 {ratio:.3f} >= {MASS_TIE_RATIO}"
        else:
            status, slug_out = "assigned", best_s
            reason = f"{best_s} 질량 점유율 {share:.4f}, 2위/1위 {ratio:.3f}"
        # 최고 도메인 내부의 그룹 질량 (전기차배터리 등 한정 근거 식별용)
        grp_mass: Counter[str] = Counter()
        for j in by_domain[best_s]:
            grp_mass[claimed[j][1]] += float(H[k, j])
        dom_group = sorted(grp_mass.items(), key=lambda x: (-x[1], x[0]))[0][0] if grp_mass else ""
        claimed_top = sorted(by_domain[best_s], key=lambda j: (-float(H[k, j]), j))[:6]
        top_idx = np.lexsort((np.arange(H.shape[1]), -H[k]))[:TOP_TERMS]
        row: dict[str, Any] = {
            "topic": k,
            "status": status,
            "assigned_slug": slug_out,
            "assigned_label": DOMAIN_SPEC[slug_out]["label"] if slug_out else "",
            "best_slug": best_s,
            "best_mass": best_m,
            "best_share": share,
            "second_slug": second_s,
            "second_mass": second_m,
            "mass_ratio": ratio,
            "confidence": (1.0 - ratio) if status == "assigned" else float("nan"),
            "dominant_group": dom_group,
            "top_terms": ", ".join(vocab[j] for j in top_idx),
            "claimed_top_terms": ", ".join(vocab[j] for j in claimed_top),
            "reason": reason,
        }
        for s in DOMAIN_ORDER:
            row[f"mass_{s}"] = masses[s]
            row[f"share_{s}"] = masses[s] / total
        rows.append(row)
    return pd.DataFrame(rows)


def mapping_hash(df_map: pd.DataFrame) -> str:
    cols = [c for c in df_map.columns if c not in ("run_id",)]
    return sha256_bytes(df_map[cols].to_csv(index=False, float_format="%.10g").encode("utf-8"))


def domain_topics(df_map: pd.DataFrame) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {s: [] for s in DOMAIN_ORDER}
    for _, r in df_map[df_map["status"] == "assigned"].iterrows():
        out[r["assigned_slug"]].append(int(r["topic"]))
    return out


def domain_support(df_map: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """지원 상태. 미지원 국면은 비중 0이 아니라 unrepresented 로 표기한다."""
    topics = domain_topics(df_map)
    out: dict[str, dict[str, Any]] = {}
    for s in DOMAIN_ORDER:
        ks = topics[s]
        if not ks:
            cand = df_map[(df_map["best_slug"] == s) & (df_map["status"] != "assigned")]["topic"].astype(int).tolist()
            out[s] = {
                "status": "unrepresented",
                "topics": [],
                "note": "학습 H에서 임계값·모호성 규칙을 통과한 토픽 없음"
                + (f" (최고 후보였으나 residual/ambiguous: {cand})" if cand else ""),
            }
            continue
        groups = {str(df_map.loc[df_map["topic"] == k, "dominant_group"].iloc[0]) for k in ks}
        if s == "aichip" and groups == {EV_GROUP}:
            out[s] = {"status": "supported_ev_battery_only", "topics": ks,
                      "note": "지지 근거가 사전의 전기차배터리 그룹뿐이며 AI·반도체 직접 근거는 아님"}
        else:
            out[s] = {"status": "supported", "topics": ks, "note": f"우세 키워드 그룹: {sorted(groups)}"}
    return out


def build_regime_monthly(df_topic: pd.DataFrame, df_map: pd.DataFrame, run_id: str) -> pd.DataFrame:
    """share_d(m)=Σ_{k∈K_d} topic_k(m);  residual(m)=Σ_{k∈K_res} topic_k(m);  Σ_d share_d + residual = 1.
    미지원 국면은 NaN(비중 0이 아님). K_res = 미배정(residual/ambiguous) 토픽. Z는 학습 48개월 mean/std(ddof=1)."""
    topics = domain_topics(df_map)
    support = domain_support(df_map)
    res_topics = df_map[df_map["status"] != "assigned"]["topic"].astype(int).tolist()
    out = pd.DataFrame({"run_id": run_id, "month": df_topic["month"], "n_docs": df_topic["n_docs"],
                        "n_valid": df_topic["n_valid"]})
    out["period"] = np.where(out["month"] <= TRAIN_END, "train", "eval")
    for s in DOMAIN_ORDER:
        out[f"status_{s}"] = support[s]["status"]
    for s in DOMAIN_ORDER:
        ks = topics[s]
        out[f"share_{s}"] = df_topic[[f"topic_{k}" for k in ks]].sum(axis=1).to_numpy() if ks else np.nan
    out["residual_share"] = (df_topic[[f"topic_{k}" for k in res_topics]].sum(axis=1).to_numpy()
                             if res_topics else 0.0)
    comp = [f"share_{s}" for s in DOMAIN_ORDER if topics[s]] + ["residual_share"]
    assert np.allclose(out[comp].sum(axis=1), 1.0, atol=1e-9), "월별 비중 합이 1이 아님"
    tr = out["month"] <= TRAIN_END
    assert int(tr.sum()) == 48
    for s in DOMAIN_ORDER:
        if topics[s]:
            mu = float(out.loc[tr, f"share_{s}"].mean())
            sd = float(out.loc[tr, f"share_{s}"].std(ddof=1))
            out[f"z_{s}"] = (out[f"share_{s}"] - mu) / sd
        else:
            out[f"z_{s}"] = np.nan
    return out
