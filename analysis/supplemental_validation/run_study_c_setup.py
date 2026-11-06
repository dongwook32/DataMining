"""연구 C: 사람의 직접 라벨링을 위한 블라인드 표본 추출 및 평가 파일 생성 스크립트.

원칙:
1. Strict OOS 테스트 기간(2025-01 ~ 2026-07, 19개월, 288,614건)에서 19개월 균등 층화 무작위 추출 (월별 20건 = 총 380건).
2. 언론사별(한국경제, 매일경제, 서울경제) 고른 분포 보장.
3. 평가자용 CSV(Batch A, Batch B)에는 모델 예측값, NMF 점수, 클러스터 라벨을 일절 포함하지 않음 (완전 블라인드).
4. 실제 article_id와 익명 ann_id의 매핑은 join_key 파일로 격리 보관.
"""

from __future__ import annotations
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent.parent
CORPUS_PATH = ROOT / "data" / "processed" / "corpus" / "news_corpus.parquet"
OUT_DIR = ROOT / "data" / "processed" / "supplemental_validation"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 20261101
N_PER_MONTH = 20

def generate_annotation_batches():
    np.random.seed(SEED)
    print("1. 테스트 기간 기사 로드...")
    tab = pq.read_table(CORPUS_PATH, columns=["article_id", "date", "month", "source", "title", "keywords"])
    df_all = tab.to_pandas()
    df_eval = df_all[df_all["month"] >= "2025-01"].reset_index(drop=True)
    print(f"  테스트 기간(2025-01~2026-07) 기사 수: {len(df_eval):,}")
    
    # 2. 19개월 균등 층화 무작위 추출 (월별 20건, 언론사 고른 표집)
    sampled_list = []
    months = sorted(df_eval["month"].unique())
    print(f"  추출 대상 개월 수: {len(months)}개월")
    
    for m in months:
        m_df = df_eval[df_eval["month"] == m].copy()
        # 언론사별 균등 시도 (한국경제, 매일경제, 서울경제)
        sources = m_df["source"].unique()
        per_source = N_PER_MONTH // len(sources)
        remainder = N_PER_MONTH % len(sources)
        
        m_samples = []
        for i, s in enumerate(sources):
            s_df = m_df[m_df["source"] == s]
            k = per_source + (1 if i < remainder else 0)
            if len(s_df) >= k:
                m_samples.append(s_df.sample(n=k, random_state=SEED))
            else:
                m_samples.append(s_df)
                
        m_sampled = pd.concat(m_samples)
        if len(m_sampled) < N_PER_MONTH:
            # 부족분 보충
            extra = m_df.loc[~m_df.index.isin(m_sampled.index)].sample(n=N_PER_MONTH - len(m_sampled), random_state=SEED)
            m_sampled = pd.concat([m_sampled, extra])
        sampled_list.append(m_sampled)
        
    sample_df = pd.concat(sampled_list).sample(frac=1.0, random_state=SEED).reset_index(drop=True)
    print(f"  최종 추출 표본 수: {len(sample_df)}건 (월별 20건 x 19개월)")
    
    # 익명 식별자 ann_id 부여
    sample_df["ann_id"] = [f"ANN_{i+1:04d}" for i in range(len(sample_df))]
    
    # 3. 조인 키 및 매니페스트 생성
    join_key = sample_df[["ann_id", "article_id", "date", "month", "source"]].copy()
    join_key.to_csv(OUT_DIR / "human_annotation_join_key.csv", index=False, encoding="utf-8-sig")
    
    manifest = sample_df.groupby(["month", "source"]).size().reset_index(name="sample_count")
    manifest.to_csv(OUT_DIR / "human_annotation_sample_manifest.csv", index=False, encoding="utf-8-sig")
    
    # 4. 블라인드 평가자용 CSV 생성 (Batch A, Batch B)
    # 제목과 키워드만 노출, 모델 점수/국면 비공개
    eval_cols = [
        "ann_id", "date", "source", "title", "keywords",
        "macro", "realestate", "aichip", "market", "earnings", "capital", "other", "unclear", "notes"
    ]
    batch_df = sample_df[["ann_id", "date", "source", "title", "keywords"]].copy()
    for c in ["macro", "realestate", "aichip", "market", "earnings", "capital", "other", "unclear", "notes"]:
        batch_df[c] = ""
        
    batch_a_path = OUT_DIR / "human_annotation_batch_A.csv"
    batch_b_path = OUT_DIR / "human_annotation_batch_B.csv"
    batch_df.to_csv(batch_a_path, index=False, encoding="utf-8-sig")
    batch_df.to_csv(batch_b_path, index=False, encoding="utf-8-sig")
    
    # 5. 연구 C 현황 및 QC 보고서 생성
    qc_lines = [
        "# 연구 C: 경제 국면 의미 타당성 검증 QC 보고서 (`human_validation_qc.md`)",
        "",
        "- **작성 일시:** 2026-11-01",
        "- **평가 대상 표본:** Strict OOS 테스트 기간(2025-01~2026-07, 19개월) 380건 무작위 층화 표본",
        "- **평가 방식:** 완전 블라인드 평가자 2인(평가자 A, B) 독립 라벨링",
        "",
        "## 1. 표본 추출 및 블라인드 파일 준비 상태",
        "",
        f"- **총 표본 수:** {len(sample_df)}건 (19개월 x 월별 20건 균등)",
        f"- **언론사 분포:** {sample_df['source'].value_counts().to_dict()}",
        "- **블라인드 평가 파일:**",
        f"  - `human_annotation_batch_A.csv`: 생성 완료 (빈 라벨 템플릿)",
        f"  - `human_annotation_batch_B.csv`: 생성 완료 (빈 라벨 템플릿)",
        f"  - `human_annotation_codebook.md`: 6대 국면 정의 및 다중 라벨/미형성 국면 지침 작성 완료",
        f"  - `human_annotation_join_key.csv`: 원본 기사 매핑키 분리 격리 완료",
        f"  - `human_annotation_sample_manifest.csv`: 월별/언론사별 분포 매니페스트 저장 완료",
        "",
        "## 2. 평가 현황 및 다음 단계",
        "",
        "> [!IMPORTANT]",
        "> **자동화 모델의 사람 라벨 대체 금지 원칙 준수**",
        "> - 본 연구는 LLM이나 휴리스틱 모델이 사람의 판정을 대신하는 것을 엄격히 금지함.",
        "> - 현재 단계는 **실제 인간 평가자 2인의 독립 라벨링 입력 대기 상태(WAITING FOR HUMAN LABELS)**임.",
        "> - 실제 사람이 기사를 직접 읽고 `batch_A.csv`와 `batch_B.csv`를 작성하여 반환한 이후에만 평가자 간 일치도(Cohen's kappa)와 모델의 분류 성능(Precision, Recall, F1)을 공식 계산함.",
        ""
    ]
    (OUT_DIR / "human_validation_qc.md").write_text("\n".join(qc_lines), encoding="utf-8")
    print("연구 C 표본 추출 및 블라인드 평가 파일 생성 완료.")

if __name__ == "__main__":
    generate_annotation_batches()

