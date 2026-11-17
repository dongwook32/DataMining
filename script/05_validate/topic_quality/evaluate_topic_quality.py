"""연구 A·B 공통 모듈: 토픽 품질(Coherence C_v, NPMI, U_mass, Diversity, Redundancy, Coverage) 및
토픽 정렬(Hungarian Matching, Cosine, Jaccard, Weighted Jaccard) 평가 유틸리티.

모든 Coherence 계산은 학습 기간(2021-01~2024-12, N=643,095) 코퍼스의 문서-어휘 이진 동시출현 행렬을
기준 코퍼스(Reference Corpus)로 사용하여 미래 정보 누수 없이 정확하고 일관되게 산출한다.
"""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from scipy import sparse
from scipy.optimize import linear_sum_assignment


def get_top_term_indices(H: np.ndarray, top_n: int = 20) -> np.ndarray:
    """각 토픽(행)에서 가중치 내림차순(동률 시 인덱스 오름차순) 상위 top_n개 어휘 인덱스를 반환한다."""
    K, V = H.shape
    out = np.empty((K, top_n), dtype=np.int32)
    idx_range = np.arange(V)
    for k in range(K):
        out[k] = np.lexsort((idx_range, -H[k]))[:top_n]
    return out


def compute_topic_coherence_and_diversity(
    H: np.ndarray,
    X_ref_bin: sparse.csr_matrix,
    vocab: list[str],
    top_m_coherence: int = 10,
) -> dict[str, Any]:
    """토픽 행렬 H (K x V)와 학습 기준 이진 문서-단어 행렬 X_ref_bin (N_docs x V)으로부터
    토픽별 및 전체 C_v, NPMI, U_mass, Topic Diversity@10, @20, Redundancy, Coverage를 계산한다.
    """
    K, V = H.shape
    N_docs = float(X_ref_bin.shape[0])
    eps = 1e-12

    top10_idx = get_top_term_indices(H, 10)
    top20_idx = get_top_term_indices(H, 20)
    topm_idx = top10_idx if top_m_coherence == 10 else get_top_term_indices(H, top_m_coherence)

    # 필요한 상위 단어들의 합집합에 대해서만 희소 부분행렬 동시출현을 한 번에 계산
    uniq_terms = np.unique(np.concatenate([top10_idx.ravel(), top20_idx.ravel(), topm_idx.ravel()]))
    term_to_local = {int(t): i for i, t in enumerate(uniq_terms)}
    X_sub = X_ref_bin[:, uniq_terms].astype(np.float64)
    cooc_mat = (X_sub.T @ X_sub).toarray()  # (U, U)
    doc_freq = np.diag(cooc_mat).copy()  # N(w_i)

    # Diversity & Redundancy
    unique_10 = len(np.unique(top10_idx.ravel()))
    unique_20 = len(np.unique(top20_idx.ravel()))
    td_10 = unique_10 / float(K * 10)
    td_20 = unique_20 / float(K * 20)
    redundancy_10 = 1.0 - td_10
    redundancy_20 = 1.0 - td_20

    # 각 토픽의 상위 10/20개 단어 중 다른 토픽 상위 단어와 겹치는 비율
    from collections import Counter
    counts_10 = Counter(top10_idx.ravel().tolist())
    counts_20 = Counter(top20_idx.ravel().tolist())

    topic_cv = np.zeros(K, dtype=np.float64)
    topic_npmi = np.zeros(K, dtype=np.float64)
    topic_umass = np.zeros(K, dtype=np.float64)
    topic_red10 = np.zeros(K, dtype=np.float64)
    topic_red20 = np.zeros(K, dtype=np.float64)
    topic_eff_vocab = np.zeros(K, dtype=np.float64)

    for k in range(K):
        t_m = [term_to_local[int(w)] for w in topm_idx[k]]
        M = len(t_m)
        npmi_sub = np.zeros((M, M), dtype=np.float64)
        npmi_pairs = []
        umass_pairs = []

        for i in range(M):
            wi = t_m[i]
            pi = max(doc_freq[wi] / N_docs, eps)
            for j in range(M):
                wj = t_m[j]
                pj = max(doc_freq[wj] / N_docs, eps)
                pij = cooc_mat[wi, wj] / N_docs
                if i == j:
                    npmi_val = 1.0
                elif pij <= 0.0:
                    npmi_val = -1.0
                else:
                    pmi = np.log((pij + eps) / (pi * pj))
                    npmi_val = float(pmi / (-np.log(pij + eps)))
                npmi_sub[i, j] = npmi_val
                if j < i:
                    npmi_pairs.append(npmi_val)
                    # U_mass (Mimno et al. 2011): log((N(w_i, w_j) + 1) / N(w_j)) where w_j is higher-ranked
                    umass_pairs.append(float(np.log((cooc_mat[wi, wj] + 1.0) / max(doc_freq[wj], 1.0))))

        topic_npmi[k] = float(np.mean(npmi_pairs))
        topic_umass[k] = float(np.mean(umass_pairs))

        # C_v (Röder et al. 2015): word NPMI context vector vs summed topic context vector cosine similarity
        # Shift NPMI from [-1, 1] to non-negative context weight max(npmi, 0) or standard signed NPMI vector
        # Standard Röder et al. C_v uses direct NPMI vector (gamma=1) cosine similarity against topic sum vector
        vec_sum = npmi_sub.sum(axis=0)
        norm_sum = float(np.linalg.norm(vec_sum))
        cos_list = []
        for i in range(M):
            vi = npmi_sub[i]
            ni = float(np.linalg.norm(vi))
            if ni > 0 and norm_sum > 0:
                cos_list.append(float(np.dot(vi, vec_sum) / (ni * norm_sum)))
            else:
                cos_list.append(0.0)
        topic_cv[k] = float(np.mean(cos_list))

        topic_red10[k] = float(np.mean([1.0 if counts_10[int(w)] > 1 else 0.0 for w in top10_idx[k]]))
        topic_red20[k] = float(np.mean([1.0 if counts_20[int(w)] > 1 else 0.0 for w in top20_idx[k]]))

        # Effective vocabulary size via Shannon entropy
        row_h = np.maximum(H[k].astype(np.float64), 0.0)
        s_h = row_h.sum()
        if s_h > 0:
            p_h = row_h / s_h
            pos = p_h > 1e-15
            ent = -float(np.sum(p_h[pos] * np.log(p_h[pos])))
            topic_eff_vocab[k] = float(np.exp(ent))

    # Vocabulary coverage (terms with normalized weight > 1/V in at least one topic)
    H_norm = H / np.maximum(H.sum(axis=1, keepdims=True), 1e-15)
    active_vocab_mask = (H_norm > (1.0 / float(V))).any(axis=0)
    vocab_coverage = float(np.mean(active_vocab_mask))

    return {
        "cv_mean": float(np.mean(topic_cv)),
        "cv_std": float(np.std(topic_cv, ddof=1)),
        "cv_median": float(np.median(topic_cv)),
        "npmi_mean": float(np.mean(topic_npmi)),
        "npmi_std": float(np.std(topic_npmi, ddof=1)),
        "umass_mean": float(np.mean(topic_umass)),
        "umass_std": float(np.std(topic_umass, ddof=1)),
        "topic_diversity_10": float(td_10),
        "topic_diversity_20": float(td_20),
        "topic_redundancy_10": float(redundancy_10),
        "topic_redundancy_20": float(redundancy_20),
        "vocab_coverage_above_uniform": vocab_coverage,
        "mean_effective_vocab_size": float(np.mean(topic_eff_vocab)),
        "per_topic": {
            "cv": topic_cv,
            "npmi": topic_npmi,
            "umass": topic_umass,
            "red10": topic_red10,
            "red20": topic_red20,
            "eff_vocab": topic_eff_vocab,
            "top10_idx": top10_idx,
            "top20_idx": top20_idx,
        },
    }


