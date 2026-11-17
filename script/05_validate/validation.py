"""Final paper: validation. See core/description.md."""
from __future__ import annotations

import inspect
import json
import re
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from config.research import DOMAIN_ORDER, EVAL_START, EXPECTED_COUNTS, H1_DOMAIN, H2_DOMAIN, MASS_TIE_RATIO, MAX_DF_RATIO, MIN_DF, MIN_MAP_SHARE, NMF_INIT, NMF_MAX_ITER, N_TOPICS, SEED, STUDY_START, TOP_N_VOCAB, TRAIN_END
from core.forecast_analysis import _predict
from config.research import ACTUAL_COL, MODEL_SPECS
from util.research import arr_hash, is_nan, text_hash
from core.regime_analysis import build_domain_pairs, domain_topics, map_topics, mapping_hash


def _chk(status: bool | None, detail: str, **ev: Any) -> dict[str, Any]:
    return {"status": "PASS" if status is True else "FAIL" if status is False else "INSUFFICIENT EVIDENCE",
            "detail": detail, "evidence": ev}


def independent_mapping(H: np.ndarray, vocab: list[str]) -> list[tuple[str, str, float]]:
    """map_topics 와 다른 구현(어휘 중심 점유)으로 (status, slug, best_mass)를 다시 계산한다."""
    pairs = build_domain_pairs()
    owner: list[str | None] = []
    for term in vocab:
        hit = None
        for kw, slug, _g in pairs:
            if kw == term or (len(kw) >= 2 and kw in term):
                hit = slug
                break
        owner.append(hit)
    own = np.array([o if o else "" for o in owner])
    res = []
    for k in range(H.shape[0]):
        total = H[k].sum()
        masses = [(float(H[k][own == s].sum()), i, s) for i, s in enumerate(DOMAIN_ORDER)]
        masses.sort(key=lambda x: (-x[0], x[1]))
        (bm, _, bs), (sm_, _, _s2) = masses[0], masses[1]
        if bm <= 0 or bm / total < MIN_MAP_SHARE:
            res.append(("residual", "", bm))
        elif sm_ / bm >= MASS_TIE_RATIO:
            res.append(("ambiguous", "", bm))
        else:
            res.append(("assigned", bs, bm))
    return res


