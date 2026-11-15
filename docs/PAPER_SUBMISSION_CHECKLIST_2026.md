> 학회 양식은 [원본 ZIP](../scratch/kiice_template_2026/template_2026.zip)에 보관되어 있습니다. 필요한 파일을 압축 해제해 사용하세요.

# 한국정보통신학회논문지(JKIICE) 2026년 국문지 최종 투고 점검표 (Submission Checklist)

- **문서 작성일**: 2026-11-02
- **기준 학회 공지**: [한국정보통신학회 국문지 논문 투고 안내 (2026년 양식)](https://kiice.org/board/proceedings/article/271327)
- **온라인 논문투고시스템**: [DBpiaONE 한국정보통신학회 투고시스템](https://www.dbpiaone.com/jkiice/index.do)
- **대상 원고**:
  1. 마크다운 정본: [`docs/PAPER_DRAFT_JKIICE.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE.md)
  2. 제출용 원문파일 (저자·소속·약력란 포함): [`docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx)
  3. 심사용 블라인드 파일 (붉은색 상자 ①~⑤ 삭제): [`docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx)
  4. 공식 다운로드 양식 묶음 보존 경로: [`scratch/kiice_template_2026/`](file:///c:/Users/CDW/1_Project/DataMining/scratch/kiice_template_2026/)

---

## 1. 작업 분담 구분 요약 (에이전트 완료 항목 vs 사용자 수행 필요 항목)

| 구분 | 세부 항목 | 상태 | 담당 주체 | 비고 |
| :--- | :--- | :---: | :---: | :--- |
| **원고 내용 동결** | 연구 A(다중 국면), Phase 5.6 Strict OOS, 연구 B(네이버 검색 교차 검증) 통합 및 연구 C(인간 평가) 본문 제외 | **완료** | 에이전트 | 수치 임의 생성·축약 없음 |
| **수치·논리 감사** | 표 1~4, 초록, 본문, 결론 간 상관계수 및 Newey-West HAC Holm 보정 $p$값 전수 대조 | **완료** | 에이전트 | [`PAPER_FINAL_SUBMISSION_AUDIT_2026.md`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_FINAL_SUBMISSION_AUDIT_2026.md) 참조 |
| **2026 학회 양식 반영** | 제1면 레이아웃, 서론 앞 쪽 나눔(Page Break), 장·절 번호(`Ⅰ~Ⅴ`), 영문 표 캡션(`Table 1~4`), 수식 번호 `(1)~(3)` | **완료** | 에이전트 | `.docx` 2종(원문/심사용) 생성 완료 |
| **참고문헌 및 DOI 검증** | `REFERENCES` `[1]~[16]` 영문 서지사항 통일 및 해외 학술지 10편 Crossref DOI 실재성 검증 | **완료** | 에이전트 | 학회 최소 기준(7편 이상) 충족 (총 16편) |
| **저자 실명·약력 기입** | 원문파일 내 ① 국문 저자명, ② 영문 저자명·직위·소속, ③ 교신저자 연락처, ⑤ 저자 사진·학력·약력 기입 | **사용자 입력 필요** | **사용자** | 심사용 블라인드 파일에는 기입하지 않음 |
| **필수 부속 서류 서명** | 저작권이양동의서(`Copyright Transfer Agreement(JKIICE).hwp`) 및 이해관계명시서(`Conflict of Interest Form(JKIICE).hwp`) 작성·자필 서명(또는 날인) 스캔 | **사용자 수행 필요** | **사용자** | [`scratch/kiice_template_2026/`](file:///c:/Users/CDW/1_Project/DataMining/scratch/kiice_template_2026/)에 원본 보관됨 |
| **학회 회원가입 확인** | 투고 논문 모든 저자의 한국정보통신학회 회원가입 및 입회비·연회비 납부 상태 확인 | **사용자 확인 필요** | **사용자** | 학회 규정상 전 저자 회원 자격 필수 |
| **온라인 투고 및 심사료** | DBpiaONE 투고시스템 별도 회원가입, 원문/심사용 파일 업로드, 심사료(일반 4만원/긴급 8만원) 납부 | **사용자 수행 필요** | **사용자** | 에이전트는 외부 시스템 제출·결제 미수행 |

---

## 2. 2026년 한국정보통신학회(JKIICE) 국문지 양식 적용 점검표

공식 배포 파일 `[일반] 한국정보통신학회논문편집양식_2026.hwp`(ZIP 안의 일반 논문편집양식) 및 `★★★심사용 파일 편집양식★★★ 반드시 확인.pdf`(ZIP 안의 심사용 파일 편집양식 PDF)의 편집 규정을 기준으로 점검한 결과입니다.

| 점검 항목 | 학회 공식 양식 기준 (2026년) | 최종 제출본 적용 상태 | 판정 |
| :--- | :--- | :--- | :---: |
| **용지 및 여백** | A4 (210mm × 297mm), 학술지 표준 여백 및 머리말(`JKIICE`) | A4 규격(상하 24mm, 좌우 20mm), 상단 `JKIICE` 배너 및 서지 헤더 적용 | 적합 |
| **국문 제목** | 고딕 Bold 17pt, 자간 -5, 줄간격 130%, 왼쪽정렬 | `맑은 고딕` Bold 17pt, 자간 -0.5pt, 줄간격 130%, 왼쪽정렬 | 적합 |
| **영문 제목** | Arial 12.5pt, 줄간격 120%, 왼쪽정렬, **`A Study on`으로 시작 금지** | Arial Bold 12.5pt, 왼쪽정렬, `"Multi-Regime Detection of Korean Economic Issues..."` (`A Study on` 미사용) | 적합 |
| **영문 소속·직위** | Times New Roman 9pt, **영문 직위(Undergraduate student, Graduate student, Professor 등) 필수 표기** | 원문파일(`SUBMISSION_2026.docx`)에 영문 직위 기입 템플릿 반영 완료 | 적합 |
| **국문 요약 (`요 약`)** | 제목 고딕B 10pt, 본문 명조 9.2pt, 들여쓰기 10pt, 줄간격 130%, 양쪽정렬 | `요  약` 10pt Bold + 본문 `바탕` 9.2pt, 들여쓰기 10pt, 줄간격 130%, 양쪽정렬 | 적합 |
| **영문 초록 (`ABSTRACT`)** | 제목 고딕B 10pt, 본문 Times New Roman 8.5pt, 들여쓰기 10pt, 줄간격 130%, 양쪽정렬 | `ABSTRACT` 10pt Bold + 본문 `Times New Roman` 8.5pt, 들여쓰기 10pt, 줄간격 130% (※ 아래 2.1절 단어 수 안내 참조) | 적합 |
| **국문·영문 키워드** | `키워드 :` (고딕 10pt / 본문 명조 8.5pt), `Keywords :` (Arial 10pt / 본문 TNR 8.5pt, **알파벳순**) | 국문 8개 키워드, 영문 8개 키워드 알파벳순(`Cross-Source Validation` ~ `Topic Modeling`) 정렬 완료 | 적합 |
| **제1면 하단 및 쪽 나눔** | 접수일란, 교신저자 각주, Open Access(`pISSN: 2234-4772`) 후 **`Ⅰ. 서 론`부터 반드시 새 페이지 시작** | 제1면 하단 블록 배치 후 명시적 Page Break(`doc.add_page_break()`) 적용 완료 | 적합 |
| **장·절·소절 제목** | `Ⅰ, Ⅱ, Ⅲ, Ⅳ, Ⅴ` (고딕B 11pt 왼쪽정렬), `1.1 / 2.1` (고딕B 10pt 왼쪽정렬) | `Ⅰ. 서 론` ~ `Ⅴ. 결 론` 11pt Bold, 절 제목 10pt Bold, 소절 9.5pt Bold 적용 | 적합 |
| **본문 문단** | 명조 9.2pt, 들여쓰기 10pt, 줄간격 150%, 양쪽정렬 | `바탕`/`Times New Roman` 9.2pt, 첫 줄 들여쓰기 10pt, 줄간격 150%, 양쪽정렬 | 적합 |
| **표(Table) 양식** | 캡션은 **표 상단 왼쪽정렬 영문 표기(`Table 1. ...`)**, 고딕B 8~8.5pt, 학술지 삼선표 | `Table 1.` ~ `Table 4.` 영문 캡션 상단 왼쪽정렬 및 상·하단 1.0pt 실선 삼선표 적용 | 적합 |
| **수식(Equation) 양식** | 수식 중앙 정렬 + 우측 끝에 `(1)`, `(2)`, `(3)` 일련번호 표기 | 수식 (1) NMF 분해, 수식 (2) Newey-West HAC 공분산, 수식 (3) 학습 고정 표준화 점수 우측 번호 정렬 완료 | 적합 |
| **참고문헌 (`REFERENCES`)** | 제목 `REFERENCES`(고딕 11pt), **모든 참고문헌 영문 작성**, **최소 7편 이상**, TNR 8pt, 줄간격 150% | `[1]`~`[16]` 총 16편 전수 영문 표기 완료 (국내 문헌 `[5], [6], [7], [16]`은 영문 서지 뒤 괄호 안에 국문 원제 병기) | 적합 |

### 2.1 영문초록(ABSTRACT) 단어 수 규정 및 온라인 투고 포털 입력용 축약본 안내

- **점검 내용**: `[일반] 한국정보통신학회논문편집양식_2026.hwp` 내 안내문에는 `"★영문초록 단어 수 140~160개"`라는 권장 문구가 기재되어 있습니다.
- **원고 처리 원칙**: 본 과업의 원칙("원고의 내용을 임의로 축약하지 않는다", "초록과 결론의 핵심 결과 및 HAC·Holm 보정 $p$값 일치")을 엄수하기 위해, 제출용 Word 파일([`PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx))에는 모든 핵심 검증 수치가 빠짐없이 포함된 정본 영문초록(298단어)을 수록하였습니다.
- **대응 방안 (155단어 축약본 준비)**: 만약 DBpiaONE 온라인 투고 시스템의 메타데이터 입력창이나 편집위원회에서 140~160단어 제한을 엄격히 요구할 경우, 핵심 수치($N=931,709$, 67개월, 다중 활성화 $58.21\%$, 미표현 신호 $43.75\%$, OLS $R^2=16.19\%$, 주별 검색 교차 검증 4쌍 및 OOS 2쌍 유의성)를 모두 유지하면서 **정확히 155단어**로 맞춘 아래 영문초록을 즉시 복사하여 사용할 수 있습니다.

> **[선택 사용: JKIICE 140~160단어 규격 맞춤 영문초록 (155 words)]**
> This study constructs a Strict Out-of-Sample (OOS) Non-negative Matrix Factorization (NMF) framework using 931,709 Korean economic news articles from three major business dailies over 67 months (2021.01–2026.07). Vocabulary (22,193 terms), IDF weights, NMF basis vectors (14 topics), and standardization parameters were fixed exclusively on the training period (2021.01–2024.12, 48 months) and projected onto the test period (2025.01–2026.07, 19 months), identifying six valid economic regimes. First, two or more regimes were concurrently active ($z \ge 0.5$) in 58.21% of months (39/67), and single-dominant regime selection left 43.75% (49/112) of active regime signals unrepresented. Second, Newey-West HAC OLS regression on volatility-standardized KOSPI returns ($N=67$) yielded $R^2 = 16.19\%$ ($F = 4.6833, p = 0.000573$), with negative contemporaneous associations for Interest Rate & Inflation ($\beta = -0.7418, p_{\text{holm}} = 0.0024$) and Capital Transactions ($\beta = -0.5299, p_{\text{holm}} = 0.0129$). Third, weekly first-differenced cross-validation against Naver Datalab search indices ($N=291$, 24-test HAC Holm adjustment) confirmed significant contemporaneous co-movement across four pairs overall and two pairs—Stock Market ($r = +0.4984, p_{\text{holm}} = 0.0432$) and Corporate Earnings ($r = +0.4718, p_{\text{holm}} = 0.0011$)—in OOS testing.

---

## 3. 제출 파일 구성 및 블라인드(심사용) 파일 점검표

학회 공지 문서 `★★★심사용 파일 편집양식★★★ 반드시 확인.pdf`(ZIP 안의 심사용 파일 편집양식 PDF)에 따르면 온라인 투고 시 **원문파일**과 **심사용 파일** 2종을 각각 업로드해야 하며, 심사용 파일에서는 붉은색 네모 박스로 표시된 **① ~ ⑤ 항목을 반드시 삭제**해야 합니다.

| 번호 | 삭제 대상 항목 (심사용 파일 편집양식 PDF 기준) | 원문파일 (`PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`) | 심사용 파일 (`PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx`) | 점검 결과 |
| :---: | :--- | :--- | :--- | :---: |
| **①** | **국문 저자명** (제1면 국문 제목 아래) | 포함 (`홍길동¹ · 홍동순²*` 입력란) | **완전 삭제** | 완료 |
| **②** | **영문 저자명 및 소속·직위** (제1면 영문 제목 아래) | 포함 (`Kil-Dong Hong¹...` 및 소속·직위 입력란) | **완전 삭제** | 완료 |
| **③** | **교신저자 각주** (제1면 하단 `* Corresponding Author...`) | 포함 (성명·이메일·전화번호·소속 입력란) | **완전 삭제** | 완료 |
| **④** | **사사 / 연구과제 표기** (`ACKNOWLEDGEMENTS`, 참고문헌 직전) | 해당 없음 (연구과제 문구 미포함; 필요 시 영문 추가 가능) | **완전 삭제** (미포함) | 완료 |
| **⑤** | **저자 약력 및 사진** (참고문헌 뒤 증명사진·성명·학력·관심분야 표) | 포함 (제1저자·교신저자 2인 기준 표준 약력 표 수록) | **완전 삭제** | 완료 |

> **참고 (HWP 파일 변환이 필요한 경우)**:
> DBpiaONE 투고 시스템에서 아래아한글(`.hwp` 또는 `.hwpx`) 포맷 업로드를 선호할 경우, 한글(Hancom Office HWP) 프로그램에서 [`PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx) 및 [`PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026.docx)를 열어 `[다른 이름으로 저장] -> 한글 문서 (*.hwp)`로 즉시 저장하거나, [학회 양식 ZIP](../scratch/kiice_template_2026/template_2026.zip) 원본에 텍스트와 표를 붙여넣어 사용할 수 있습니다.

---

## 4. 표·수식·참고문헌 최종 점검 결과

### 4.1 표(Table 1 ~ Table 4) 가독성 및 정합성
- **Table 1**: 6대 유효 국면(`realestate`, `capital`, `macro`, `market`, `aichip`, `earnings`), 미형성 국면(`hhdebt`, `trade`), 비할당 잔차(`residual`)의 학습 기간(48개월) 평균($\mu_{\text{train}}$), 표준편차($\sigma_{\text{train}}$), 임계 비중($z \ge 0.5$) 및 구간별 활성 월수(전체 112건 = 학습 89건 + 테스트 23건)가 본문 4.1절과 100% 일치합니다.
- **Table 2**: 단일 대표 국면(Argmax / Hurdle Argmax) 대비 다중 국면 활성화($z \ge 0.5$) 비교표에서 전체 다중 활성 비율 $58.21\%(39/67)$, 단일 방식 제한 시 미표현 신호 비율 $43.75\%(49/112)$이 본문 4.2절·초록·결론과 일치합니다.
- **Table 3**: 과거 변동성 정규화 코스피 수익률(`kospi_ret_std`, $N=67$)에 대한 Newey-West HAC($\text{maxlags}=3$) OLS 추정표에서 $R^2=0.161879(16.19\%)$, $\text{Adj-}R^2=0.078067(7.81\%)$, $\text{HAC } F=4.683257(p=0.000573)$ 및 6개 변수 회귀계수·표준오차·원시 $p$값·Holm 보정 $p$값·VIF가 본문 4.3.1절과 일치합니다.
- **Table 4**: 주별 1차 차분 뉴스 점유율과 네이버 상대 검색 지수 간 교차 검증($N=208/82/291$, Newey-West HAC $\text{maxlags}=4$, 24개 검정 Holm 보정) 결과가 본문 4.4절·초록·결론과 일치합니다.

### 4.2 수식(Equation 1 ~ Equation 3) 점검
- **수식 (1)**: $V \approx W \times H \quad (\text{단, } W \ge 0, H \ge 0)$ — 2.2절 NMF 행렬 분해 정의
- **수식 (2)**: $\hat{V}_{\text{HAC}} = (X'X)^{-1} \left[ \hat{\Gamma}_0 + \sum_{l=1}^{q} \left(1 - \frac{l}{q+1}\right) (\hat{\Gamma}_l + \hat{\Gamma}_l') \right] (X'X)^{-1}$ — 2.3절 Newey-West HAC 공분산 추정량
- **수식 (3)**: $z_{d,t} = (s_{d,t} - \mu_{d,\text{train}}) / \sigma_{d,\text{train}}$ — 3.4절 학습 기간 모수 고정 표준화 점수

### 4.3 참고문헌 (`REFERENCES` `[1] ~ [16]`) 및 Crossref DOI 실재성 검증
- 학회 규정("모든 참고문헌은 영문으로 작성, 최소 7편 이상 인용")에 따라 총 16편의 참고문헌을 모두 영문 서지 형식으로 작성하였으며, 해외 학술지 논문 10편은 Crossref API(`https://api.crossref.org/works/...`)를 통해 권(vol)·호(no)·페이지(pp)·연도 및 DOI 유효성을 전수 확인하였습니다:
  - `[1]` Baker et al. (2016), *QJE*, vol. 131, no. 4, pp. 1593-1636 — `DOI: 10.1093/qje/qjw024` (검증 완료)
  - `[2]` Bybee et al. (2024), *J. Finance*, vol. 79, no. 5, pp. 2947-2993 — `DOI: 10.1111/jofi.13377` (검증 완료)
  - `[3]` Thorsrud (2020), *JBES*, vol. 38, no. 2, pp. 393-409 — `DOI: 10.1080/07350015.2018.1506344` (검증 완료)
  - `[4]` Tetlock (2007), *J. Finance*, vol. 62, no. 3, pp. 1139-1168 — `DOI: 10.1111/j.1540-6261.2007.01232.x` (검증 완료)
  - `[8]` Lee and Seung (1999), *Nature*, vol. 401, no. 6755, pp. 788-791 — `DOI: 10.1038/44565` (검증 완료)
  - `[10]` Truong et al. (2020), *Signal Processing*, vol. 167, art. no. 107299 — `DOI: 10.1016/j.sigpro.2019.107299` (검증 완료)
  - `[12]` Newey and West (1987), *Econometrica*, vol. 55, no. 3, pp. 703-708 — `DOI: 10.2307/1913610` (검증 완료)
  - `[13]` White (1980), *Econometrica*, vol. 48, no. 4, pp. 817-838 — `DOI: 10.2307/1912559` (검증 완료)
  - `[14]` Da et al. (2015), *Rev. Financial Studies*, vol. 28, no. 1, pp. 1-32 — `DOI: 10.1093/rfs/hhu072` (검증 완료)
  - `[15]` Granger and Newbold (1974), *J. Econometrics*, vol. 2, no. 2, pp. 111-120 — `DOI: 10.1016/0304-4076(74)90034-7` (검증 완료)

---

## 5. 사용자 직접 수행 필요 사항 및 온라인 투고 절차 안내

### 단계 1. 원문파일(`PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`) 내 저자 정보 기입
[`docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx`](file:///c:/Users/CDW/1_Project/DataMining/docs/PAPER_DRAFT_JKIICE_SUBMISSION_2026.docx) 파일을 열어 다음 4곳의 플레이스홀더(`※ ... 기입`)를 실제 저자 정보로 수정합니다(심사용 블라인드 파일은 수정할 필요 없음):
1. **제1면 국문 저자명(①)**: 예) `홍길동¹ · 홍동순²*`
2. **제1면 영문 저자명 및 소속·직위(②)**:
   - 학회 규정상 영문 소속 앞에 **반드시 영문 직위(`Undergraduate student`, `Graduate student`, `Researcher`, `Assistant professor`, `Associate professor`, `Professor` 등)를 표기**해야 합니다.
3. **제1면 하단 교신저자 각주(③)**: 교신저자 영문 성명, 이메일 주소, 전화번호, 소속 및 우편번호 기입
4. **마지막 페이지 저자 약력란(⑤)**:
   - 증명사진 삽입, 국·영문 성명, 학사·석사·박사 졸업연도(월 제외, 연도만 기입), 현재 소속 및 직위, 관심분야(3개 내외) 기입
5. **(선택) 연구수행과제 사사 문구(④)**: 연구비 지원 과제가 있는 경우에만 `REFERENCES` 바로 위에 `ACKNOWLEDGEMENTS` 제목(고딕 11pt)과 함께 **영문으로** 작성합니다(사사 문구 삽입 시 채택 후 게재료에 100,000원이 가산됨).

### 단계 2. 부속 제출 서류 2종 작성 및 서명
[`scratch/kiice_template_2026/`](file:///c:/Users/CDW/1_Project/DataMining/scratch/kiice_template_2026/) 폴더에 다운로드된 학회 공식 양식 2종을 작성하여 서명 후 스캔(PDF/이미지)합니다:
1. **저작권이양동의서**: [학회 양식 ZIP](../scratch/kiice_template_2026/template_2026.zip) (`Copyright Transfer Agreement(JKIICE).hwp`) — 논문 제목 기입 및 저자 서명
2. **이해관계명시서**: [학회 양식 ZIP](../scratch/kiice_template_2026/template_2026.zip) (`Conflict of Interest Form(JKIICE).hwp`) — 이해상충 여부 체크 및 교신저자 서명

### 단계 3. 학회 회원가입 및 DBpiaONE 투고시스템 등록
1. **한국정보통신학회 회원 자격 확인**: 게재 논문의 **모든 저자**는 한국정보통신학회(`https://kiice.org`) 회원이어야 하며, 입회비 및 연회비가 납부되어 있어야 합니다.
2. **DBpiaONE 투고시스템 별도 회원가입**: 학회 홈페이지 계정과 논문투고시스템([`https://www.dbpiaone.com/jkiice/index.do`](https://www.dbpiaone.com/jkiice/index.do)) 계정은 연동되지 않으므로, 최초 투고 시 투고시스템에서 별도 회원가입을 진행합니다.
3. **파일 업로드**:
   - **원문파일**: 저자 정보를 기입한 `PAPER_DRAFT_JKIICE_SUBMISSION_2026` 업로드
   - **심사용 파일**: 저자 정보가 모두 제거된 `PAPER_DRAFT_JKIICE_BLIND_REVIEW_2026` 업로드
   - **부속 서류**: 서명된 저작권이양동의서 및 이해관계명시서 업로드

### 단계 4. 심사료 및 게재료 납부 안내 (2026년 기준, `scratch/kiice_template_2026/page_charges_2026.png`)
1. **논문 심사료 (투고 완료 후 납부)**:
   - **일반 심사**: **40,000원**
   - **긴급 심사**: **80,000원**
   - **납부 방법**: 온라인 투고 시스템 내 카드결제 또는 우체국 계좌이체 (`600668-01-003365`, 예금주: `한국정보통신학회`). 계좌이체 시 입금자명을 `OOO심사비`(제1저자 또는 교신저자 성명)로 기재하고 학회 사무국 이메일(`journal@kiice.org`)로 입금 확인 메일을 발송해야 심사가 진행됩니다.
2. **논문 게재료 (최종 채택 후 청구, 선납 불가)**:
   - **일반 심사 기준**: 기본 6쪽까지 **200,000원** / 7~8쪽 페이지당 **+30,000원** / 9쪽 이상 페이지당 **+40,000원**
   - **긴급 심사 기준**: `(일반 게재료 × 2)`
   - **연구수행과제(사사) 문구 삽입 시**: **+100,000원** 추가