def jaccard_top_k(idx_a: np.ndarray, idx_b: np.ndarray) -> float:
    set_a = set(int(x) for x in idx_a)
    set_b = set(int(x) for x in idx_b)
    union = len(set_a | set_b)
    return float(len(set_a & set_b) / union) if union > 0 else 0.0


def weighted_jaccard_top_k(vec_a: np.ndarray, vec_b: np.ndarray, idx_a: np.ndarray, idx_b: np.ndarray) -> float:
    """두 토픽의 상위 키워드 합집합 상에서 정규화된 가중치의 Weighted Jaccard (Ruzicka) 유사도를 계산한다."""
    union_idx = np.unique(np.concatenate([idx_a, idx_b]))
    wa = vec_a[union_idx].astype(np.float64)
    wb = vec_b[union_idx].astype(np.float64)
    sa = wa.sum()
    sb = wb.sum()
    if sa > 0:
        wa = wa / sa
    if sb > 0:
        wb = wb / sb
    denom = float(np.sum(np.maximum(wa, wb)))
    return float(np.sum(np.minimum(wa, wb)) / denom) if denom > 0 else 0.0


def align_topics_hungarian(H_ref: np.ndarray, H_cand: np.ndarray) -> list[dict[str, Any]]:
    """기준 모델 H_ref (K x V)와 비교 모델 H_cand (K x V) 간의 코사인 유사도 행렬을 계산하고,
    Hungarian Algorithm (linear_sum_assignment)으로 1:1 최적 매칭 및 Jaccard@10/@20, Weighted Jaccard@20을 반환한다.
    """
    K = H_ref.shape[0]
    norm_ref = H_ref / np.maximum(np.linalg.norm(H_ref, axis=1, keepdims=True), 1e-15)
    norm_cand = H_cand / np.maximum(np.linalg.norm(H_cand, axis=1, keepdims=True), 1e-15)
    cos_mat = np.clip(norm_ref @ norm_cand.T, 0.0, 1.0)

    row_ind, col_ind = linear_sum_assignment(-cos_mat)

    top10_ref = get_top_term_indices(H_ref, 10)
    top20_ref = get_top_term_indices(H_ref, 20)
    top10_cand = get_top_term_indices(H_cand, 10)
    top20_cand = get_top_term_indices(H_cand, 20)

    matches = []
    for r_i, c_i in zip(row_ind, col_ind):
        cos_sim = float(cos_mat[r_i, c_i])
        j10 = jaccard_top_k(top10_ref[r_i], top10_cand[c_i])
        j20 = jaccard_top_k(top20_ref[r_i], top20_cand[c_i])
        wj20 = weighted_jaccard_top_k(H_ref[r_i], H_cand[c_i], top20_ref[r_i], top20_cand[c_i])
        # 2순위 후보와의 마진 확인 (분할/병합 여부 진단용)
        sorted_c = np.argsort(-cos_mat[r_i])
        second_c = int(sorted_c[1]) if sorted_c[0] == c_i else int(sorted_c[0])
        second_cos = float(cos_mat[r_i, second_c])
        matches.append({
            "ref_topic": int(r_i),
            "cand_topic": int(c_i),
            "cosine_sim": cos_sim,
            "jaccard_top10": j10,
            "jaccard_top20": j20,
            "weighted_jaccard_top20": wj20,
            "second_best_cand_topic": second_c,
            "second_best_cosine": second_cos,
            "cosine_margin": cos_sim - second_cos,
        })
    return matches