def pre_md_checks(ctx: dict[str, Any]) -> dict[str, Any]:
    meta, H, vocab = ctx["meta"], ctx["H"], ctx["vocab"]
    art = ctx["art_dir"]
    checks: dict[str, Any] = {}
    c = meta["counts"]

    ec = EXPECTED_COUNTS
    ok = (c["raw_rows"], c["train_docs"], c["eval_docs"], meta["n_fit_sample"]) == (ec["raw"], ec["train"], ec["eval"], ec["fit_sample"])
    checks["01_데이터 표본 수"] = _chk(ok, f"원본 {c['raw_rows']:,}, 학습 {c['train_docs']:,}, 평가 {c['eval_docs']:,}, 적합 표본 {meta['n_fit_sample']:,} "
                                    f"(기대 {ec['raw']:,}/{ec['train']:,}/{ec['eval']:,}/{ec['fit_sample']:,})", counts=c)

    vdf = pd.read_csv(art / "vocab_idf.csv", encoding="utf-8-sig")
    terms = vdf["term"].astype(str).tolist()
    ordered = all((vdf["df_train"].iloc[i], terms[i]) is not None for i in range(1)) and \
        all((-int(vdf["df_train"].iloc[i]), terms[i]) <= (-int(vdf["df_train"].iloc[i + 1]), terms[i + 1]) for i in range(len(vdf) - 1))
    rules = bool((vdf["df_train"] >= MIN_DF).all() and (vdf["df_train"] / c["train_docs"] <= MAX_DF_RATIO).all()
                 and len(vdf) <= TOP_N_VOCAB)
    ok = ordered and rules and meta["df_docs_max_month"] <= TRAIN_END and meta["n_df_docs"] == c["train_docs"] \
        and text_hash(terms) == meta["vocab_sha256"] and terms == vocab
    checks["02_어휘·DF 학습기간 한정과 정렬 규칙"] = _chk(ok, f"DF 계산 기사 {meta['n_df_docs']:,}건, 최대 월 {meta['df_docs_max_month']}, "
                                                    f"저장된 어휘표에서 DF 규칙 {rules}, (−DF,토큰) 정렬 {ordered}, 해시 일치", vocab_size=len(terms))

    sid = pd.read_csv(art / "fit_sample_ids.csv", dtype=str)
    ok = bool((sid["month"] <= TRAIN_END).all()) and len(sid) == meta["n_fit_sample"] and sid["article_id"].is_unique \
        and text_hash(sid["article_id"].tolist()) == meta["sample_ids_sha256"] and meta["idf_independent_recompute_maxdiff"] < 1e-5
    checks["03_IDF 적합 표본(학습기간) 및 IDF 독립 재계산"] = _chk(
        ok, f"표본 {len(sid):,}건 월 범위 {sid['month'].min()}~{sid['month'].max()}, 표본 DF로 재계산한 IDF 최대 차 {meta['idf_independent_recompute_maxdiff']:.2e}")

    ok = H.shape == (N_TOPICS, len(vocab)) and bool((H >= 0).all()) and meta["nmf_params"].get("max_iter") == NMF_MAX_ITER \
        and meta["nmf_params"].get("init") == NMF_INIT and meta["nmf_params"].get("random_state") == SEED \
        and meta["nmf_params"].get("n_components") == N_TOPICS and meta["n_fit_sample"] == len(sid)
    conv = meta["nmf_converged_no_warning"]
    checks["04_NMF 적합 입력과 설정"] = _chk(ok, f"H {H.shape}, 비음수, 파라미터 {meta['nmf_params']}, 반복 {meta['nmf_n_iter']}, 수렴 경고 없음={conv}",
                                          converged=conv)

    ok = meta["H_sha256"] == meta["H_sha256_after_transform"] and meta["idf_sha256"] == meta["idf_sha256_after_transform"]
    checks["05_평가기간 기사는 transform만 적용(H·IDF 불변)"] = _chk(ok, "전량 transform 전후 H·IDF 해시 동일")

    H_disk = np.load(art / "nmf_H.npy")
    ok_h = arr_hash(H_disk) == meta["H_sha256"]
    df_map = ctx["df_map"]
    ind = independent_mapping(H_disk, terms)
    same = all(ind[k][0] == df_map.loc[df_map["topic"] == k, "status"].iloc[0]
               and ind[k][1] == ("" if pd.isna(df_map.loc[df_map["topic"] == k, "assigned_slug"].iloc[0])
                                else str(df_map.loc[df_map["topic"] == k, "assigned_slug"].iloc[0]))
               and abs(ind[k][2] - float(df_map.loc[df_map["topic"] == k, "best_mass"].iloc[0])) < 1e-6 * max(1.0, abs(ind[k][2]))
               for k in range(N_TOPICS))
    params = list(inspect.signature(map_topics).parameters)
    ok = ok_h and same and params == ["H", "vocab"]
    checks["06_매핑이 학습 H·학습 어휘·고정 사전만 사용하고 독립 구현과 일치"] = _chk(
        ok, f"저장된 H(해시 일치 {ok_h})와 저장된 어휘로 다른 구현이 14개 토픽 판정·질량을 재현 {same}; map_topics 인자 {params}")

    sig = {k: (df_map.loc[df_map["topic"] == k, "status"].iloc[0], df_map.loc[df_map["topic"] == k, "assigned_slug"].iloc[0])
           for k in range(N_TOPICS)}
    perm_ok = True
    for sd in range(5):
        perm = np.random.default_rng(sd).permutation(N_TOPICS)
        m2 = map_topics(H_disk[perm], terms)
        for i in range(N_TOPICS):
            if (m2.loc[m2["topic"] == i, "status"].iloc[0], m2.loc[m2["topic"] == i, "assigned_slug"].iloc[0]) != sig[int(perm[i])]:
                perm_ok = False
    checks["07_토픽 번호 재정렬 불변성(무작위 순열 5회)"] = _chk(perm_ok, "H 행을 무작위로 재정렬해도 각 토픽의 판정이 상위 단어를 따라 이동")

    reg = pd.read_csv(ctx["regime_path"])
    tr = reg["month"] <= TRAIN_END
    zok = True
    for s in DOMAIN_ORDER:
        if reg[f"share_{s}"].notna().all():
            z = (reg[f"share_{s}"] - reg.loc[tr, f"share_{s}"].mean()) / reg.loc[tr, f"share_{s}"].std(ddof=1)
            zok &= bool(np.allclose(z, reg[f"z_{s}"], atol=1e-10)) and int(tr.sum()) == 48
        else:
            zok &= bool(reg[f"z_{s}"].isna().all())
    checks["08_Z-score 모수 학습 48개월 한정"] = _chk(zok, f"저장된 월별 CSV에서 {STUDY_START}~{TRAIN_END} {int(tr.sum())}개월 평균·표준편차(ddof=1)로 z를 재계산해 일치")

    topics = domain_topics(df_map)
    dtp = pd.read_csv(art / "monthly_topic_share.csv")
    link_ok = True
    has_unrep = False
    link_detail: list[str] = []
    for dom, col in ((H1_DOMAIN, f"share_{H1_DOMAIN}"), (H2_DOMAIN, f"share_{H2_DOMAIN}")):
        ks = topics[dom]
        if not ks:
            has_unrep = True
            link_detail.append(f"{dom}: unrepresented (학습 H에서 독립 국면 미형성)")
            continue
        rec = dtp[[f"topic_{k}" for k in ks]].sum(axis=1).to_numpy()
        match = bool(np.allclose(rec, reg[col].to_numpy(), atol=1e-12))
        link_ok &= match
        link_detail.append(f"{dom}→토픽{ks}→{col}(일치={match})")
    fc = pd.read_csv(ctx["forecast_path"])
    mon = reg.set_index("month")
    lag_ok = True
    for _, r in fc.iterrows():
        prev = mon.index[mon.index.get_loc(r["forecast_month"]) - 1]
        lag_ok &= (r["last_available_obs_month"] == prev) and (r["last_available_obs_month"] < r["forecast_month"])
    status_09 = False if not link_ok else (None if has_unrep else True)
    checks["09_H1·H2 특징 연결 재현"] = _chk(status_09, "; ".join(link_detail) + " — 월별 토픽 아티팩트와 매핑으로 특징 열 정합성 확인")
    checks["10_시차 정합(대상월 t는 직전월까지의 정보)"] = _chk(bool(lag_ok), "19개월 전수 last_available_obs_month = 대상월의 직전월")

    df = ctx["df_study"]
    perturb_ok = True
    maxdiff = 0.0
    for m in fc["forecast_month"]:
        t = int(df.index[df["month"] == m][0])
        bad = df.copy()
        bad.loc[bad.index >= t, ["kospi_ret", "base_rate_diff", f"share_{H1_DOMAIN}", f"share_{H2_DOMAIN}"]] = 1.0e6
        row = fc[fc["forecast_month"] == m].iloc[0]
        for tag, y, x, ny, nx, col in (("h1", "kospi_ret", f"share_{H1_DOMAIN}", 2, 2, "h1_ar2_exp_pred"),
                                       ("h1", "kospi_ret", f"share_{H1_DOMAIN}", 2, 2, "h1_news_exp_pred"),
                                       ("h2", "base_rate_diff", f"share_{H2_DOMAIN}", 1, 1, "h2_ar1_exp_pred"),
                                       ("h2", "base_rate_diff", f"share_{H2_DOMAIN}", 1, 1, "h2_news_exp_pred")):
            if is_nan(row[col]):
                continue
            p = _predict_with_future(bad, t, y, x, ny, nx, "news" in col)
            maxdiff = max(maxdiff, abs(p - float(row[col])))
    perturb_ok = maxdiff < 1e-8
    checks["11_확장창 회귀가 대상월 이후 종속변수·특징을 쓰지 않음(교란 시험)"] = _chk(
        perturb_ok, f"대상월 이후 값을 1e6으로 교란해도 19개월×4모형 예측 최대 변화 {maxdiff:.2e}")

    ind_max = 0.0
    for _, row in fc.iterrows():
        t = int(df.index[df["month"] == row["forecast_month"]].tolist()[0])
        for tag, y, x, ny, nx in (("h1", "kospi_ret", f"share_{H1_DOMAIN}", 2, 2), ("h2", "base_rate_diff", f"share_{H2_DOMAIN}", 1, 1)):
            for news in (False, True):
                for win in ("exp", "fix"):
                    col = f"{tag}_{'news' if news else ('ar2' if tag == 'h1' else 'ar1')}_{win}_pred"
                    if is_nan(row[col]):
                        continue
                    end = t if win == "exp" else int(df.index[df["month"] == EVAL_START][0])
                    p = _numpy_predict(df, t, y, x, ny, nx, news, end)
                    ind_max = max(ind_max, abs(p - float(row[col])))
    checks["12_예측 독립 재현(numpy lstsq, 저장 CSV 기준)"] = _chk(ind_max < 1e-8, f"statsmodels 예측과 numpy 최소제곱 재구현의 최대 차 {ind_max:.2e}")

    cls_valid = [r for r in ctx["metrics"]["class"].values() if r is not None]
    m_ids = len(cls_valid) > 0 and all(r["identities_ok"] for r in cls_valid)
    checks["13_혼동행렬 항등식 4종"] = _chk(m_ids, f"TP+FN=하락월, TN+FP=비하락월, TP+TN=적중, 합=N 을 {len(cls_valid)}개 지원 모형에서 확인")

    if ctx["rerun_dir"] is None or not (Path(ctx["rerun_dir"]) / "core_meta.json").exists():
        checks["14_동일 입력·설정 재실행 일치"] = _chk(None, "재실행 아티팩트가 없어 비교하지 못함")
    else:
        rd = Path(ctx["rerun_dir"])
        rm = json.loads((rd / "core_meta.json").read_text(encoding="utf-8"))
        same_hash = {k: rm[k] == meta[k] for k in ("vocab_sha256", "idf_sha256", "sample_ids_sha256", "H_sha256")}
        r_topic = pd.read_csv(rd / "monthly_topic_share.csv")
        f_topic = pd.read_csv(art / "monthly_topic_share.csv")
        cols = [f"topic_{k}" for k in range(N_TOPICS)]
        md = float(np.nanmax(np.abs(r_topic[cols].to_numpy() - f_topic[cols].to_numpy())))
        r_map = map_topics(np.load(rd / "nmf_H.npy"), pd.read_csv(rd / "vocab_idf.csv", encoding="utf-8-sig")["term"].astype(str).tolist())
        same_map = mapping_hash(r_map) == ctx["map_sha"]
        ok = all(same_hash.values()) and md == 0.0 and same_map and r_topic["n_docs"].tolist() == f_topic["n_docs"].tolist()
        checks["14_동일 입력·설정 재실행 일치"] = _chk(
            ok, f"별도 프로세스 재실행({rm['run_id']})과 해시 일치 {same_hash}, 월별 토픽 비중 최대 차 {md:.2e}, 매핑 해시 일치 {same_map}")

    checks["15_평가기간 정보가 특징 선택·적합에 쓰이지 않음"] = _chk(
        meta["fit_sample_month_range"][1] <= TRAIN_END and meta["df_docs_max_month"] <= TRAIN_END
        and params == ["H", "vocab"] and ctx["panel_loaded_after_mapping"],
        f"적합 표본 월 ≤ {meta['fit_sample_month_range'][1]}, DF 기사 월 ≤ {meta['df_docs_max_month']}, "
        f"매핑 함수 입력은 H·vocab 뿐이며 패널(수익률·금리)은 매핑 확정 이후에 읽음")
    return checks


def _predict_with_future(df: pd.DataFrame, t: int, y: str, x: str, ny: int, nx: int, news: bool) -> float:
    return _predict(df, t, y, x, ny, nx, news, t)


def _numpy_predict(df: pd.DataFrame, t: int, y: str, x: str, ny: int, nx: int, news: bool, end: int) -> float:
    start = max(ny, nx)
    yv, xv = df[y].to_numpy(), df[x].to_numpy()
    rows, tgt = [], []
    for i in range(start, end):
        r = [1.0] + [yv[i - L] for L in range(1, ny + 1)]
        if news:
            r += [xv[i - L] for L in range(1, nx + 1)]
        rows.append(r)
        tgt.append(yv[i])
    beta = np.linalg.lstsq(np.array(rows), np.array(tgt), rcond=None)[0]
    q = [1.0] + [yv[t - L] for L in range(1, ny + 1)]
    if news:
        q += [xv[t - L] for L in range(1, nx + 1)]
    return float(np.dot(beta, np.array(q)))


def post_md_checks(ctx: dict[str, Any], md_path: Path, files: dict[str, Path]) -> dict[str, Any]:
    """MD 작성 후: CSV에서 다시 계산한 지표가 MD 표의 모든 셀과 일치하는지, 실행 ID 일치를 확인."""
    checks: dict[str, Any] = {}
    md = md_path.read_text(encoding="utf-8")
    fc = pd.read_csv(files["forecast"])
    mism: list[str] = []
    n_cells = 0

    def cells(tag: str) -> list[str] | None:
        for line in md.splitlines():
            if f"<!--{tag}-->" in line:
                return [c.strip() for c in line.strip().strip("|").split("|")]
        return None

    num = re.compile(r"[+-]?\d+\.\d+")
    ind: dict[str, dict[str, float]] = {}
    for tag in ("h1", "h2"):
        act = fc[ACTUAL_COL[tag]].to_numpy()
        for key, _n in MODEL_SPECS[tag]:
            pr = fc[f"{tag}_{key}_pred"].to_numpy()
            if np.isnan(pr).any():
                ind[f"{tag}_{key}"] = {"rmse": float("nan"), "mae": float("nan"), "bias": float("nan")}
            else:
                e = pr - act
                ind[f"{tag}_{key}"] = {"rmse": float(np.sqrt(np.mean(e ** 2))), "mae": float(np.mean(np.abs(e))), "bias": float(np.mean(e))}
    for tag, base_exp, base_fix in (("h1", "ar2_exp", "ar2_fix"), ("h2", "ar1_exp", "ar1_fix")):
        nd = 4 if tag == "h1" else 5
        for key, _n in MODEL_SPECS[tag]:
            row = cells(f"id:{tag}_{key}")
            if row is None:
                mism.append(f"{tag}_{key}: 행 없음")
                continue
            c = ind[f"{tag}_{key}"]
            if np.isnan(c["rmse"]):
                exp_vals = ["N/A", "N/A", "N/A"]
            else:
                exp_vals = [f"{c['rmse']:.4f}", f"{c['mae']:.4f}", f"{c['bias']:.4f}"]
            for j, ev in enumerate(exp_vals, start=1):
                n_cells += 1
                if row[j] != ev:
                    mism.append(f"{tag}_{key} col{j}: MD {row[j]} vs CSV {ev}")
            z, be = ind[f"{tag}_zero"], ind[f"{tag}_{base_exp}"]
            same = {"news_exp": base_exp, "news_fix": base_fix}
            refs = [(4, z, key == "zero"), (6, be, key == base_exp)]
            if key in same:
                refs.append((8, ind[f"{tag}_{same[key]}"], False))
            for j0, base, selfref in refs:
                if selfref:
                    continue
                for off, met in ((0, "rmse"), (1, "mae")):
                    n_cells += 1
                    if np.isnan(c[met]) or np.isnan(base[met]):
                        if not row[j0 + off].startswith("N/A"):
                            mism.append(f"{tag}_{key} improvement col{j0 + off}: MD {row[j0 + off]} vs CSV N/A")
                    else:
                        val = 100.0 * (base[met] - c[met]) / base[met]
                        got = num.findall(row[j0 + off])
                        if not got or f"{val:+.2f}" != got[0]:
                            mism.append(f"{tag}_{key} improvement col{j0 + off}: MD {row[j0 + off]} vs CSV {val:+.2f}")
    # 분류표
    act1 = fc["actual_kospi_ret"].to_numpy()
    nrow = len(fc)
    cls_pred = {"always_pos": np.ones(nrow), "always_neg": -np.ones(nrow), "exp_base": fc["h1_ar2_exp_pred"].to_numpy(),
                "exp_news": fc["h1_news_exp_pred"].to_numpy(), "fix_base": fc["h1_ar2_fix_pred"].to_numpy(),
                "fix_news": fc["h1_news_fix_pred"].to_numpy()}
    for key, pr in cls_pred.items():
        row = cells(f"cls:{key}")
        if row is None:
            mism.append(f"cls_{key}: 행 없음")
            continue
        if np.isnan(pr).any():
            n_cells += 1
            if row[1] != "N/A":
                mism.append(f"cls_{key} N/A row: MD {row[1]}")
            continue
        pos, neg = act1 < 0, act1 >= 0
        pp = pr < 0
        tp, fp = int((pos & pp).sum()), int((neg & pp).sum())
        fn, tn = int((pos & ~pp).sum()), int((neg & ~pp).sum())
        for j, v in zip((1, 2, 3, 4), (tp, tn, fp, fn)):
            n_cells += 1
            if row[j] != str(v):
                mism.append(f"cls_{key} col{j}: MD {row[j]} vs CSV {v}")
        n_cells += 1
        if not row[5].startswith(f"{100 * (tp + tn) / nrow:.1f}% ({tp + tn}/{nrow})"):
            mism.append(f"cls_{key} hits: MD {row[5]}")
    checks["16_MD의 모든 지표 셀이 CSV 재계산값과 일치"] = _chk(len(mism) == 0, f"비교 셀 {n_cells}개, 불일치 {len(mism)}개" + (f": {mism[:5]}" if mism else ""))

    run_id = ctx["run_id"]
    rid_ok = {}
    for name, p in files.items():
        txt = p.read_text(encoding="utf-8-sig") if p.suffix != ".json" else p.read_text(encoding="utf-8")
        rid_ok[name] = run_id in txt
    rid_ok["artifact_meta"] = json.loads((ctx["art_dir"] / "core_meta.json").read_text(encoding="utf-8"))["run_id"] == run_id
    checks["17_산출물 실행 ID 일치"] = _chk(all(rid_ok.values()), f"실행 ID {run_id} 포함 여부: {rid_ok}")

    reg_cols_ok = all(c in pd.read_csv(files["regime"], nrows=1).columns for c in ("run_id", "month", "n_docs", "residual_share"))
    map_df = pd.read_csv(files["mapping"], encoding="utf-8-sig")
    once = sorted(map_df["topic"].tolist()) == list(range(N_TOPICS)) and map_df["topic"].is_unique
    checks["18_14개 토픽 각 1회 명시·중복 배정 없음"] = _chk(once and reg_cols_ok, f"토픽 {sorted(map_df['topic'].tolist())}, 각 토픽은 한 행(한 판정)")
    return checks


def overall_verdict(checks: dict[str, Any]) -> str:
    st = [c["status"] for c in checks.values()]
    if "FAIL" in st:
        return "REMAINS INCOMPLETE"
    if "INSUFFICIENT EVIDENCE" in st:
        return "PARTIALLY VERIFIED"
    return "TECHNICAL VALIDATION COMPLETE"
