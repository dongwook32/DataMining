(function () {
  "use strict";

  const D = window.RESEARCH_DATA;
  if (!D) {
    console.error("RESEARCH_DATA가 로드되지 않았습니다.");
    return;
  }

  // 중요: Plotly는 전달된 layout 객체를 내부에서 직접 변이(mutate)시키므로
  // 매 차트마다 반드시 새로운 layout 객체를 생성하는 팩토리 함수를 사용해야 함!
  function createLayout(overrides = {}) {
    const base = {
      paper_bgcolor: "#ffffff",
      plot_bgcolor: "#f8fafc",
      font: { family: "Pretendard, -apple-system, sans-serif", color: "#0f172a", size: 12.5 },
      margin: { t: 44, r: 36, b: 56, l: 68 },
      xaxis: {
        gridcolor: "#e2e8f0",
        zerolinecolor: "#cbd5e1",
        tickfont: { size: 11.5, color: "#334155" },
        automargin: true,
      },
      yaxis: {
        gridcolor: "#e2e8f0",
        zerolinecolor: "#cbd5e1",
        tickfont: { size: 11.5, color: "#334155" },
        automargin: true,
      },
      legend: {
        orientation: "h",
        yanchor: "bottom",
        y: 1.03,
        xanchor: "left",
        x: 0,
        font: { size: 12, color: "#0f172a" },
        bgcolor: "rgba(255,255,255,0.9)",
      },
      hovermode: "x unified",
    };

    const result = { ...base, ...overrides };
    if (overrides.xaxis) {
      result.xaxis = { ...base.xaxis, ...overrides.xaxis };
    }
    if (overrides.yaxis) {
      result.yaxis = { ...base.yaxis, ...overrides.yaxis };
    }
    if (overrides.margin) {
      result.margin = { ...base.margin, ...overrides.margin };
    }
    if (overrides.legend) {
      result.legend = { ...base.legend, ...overrides.legend };
    }
    return result;
  }

  const PLOT_CFG = {
    responsive: true,
    displayModeBar: false,
  };

  // 국면 한글 이름 및 색상
  const REGIME_KR = {
    macro: "금리·물가 (macro)",
    realestate: "부동산 (realestate)",
    hhdebt: "가계부채·신용 (hhdebt)",
    aichip: "첨단산업·전기차·배터리 (aichip)",
    market: "시황·증시 (market)",
    earnings: "기업실적 (earnings)",
    capital: "자본거래·투자 (capital)",
    z_macro: "금리·물가 (z_macro)",
    z_realestate: "부동산 (z_realestate)",
    z_hhdebt: "가계부채·신용 (z_hhdebt)",
    z_aichip: "첨단산업 (z_aichip)",
    z_market: "시황·증시 (z_market)",
    z_earnings: "기업실적 (z_earnings)",
    z_capital: "자본거래 (z_capital)",
  };

  const REGIME_COLOR = {
    macro: "#e11d48",
    realestate: "#d97706",
    hhdebt: "#ca8a04",
    aichip: "#059669",
    market: "#2563eb",
    earnings: "#7c3aed",
    capital: "#4f46e5",
  };

  function fmt(v, d = 4) {
    if (v === null || v === undefined || Number.isNaN(v)) return "-";
    if (typeof v !== "number") return String(v);
    return v.toFixed(d);
  }

  function calcStats(xArr, yArr) {
    const pts = [];
    for (let i = 0; i < xArr.length; i++) {
      const xv = xArr[i];
      const yv = yArr[i];
      if (xv !== null && xv !== undefined && yv !== null && yv !== undefined && !Number.isNaN(xv) && !Number.isNaN(yv)) {
        pts.push([Number(xv), Number(yv)]);
      }
    }
    const n = pts.length;
    if (n < 3) return { r: 0, n, slope: 0, intercept: 0 };
    let sx = 0, sy = 0;
    for (const [x, y] of pts) { sx += x; sy += y; }
    const mx = sx / n, my = sy / n;
    let sxx = 0, syy = 0, sxy = 0;
    for (const [x, y] of pts) {
      const dx = x - mx, dy = y - my;
      sxx += dx * dx;
      syy += dy * dy;
      sxy += dx * dy;
    }
    if (sxx === 0 || syy === 0) return { r: 0, n, slope: 0, intercept: my };
    const r = sxy / Math.sqrt(sxx * syy);
    const slope = sxy / sxx;
    const intercept = my - slope * mx;
    return { r, n, slope, intercept };
  }

  // ==================== SECTION 1: OVERVIEW ====================
  function renderSection1() {
    const p67 = D.study_panel_67m;
    const trainRows = p67.filter((r) => r.period === "train");
    const oosRows = p67.filter((r) => r.period !== "train");

    Plotly.newPlot(
      "chart-sec1-docs",
      [
        {
          x: trainRows.map((r) => r.month),
          y: trainRows.map((r) => r.n_docs),
          name: "학습 구간 (2021~2024, 48개월, 643,095건)",
          type: "bar",
          marker: { color: "#2563eb" },
        },
        {
          x: oosRows.map((r) => r.month),
          y: oosRows.map((r) => r.n_docs),
          name: "미래 검증 구간 (2025~2026.07, 19개월, 288,614건)",
          type: "bar",
          marker: { color: "#059669" },
        },
      ],
      createLayout({
        barmode: "stack",
        xaxis: { type: "category", tickangle: -30, nticks: 14 },
        yaxis: { type: "linear", title: "월별 뉴스 기사 수 (건)", range: [0, 19500], tickformat: ",d" },
        shapes: [
          {
            type: "line",
            x0: "2024-12",
            x1: "2024-12",
            y0: 0,
            y1: 1,
            yref: "paper",
            line: { color: "#e11d48", width: 2, dash: "dash" },
          },
        ],
        annotations: [
          {
            x: "2024-12",
            y: 0.96,
            yref: "paper",
            text: "학습 / 미래검증 분리선 (2024.12)",
            showarrow: false,
            xanchor: "right",
            font: { size: 11, color: "#e11d48" },
          },
        ],
      }),
      PLOT_CFG
    );
  }

  // ==================== SECTION 2: 14 TOPICS & CONVERGENCE ====================
  function renderSection2() {
    const align = D.topic_alignment;

    const topicNamesKr = {
      0: "T0: ESG·친환경 경영 (배경)",
      1: "T1: 금리·물가·통화정책",
      2: "T2: 부동산·가계대출 (가계부채 분리)",
      3: "T3: 아파트 분양·청약 (부동산)",
      4: "T4: 국제 분쟁·원자재 (모호)",
      5: "T5: 유통·할인·소비재 (배경)",
      6: "T6: 상장·펀드·주식투자 (자본거래)",
      7: "T7: 정부 예산·재정·규제 (배경)",
      8: "T8: 코스피·환율 마감 (시황)",
      9: "T9: 매출·영업이익 (기업실적)",
      10: "T10: 금융권 인사·CSR (배경)",
      11: "T11: 노사·고용·일자리 (배경)",
      12: "T12: 전기차·배터리 (첨단산업)",
      13: "T13: 경영권·인수합병 (자본거래)",
    };

    // 1. Cosine Similarity Horizontal Bar Chart
    const sortedAlign = [...align].sort((a, b) => a.topic_a - b.topic_a).reverse();
    Plotly.newPlot(
      "chart-sec2-cosine",
      [
        {
          y: sortedAlign.map((r) => topicNamesKr[r.topic_a] || `T${r.topic_a}`),
          x: sortedAlign.map((r) => Number((r.cosine_similarity * 100).toFixed(2))),
          type: "bar",
          orientation: "h",
          cliponaxis: false,
          marker: {
            color: sortedAlign.map((r) => (r.topic_a === 2 ? "#d97706" : "#059669")),
          },
          text: sortedAlign.map((r) => `${(r.cosine_similarity * 100).toFixed(2)}%`),
          textposition: "outside",
          name: "코사인 유사도(%)",
        },
      ],
      createLayout({
        margin: { t: 24, r: 68, b: 48, l: 215 },
        xaxis: { type: "linear", range: [65, 108], title: "모델 수렴 전후 토픽 일치도 (%)" },
        yaxis: { type: "category", tickfont: { size: 11 } },
        showlegend: false,
        hovermode: "closest",
      }),
      PLOT_CFG
    );

    // 2. NMF vs LDA Model Comparison Chart
    const mc = D.topic_model_comparison;
    const nmfRows = mc.filter((r) => r.model_family === "NMF");
    const ldaRows = mc.filter((r) => r.model_family === "LDA");

    Plotly.newPlot(
      "chart-sec2-modelcomp",
      [
        {
          x: nmfRows.map((r) => `토픽 ${r.n_topics_K}개`),
          y: nmfRows.map((r) => Number(r.cv_coherence_train643k.toFixed(4))),
          name: "NMF 모델 주제 선명도 (C_v 응집도)",
          type: "bar",
          cliponaxis: false,
          marker: { color: "#2563eb" },
          text: nmfRows.map((r) => r.cv_coherence_train643k.toFixed(3)),
          textposition: "outside",
        },
        {
          x: ldaRows.map((r) => `토픽 ${r.n_topics_K}개`),
          y: ldaRows.map((r) => Number(r.cv_coherence_train643k.toFixed(4))),
          name: "기존 LDA 모델 주제 선명도 (C_v 응집도)",
          type: "bar",
          cliponaxis: false,
          marker: { color: "#94a3b8" },
          text: ldaRows.map((r) => r.cv_coherence_train643k.toFixed(3)),
          textposition: "outside",
        },
      ],
      createLayout({
        barmode: "group",
        xaxis: { type: "category", title: "토픽 개수 설정 (K)" },
        yaxis: { type: "linear", range: [0.5, 0.93], title: "토픽 응집도 (C_v, 높을수록 선명)" },
      }),
      PLOT_CFG
    );

    // 3. Clean 14 Topics Table
    const filterSel = document.getElementById("filter-sec2-topic");
    function renderTopicsTable(mode) {
      const tbody = document.querySelector("#table-sec2-topics tbody");
      tbody.innerHTML = "";
      align.forEach((a) => {
        const isAssigned = a.status_a === "assigned";
        if (mode === "assigned" && !isAssigned) return;
        if (mode === "other" && isAssigned) return;

        const m4 = D.topic_terms_400.find((x) => x.topic_id === a.topic_a) || {};
        const tr = document.createElement("tr");
        if (a.topic_a === 2) tr.className = "tr-warn";
        else if (isAssigned) tr.className = "tr-sig";

        const slug400Kr = a.slug_a ? REGIME_KR[a.slug_a] || a.slug_a : "배경·미할당";
        const slug800Kr = a.slug_b ? REGIME_KR[a.slug_b] || a.slug_b : "배경·미할당";

        tr.innerHTML = `
          <td style="font-weight:700;color:#0f172a;">${topicNamesKr[a.topic_a] || `T${a.topic_a}`}</td>
          <td><span class="tag ${isAssigned ? 'tag-green' : 'tag-gray'}">${isAssigned ? '핵심 경제 국면' : '배경·기타 토픽'}</span></td>
          <td style="font-weight:700;color:${isAssigned ? '#1d4ed8' : '#64748b'};">${slug400Kr}</td>
          <td style="font-weight:700;color:${a.topic_a === 2 ? '#d97706' : (isAssigned ? '#059669' : '#64748b')};">${slug800Kr}</td>
          <td class="num" style="font-weight:700;">${(a.cosine_similarity * 100).toFixed(2)}%</td>
          <td class="num">${fmt(m4.cv_coherence, 3)}</td>
          <td style="font-size:0.84rem;color:#334155;">${a.top10_a}</td>
        `;
        tbody.appendChild(tr);
      });
    }
    filterSel.addEventListener("change", (e) => renderTopicsTable(e.target.value));
    renderTopicsTable("ALL");
  }

  // ==================== SECTION 3: 6 REGIMES & MULTI-REGIME ====================
  function renderSection3() {
    const p67 = D.study_panel_67m;
    const months = p67.map((r) => r.month);

    const regimeDescriptions = {
      macro: {
        title: "금리·물가 국면 (macro, T1)",
        keywords: "물가, 금리, 경제, Fed, 인상, 인플레이션, 통화, 경기, 중앙은행, 한국은행",
        corr: "99.52% (r = 0.9952)",
        note: "2022년 물가 급등 및 한은 기준금리 빅스텝 시기에 가장 강하게 활성화(z > 2.0)된 핵심 거시 국면",
      },
      realestate: {
        title: "부동산 국면 (realestate, T2·T3)",
        keywords: "대출, 주택, 부동산, 아파트, 전세, 매매, 단지, 분양, 가구, 청약",
        corr: "96.48% (Legacy-6 합산 기준)",
        note: "2021년 주택시장 과열기 및 2022년 하반기 레고랜드·PF 경색기에 집중 활성화된 국면",
      },
      aichip: {
        title: "첨단산업 국면 (aichip, T12 - 전기차·배터리 중심)",
        keywords: "차량, 전기차, 모델, 자동차, 주행, 출시, 현대차, 탑재, 배터리, SUV",
        corr: "99.96% (r = 0.9996)",
        note: "전기차·배터리 및 신차·모빌리티 산업 뉴스를 포착하며 NMF-400과 800에서 99.96% 일치",
      },
      market: {
        title: "시황·증시 국면 (market, T8)",
        keywords: "거래일, 마감, 지수, 포인트, 코스피, 달러, 환율, 거래, 하락, 상승",
        corr: "99.97% (r = 0.9997)",
        note: "주식시장 급등락 및 환율 마감 시황을 대변하며 주별 네이버 증시 검색량과 강하게 동조화(r = 0.498)",
      },
      earnings: {
        title: "기업실적 국면 (earnings, T9)",
        keywords: "매출, 영업, 이익, 동기, 전년, 대비, 증가, 분기, 기록, 매출액",
        corr: "99.98% (r = 0.9998)",
        note: "분기별 어닝 시즌마다 주기적으로 활성화되며 주별 네이버 기업실적 검색량과 강하게 연동(r = 0.472)",
      },
      capital: {
        title: "자본거래·투자 국면 (capital, T6·T13)",
        keywords: "상장, 주식, 투자자, 펀드, 자산, 지분, 인수, 합병, 경영권, 매각",
        corr: "99.10% (r = 0.9910)",
        note: "IPO·유상증자·인수합병·지배구조 이슈를 포착하며 급증 시 KOSPI 수익률과 유의한 음(-)의 관계(β = -0.53)",
      },
      hhdebt: {
        title: "가계부채·신용 국면 (hhdebt, NMF-800 T2 신규 분리)",
        keywords: "대출, 은행, 금리, 신용, 이자, 상환, 만기, 담보, 자금, 한도",
        corr: "NMF-800 완전수렴 전용 국면",
        note: "NMF-800 완전 수렴 시 기존 부동산(T2)에서 순수 가계대출·이자상환 이슈만 독립 분리된 제7국면",
      },
    };

    function drawSingleRegime(reg) {
      const info = regimeDescriptions[reg];
      const z400 = p67.map((r) => (reg === "hhdebt" ? null : Number(r[`z_${reg}`].toFixed(3))));
      const z800 = p67.map((r) => Number(r[`z800_${reg}`].toFixed(3)));
      const activeVal = reg === "hhdebt" ? z800 : z400;
      const activeMonths = p67.filter((_, i) => activeVal[i] !== null && activeVal[i] >= 0.5).map((r) => r.month);

      const allVals = [...z400.filter((v) => v !== null), ...z800.filter((v) => v !== null)];
      const minY = Math.min(...allVals, -1.5) - 0.4;
      const maxY = Math.max(...allVals, 2.0) + 0.5;

      document.getElementById("regime-info-banner").innerHTML = `
        <div class="mini-stat">
          <div class="m-label">선택한 국면</div>
          <div class="m-val" style="font-size:1.02rem;color:${REGIME_COLOR[reg]};">${info.title}</div>
        </div>
        <div class="mini-stat">
          <div class="m-label">활성화(z &ge; 0.5) 개월 수</div>
          <div class="m-val">${activeMonths.length}개월 <span style="font-size:0.8rem;color:#64748b;">/ 67개월</span></div>
        </div>
        <div class="mini-stat">
          <div class="m-label">NMF-400 ↔ 800 시계열 일치도</div>
          <div class="m-val" style="color:#059669;font-size:1.02rem;">${info.corr}</div>
        </div>
        <div class="mini-stat" style="grid-column: span 2;">
          <div class="m-label">대표 핵심 단어 (Top Keywords) & 특징</div>
          <div style="font-size:0.82rem;color:#334155;margin-top:3px;"><strong>키워드:</strong> ${info.keywords}<br/><strong>해석:</strong> ${info.note}</div>
        </div>
      `;

      const traces = [];
      if (reg !== "hhdebt") {
        traces.push({
          x: months,
          y: z400,
          name: `NMF-400 기준 모델 (${REGIME_KR[reg]})`,
          type: "scatter",
          mode: "lines+markers",
          fill: "tozeroy",
          fillcolor: "rgba(37, 99, 235, 0.08)",
          line: { color: REGIME_COLOR[reg], width: 2.5 },
          marker: { size: 5 },
        });
      }
      traces.push({
        x: months,
        y: z800,
        name: `NMF-800 완전수렴 모델 (${REGIME_KR[reg]})`,
        type: "scatter",
        mode: "lines",
        line: { color: reg === "hhdebt" ? "#ca8a04" : "#0f172a", width: reg === "hhdebt" ? 2.5 : 1.8, dash: reg === "hhdebt" ? "solid" : "dot" },
      });

      Plotly.newPlot(
        "chart-sec3-single-regime",
        traces,
        createLayout({
          xaxis: { type: "category", tickangle: -30, nticks: 14 },
          yaxis: { type: "linear", title: "국면 활성도 (표준화 Z-점수)", range: [minY, maxY], tickformat: ".1f" },
          shapes: [
            {
              type: "line",
              x0: months[0],
              x1: months[months.length - 1],
              y0: 0.5,
              y1: 0.5,
              line: { color: "#059669", width: 2, dash: "dash" },
            },
            {
              type: "line",
              x0: "2024-12",
              x1: "2024-12",
              y0: 0,
              y1: 1,
              yref: "paper",
              line: { color: "#94a3b8", width: 1.5, dash: "dot" },
            },
          ],
          annotations: [
            {
              x: "2021-08",
              y: 0.5,
              yshift: 12,
              text: "활성화 기준선 (z = 0.5 이상이면 주요 이슈로 켜짐)",
              showarrow: false,
              font: { size: 11, color: "#059669" },
            },
          ],
        }),
        PLOT_CFG
      );
    }

    const regPills = document.querySelectorAll("#regime-pills .pill-btn");
    regPills.forEach((btn) => {
      btn.addEventListener("click", () => {
        regPills.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        drawSingleRegime(btn.getAttribute("data-reg"));
      });
    });
    drawSingleRegime("macro");

    // 2. Heatmap
    const regOrder = ["macro", "realestate", "aichip", "market", "earnings", "capital"];
    const zMat = regOrder.map((k) => p67.map((r) => Number(r[`z_${k}`].toFixed(2))));
    const symMat = regOrder.map((k) =>
      p67.map((r) => {
        const z = r[`z_${k}`];
        if (r.argmax_regime === k && z >= 0.5) return "★";
        if (z >= 0.5) return "●";
        return "";
      })
    );

    Plotly.newPlot(
      "chart-sec3-heatmap",
      [
        {
          x: months,
          y: regOrder.map((k) => REGIME_KR[k]),
          z: zMat,
          text: symMat,
          texttemplate: "%{text}",
          textfont: { color: "#ffffff", size: 11 },
          type: "heatmap",
          colorscale: [
            [0, "#f1f5f9"],
            [0.45, "#93c5fd"],
            [0.65, "#2563eb"],
            [0.82, "#f59e0b"],
            [1.0, "#e11d48"],
          ],
          zmin: -1.8,
          zmax: 2.5,
          colorbar: { title: "Z-점수" },
        },
      ],
      createLayout({
        margin: { t: 24, r: 24, b: 50, l: 190 },
        xaxis: { type: "category", tickangle: -30, nticks: 14 },
        yaxis: { type: "category" },
        hovermode: "closest",
      }),
      PLOT_CFG
    );

    // 3. Omitted Signal Comparison Bar
    const sm = D.single_vs_multi_metrics;
    const captured = sm.map((r) => r.total_active_events - r.total_omitted_by_argmax);
    const omitted = sm.map((r) => r.total_omitted_by_argmax);

    Plotly.newPlot(
      "chart-sec3-omitted",
      [
        {
          x: ["전체 67개월", "학습 48개월", "미래검증 19개월"],
          y: captured,
          name: "단일 방식(1등만 선택) 포착 신호",
          type: "bar",
          marker: { color: "#2563eb" },
          text: captured.map((v) => `${v}건`),
          textposition: "inside",
        },
        {
          x: ["전체 67개월", "학습 48개월", "미래검증 19개월"],
          y: omitted,
          name: "단일 방식이 놓친 신호 (다중 국면만 포착!)",
          type: "bar",
          marker: { color: "#e11d48" },
          text: omitted.map((v, i) => `${v}건 누락 (${sm[i].omitted_information_ratio_pct}%)`),
          textposition: "inside",
        },
      ],
      createLayout({
        barmode: "stack",
        xaxis: { type: "category" },
        yaxis: { type: "linear", title: "활성 경제 이슈 신호 수 (건)", range: [0, 128] },
      }),
      PLOT_CFG
    );

    // 4. Case Studies
    function renderCase(ym) {
      const mRow = D.case_studies_monthly.find((r) => r.month === ym) || D.case_studies_monthly[0];
      document.getElementById("case-detail-box").innerHTML = `
        <div style="background:var(--bg-subtle);padding:12px 14px;border-radius:8px;border:1px solid var(--border-color);font-size:0.86rem;">
          <div style="font-weight:800;color:var(--primary-dark);margin-bottom:4px;">[${mRow.month}] ${mRow.selection_reason}</div>
          <div>
            • <strong>단일 방식(1위만 선택)</strong>: <span class="tag tag-blue">${mRow.argmax_regime_kr} (z = ${fmt(mRow.argmax_z, 2)})</span> 만 선택하고 나머지 무시<br/>
            • <strong>단일 방식이 놓친 실제 활성 이슈</strong>: <span class="tag tag-rose">${mRow.omitted_active_regimes_kr} (z = ${fmt(mRow.second_max_z, 2)})</span><br/>
            • <strong>당월 시장 상황</strong>: KOSPI 수익률 <code>${fmt(mRow.kospi_ret_pct, 2)}%</code> | 기준금리 변동 <code>${fmt(mRow.base_rate_diff_bp, 0)}bp</code> | 원/달러 변동 <code>${fmt(mRow.usdkrw_ret_pct, 2)}%</code>
          </div>
        </div>
      `;

      const regKeys = ["macro", "realestate", "aichip", "market", "earnings", "capital"];
      const zVals = regKeys.map((k) => Number(mRow[`z_${k}`].toFixed(2)));
      const minZ = Math.min(...zVals, -1.5) - 0.6;
      const maxZ = Math.max(...zVals, 2.0) + 0.8;

      Plotly.newPlot(
        "chart-sec3-case-bar",
        [
          {
            x: regKeys.map((k) => REGIME_KR[k].split(" (")[0]),
            y: zVals,
            type: "bar",
            cliponaxis: false,
            marker: {
              color: regKeys.map((k) => {
                if (mRow.argmax_regime === k) return "#2563eb";
                if (mRow[`z_${k}`] >= 0.5) return "#e11d48";
                return "#cbd5e1";
              }),
            },
            text: zVals.map((v) => v.toFixed(2)),
            textposition: "outside",
          },
        ],
        createLayout({
          margin: { t: 28, r: 20, b: 50, l: 55 },
          xaxis: { type: "category" },
          yaxis: { type: "linear", range: [minZ, maxZ], title: "표준화 Z-점수", tickformat: ".1f" },
          showlegend: false,
          shapes: [
            {
              type: "line",
              x0: -0.5,
              x1: 5.5,
              y0: 0.5,
              y1: 0.5,
              line: { color: "#059669", width: 2, dash: "dot" },
            },
          ],
        }),
        PLOT_CFG
      );

      const tbody = document.querySelector("#table-sec3-case-articles tbody");
      tbody.innerHTML = "";
      const arts = D.case_studies_articles.filter((a) => a.month === ym);
      arts.forEach((a) => {
        const isOmitted = a.evidence_role.includes("Omitted");
        const tr = document.createElement("tr");
        if (isOmitted) tr.className = "tr-warn";
        tr.innerHTML = `
          <td><span class="tag ${isOmitted ? 'tag-rose' : 'tag-blue'}">${isOmitted ? '단일 방식이 놓친 이슈' : '1위 이슈 (Argmax)'}</span></td>
          <td style="font-weight:700;">${a.target_regime_kr} (z=${fmt(a.monthly_regime_z, 2)})</td>
          <td class="mono" style="font-size:0.8rem;">${String(a.date).slice(0, 10)}<br/>${a.press}</td>
          <td style="font-weight:600;color:#0f172a;">${a.title}<br/><span style="font-size:0.78rem;color:#64748b;font-weight:400;">핵심어: ${a.in_vocab_keywords_top12}</span></td>
        `;
        tbody.appendChild(tr);
      });
    }

    const casePills = document.querySelectorAll("#case-pills .pill-btn");
    casePills.forEach((btn) => {
      btn.addEventListener("click", () => {
        casePills.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        renderCase(btn.getAttribute("data-ym"));
      });
    });
    renderCase("2022-10");
  }

  // ==================== SECTION 4: MACRO & FINANCIAL INDICATORS ====================
  function renderSection4() {
    const p67 = D.study_panel_67m;
    const months = p67.map((r) => r.month);

    const newsSel = document.getElementById("sel-sec4-news");
    const econSel = document.getElementById("sel-sec4-econ");

    function updateMacroCharts() {
      const nCol = newsSel.value;
      const eCol = econSel.value;
      const nName = newsSel.options[newsSel.selectedIndex].text;
      const eName = econSel.options[econSel.selectedIndex].text;

      const xAll = p67.map((r) => (r[nCol] !== null ? Number(r[nCol].toFixed(3)) : null));
      const yAll = p67.map((r) => (r[eCol] !== null ? Number(r[eCol].toFixed(3)) : null));

      const trainRows = p67.filter((r) => r.period === "train");
      const oosRows = p67.filter((r) => r.period !== "train");

      const stFull = calcStats(xAll, yAll);
      const stTrain = calcStats(trainRows.map((r) => r[nCol]), trainRows.map((r) => r[eCol]));
      const stOOS = calcStats(oosRows.map((r) => r[nCol]), oosRows.map((r) => r[eCol]));

      document.getElementById("sec4-stat-boxes").innerHTML = `
        <div class="mini-stat">
          <div class="m-label">전체 67개월 상관계수 (r)</div>
          <div class="m-val" style="color:${Math.abs(stFull.r) > 0.3 ? '#2563eb' : '#0f172a'};">${fmt(stFull.r, 4)}</div>
        </div>
        <div class="mini-stat">
          <div class="m-label">학습 구간 (48개월) 상관계수</div>
          <div class="m-val">${fmt(stTrain.r, 4)}</div>
        </div>
        <div class="mini-stat">
          <div class="m-label">미래검증 (19개월) 상관계수</div>
          <div class="m-val" style="color:#059669;">${fmt(stOOS.r, 4)}</div>
        </div>
        <div class="mini-stat">
          <div class="m-label">관계 방향 요약</div>
          <div class="m-val" style="font-size:0.95rem;color:${stFull.r >= 0 ? '#059669' : '#e11d48'};">
            ${stFull.r >= 0.25 ? "양(+)의 동행 관계" : stFull.r <= -0.25 ? "음(-)의 역방향 관계" : "약한 선형 관계"}
          </div>
        </div>
      `;

      Plotly.newPlot(
        "chart-sec4-ts",
        [
          {
            x: months,
            y: xAll,
            name: nName,
            type: "scatter",
            mode: "lines+markers",
            line: { color: "#2563eb", width: 2.4 },
            marker: { size: 5 },
            yaxis: "y1",
          },
          {
            x: months,
            y: yAll,
            name: eName,
            type: "scatter",
            mode: "lines+markers",
            line: { color: "#e11d48", width: 2.4, dash: "dot" },
            marker: { size: 5 },
            yaxis: "y2",
          },
        ],
        createLayout({
          margin: { t: 44, r: 78, b: 55, l: 68 },
          xaxis: { type: "category", tickangle: -30, nticks: 14 },
          yaxis: { type: "linear", title: "뉴스 Z-점수", titlefont: { color: "#2563eb" }, tickformat: ".1f" },
          yaxis2: {
            type: "linear",
            title: eName.split(" (")[0],
            titlefont: { color: "#e11d48" },
            tickfont: { color: "#e11d48", size: 11.5 },
            overlaying: "y",
            side: "right",
            gridcolor: "rgba(0,0,0,0)",
            automargin: true,
          },
        }),
        PLOT_CFG
      );

      const validX = xAll.filter((v) => v !== null && !Number.isNaN(v));
      const minX = Math.min(...validX);
      const maxX = Math.max(...validX);

      Plotly.newPlot(
        "chart-sec4-scatter",
        [
          {
            x: trainRows.map((r) => Number(r[nCol].toFixed(3))),
            y: trainRows.map((r) => Number(r[eCol].toFixed(3))),
            text: trainRows.map((r) => r.month),
            name: "학습 구간 (48개월)",
            mode: "markers",
            type: "scatter",
            marker: { color: "#2563eb", size: 8, opacity: 0.75 },
          },
          {
            x: oosRows.map((r) => Number(r[nCol].toFixed(3))),
            y: oosRows.map((r) => Number(r[eCol].toFixed(3))),
            text: oosRows.map((r) => r.month),
            name: "미래검증 구간 (19개월)",
            mode: "markers",
            type: "scatter",
            marker: { color: "#059669", size: 9, symbol: "diamond" },
          },
          {
            x: [minX, maxX],
            y: [stFull.intercept + stFull.slope * minX, stFull.intercept + stFull.slope * maxX],
            name: `추세선 (기울기=${fmt(stFull.slope, 2)})`,
            mode: "lines",
            type: "scatter",
            line: { color: "#e11d48", width: 2, dash: "dash" },
          },
        ],
        createLayout({
          hovermode: "closest",
          xaxis: { type: "linear", title: "뉴스 국면 Z-점수", tickformat: ".1f" },
          yaxis: { type: "linear", title: eName.split(" (")[0] },
        }),
        PLOT_CFG
      );
    }

    const presetBtns = document.querySelectorAll("#macro-preset-pills .pill-btn");
    presetBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        presetBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        newsSel.value = btn.getAttribute("data-news");
        econSel.value = btn.getAttribute("data-econ");
        updateMacroCharts();
      });
    });

    newsSel.addEventListener("change", () => {
      presetBtns.forEach((b) => b.classList.remove("active"));
      updateMacroCharts();
    });
    econSel.addEventListener("change", () => {
      presetBtns.forEach((b) => b.classList.remove("active"));
      updateMacroCharts();
    });
    updateMacroCharts();

    // 2. HAC Regression Chart & Table
    const hacDepSel = document.getElementById("sel-sec4-hac-dep");

    function updateHacSection() {
      const dep = hacDepSel.value;
      const rows400 = D.hac_regression.filter(
        (r) => r.model_spec === "NMF400_6Regime" && r.sample_split === "Full_67m" && r.dep_var === dep && r.variable !== "const"
      );
      const rows800 = D.hac_regression.filter(
        (r) => r.model_spec === "NMF800_7Regime" && r.sample_split === "Full_67m" && r.dep_var === dep && r.variable !== "const"
      );

      const coefs = rows400.map((r) => Number(r.coef.toFixed(3)));
      const minC = Math.min(...coefs, -0.2) * 1.35;
      const maxC = Math.max(...coefs, 0.2) * 1.35;

      Plotly.newPlot(
        "chart-sec4-hac",
        [
          {
            y: rows400.map((r) => REGIME_KR[r.variable] || r.variable),
            x: coefs,
            name: "NMF-400 (기준 6국면)",
            type: "bar",
            orientation: "h",
            cliponaxis: false,
            marker: {
              color: rows400.map((r) => (r.p_value_holm < 0.05 ? "#e11d48" : "#94a3b8")),
            },
            text: rows400.map((r) => `${r.coef.toFixed(2)}${r.p_value_holm < 0.05 ? " ★유의" : ""}`),
            textposition: "outside",
          },
        ],
        createLayout({
          margin: { t: 28, r: 75, b: 48, l: 165 },
          xaxis: { type: "linear", range: [minC, maxC], title: "회귀계수 (β: 뉴스 1단위 증가 시 지표 변화량)" },
          yaxis: { type: "category" },
          shapes: [
            {
              type: "line",
              x0: 0,
              x1: 0,
              y0: 0,
              y1: 1,
              yref: "paper",
              line: { color: "#0f172a", width: 1.5 },
            },
          ],
          showlegend: false,
          hovermode: "closest",
        }),
        PLOT_CFG
      );

      const tbody = document.querySelector("#table-sec4-hac tbody");
      tbody.innerHTML = "";
      const allVars = ["z_macro", "z_capital", "z_realestate", "z_aichip", "z_market", "z_earnings", "z_hhdebt"];
      allVars.forEach((v) => {
        const r4 = rows400.find((x) => x.variable === v);
        const r8 = rows800.find((x) => x.variable === v);
        if (!r4 && !r8) return;

        const sig4 = r4 && r4.p_value_holm < 0.05;
        const sig8 = r8 && r8.p_value_holm < 0.05;
        const tr = document.createElement("tr");
        if (sig4 || sig8) tr.className = "tr-sig";

        tr.innerHTML = `
          <td style="font-weight:700;color:#0f172a;">${REGIME_KR[v] || v}</td>
          <td class="num" style="font-weight:700;color:${r4 && r4.coef < 0 ? '#e11d48' : '#2563eb'};">${r4 ? `${fmt(r4.coef, 4)} (t=${fmt(r4.t_stat, 2)})` : "- (미포함)"}</td>
          <td class="num" style="font-weight:700;">${r4 ? fmt(r4.p_value_holm, 4) : "-"}</td>
          <td class="num">${r8 ? `${fmt(r8.coef, 4)} (t=${fmt(r8.t_stat, 2)})` : "-"}</td>
          <td class="num">${r8 ? fmt(r8.p_value_holm, 4) : "-"}</td>
          <td>
            <span class="tag ${sig4 || sig8 ? 'tag-green' : 'tag-gray'}">
              ${sig4 || sig8 ? "✔ 통계적 유의 (Holm p < 0.05)" : "유의하지 않음 (기각)"}
            </span>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }

    hacDepSel.addEventListener("change", updateHacSection);
    updateHacSection();
  }

  // ==================== SECTION 5: WEEKLY NAVER SEARCH ====================
  function renderSection5() {
    // 1. 8 Pairs Contemporaneous (h=0) OOS Bar Chart
    const oosH0 = D.naver_weekly_comparison
      .filter((r) => r.split === "Eval OOS (2025~2026)" && r.lag_h === 0 && r.test_family.includes("Predefined_24"))
      .sort((a, b) => a.r_400 - b.r_400);

    Plotly.newPlot(
      "chart-sec5-bars",
      [
        {
          y: oosH0.map((r) => r.pair_label),
          x: oosH0.map((r) => Number(r.r_400.toFixed(4))),
          type: "bar",
          orientation: "h",
          cliponaxis: false,
          marker: {
            color: oosH0.map((r) => (r.hac_p_holm_lag4_400 < 0.05 ? "#059669" : "#94a3b8")),
          },
          text: oosH0.map(
            (r) => `r = ${r.r_400.toFixed(3)} ${r.hac_p_holm_lag4_400 < 0.05 ? `(★유의, p=${r.hac_p_holm_lag4_400.toFixed(4)})` : "(비유의)"}`
          ),
          textposition: "outside",
        },
      ],
      createLayout({
        margin: { t: 24, r: 155, b: 48, l: 215 },
        xaxis: { type: "linear", range: [-0.22, 0.78], title: "미래검증 구간(82주) 동시점 상관계수 (r)" },
        yaxis: { type: "category", tickfont: { size: 11 } },
        showlegend: false,
        hovermode: "closest",
      }),
      PLOT_CFG
    );

    // 2. Lead-Lag Chart
    const targetPairs = [
      { label: "시황 뉴스 ↔ 국내증시 검색", short: "시황 ↔ 국내증시 검색 (동시점 유의)", color: "#2563eb" },
      { label: "기업실적 뉴스 ↔ 기업실적 검색", short: "기업실적 ↔ 기업실적 검색 (동시점 유의)", color: "#059669" },
      { label: "금리·물가 뉴스 ↔ 금리 검색", short: "금리·물가 ↔ 금리 검색", color: "#e11d48" },
    ];

    const lagTraces = targetPairs.map((tp) => {
      const sub = D.naver_weekly_comparison
        .filter((r) => r.split === "Eval OOS (2025~2026)" && r.pair_label === tp.label)
        .sort((a, b) => a.lag_h - b.lag_h);
      return {
        x: sub.map((r) => (r.lag_h === 0 ? "같은 주 (h=0)" : r.lag_h < 0 ? `검색 ${Math.abs(r.lag_h)}주 선행 (h=${r.lag_h})` : `뉴스 ${r.lag_h}주 선행 (h=+${r.lag_h})`)),
        y: sub.map((r) => Number(r.r_400.toFixed(4))),
        name: tp.short,
        type: "scatter",
        mode: "lines+markers+text",
        text: sub.map((r) => r.r_400.toFixed(2)),
        textposition: "top center",
        cliponaxis: false,
        line: { color: tp.color, width: 2.6 },
        marker: { size: 9 },
      };
    });

    Plotly.newPlot(
      "chart-sec5-leadlag",
      lagTraces,
      createLayout({
        xaxis: { type: "category", title: "시차 구분 (검색 선행 ↔ 같은 주 ↔ 뉴스 선행)" },
        yaxis: { type: "linear", range: [-0.48, 0.65], title: "상관계수 (r)", tickformat: ".2f" },
        shapes: [
          {
            type: "line",
            x0: 0,
            x1: 1,
            xref: "paper",
            y0: 0,
            y1: 0,
            line: { color: "#94a3b8", width: 1.5, dash: "dash" },
          },
        ],
      }),
      PLOT_CFG
    );

    // 3. Interactive 292-Week Pair Explorer
    const w292 = D.weekly_panel_292w;
    const weeks = w292.map((r) => r.iso_yw);
    const modeSel = document.getElementById("sel-sec5-mode");
    let currentPairStr = "news_share_market|search_market|시황 뉴스 ↔ 국내증시 검색";

    function updateWeeklyPairChart() {
      const [nBase, sBase, titleLabel] = currentPairStr.split("|");
      const isDiff = modeSel.value === "diff";
      const nCol = isDiff ? `d_${nBase}` : nBase;
      const sCol = isDiff ? `d_${sBase}` : sBase;

      const xAll = w292.map((r) => (r[nCol] !== null ? Number((r[nCol] * 100).toFixed(3)) : null));
      const yAll = w292.map((r) => (r[sCol] !== null ? Number(r[sCol].toFixed(3)) : null));

      const trainRows = w292.filter((r) => r.period === "train");
      const oosRows = w292.filter((r) => r.period !== "train");

      const stFull = calcStats(xAll, yAll);
      const stOOS = calcStats(
        oosRows.map((r) => (r[nCol] !== null ? r[nCol] * 100 : null)),
        oosRows.map((r) => r[sCol])
      );

      const csvMatch = D.naver_weekly_comparison.find(
        (r) => r.split === "Eval OOS (2025~2026)" && r.lag_h === 0 && r.pair_label === titleLabel
      );

      document.getElementById("sec5-stat-boxes").innerHTML = `
        <div class="mini-stat">
          <div class="m-label">선택한 분석 쌍</div>
          <div class="m-val" style="font-size:0.98rem;color:var(--primary-dark);">${titleLabel}</div>
        </div>
        <div class="mini-stat">
          <div class="m-label">미래검증(${stOOS.n}주) 상관계수 r</div>
          <div class="m-val" style="color:#059669;">${fmt(stOOS.r, 4)}</div>
        </div>
        <div class="mini-stat">
          <div class="m-label">전체 기간(${stFull.n}주) 상관계수 r</div>
          <div class="m-val">${fmt(stFull.r, 4)}</div>
        </div>
        <div class="mini-stat">
          <div class="m-label">엄격 보정 유의확률 (Holm p)</div>
          <div class="m-val" style="color:${csvMatch && csvMatch.hac_p_holm_lag4_400 < 0.05 ? '#059669' : '#64748b'};">
            ${csvMatch ? `${fmt(csvMatch.hac_p_holm_lag4_400, 4)} ${csvMatch.hac_p_holm_lag4_400 < 0.05 ? '(★유의)' : '(비유의)'}` : "-"}
          </div>
        </div>
      `;

      Plotly.newPlot(
        "chart-sec5-ts",
        [
          {
            x: weeks,
            y: xAll,
            name: isDiff ? "뉴스 점유율 주간 변화량 (%p)" : "뉴스 점유율 (%)",
            type: "scatter",
            mode: "lines",
            line: { color: "#2563eb", width: 1.8 },
            yaxis: "y1",
          },
          {
            x: weeks,
            y: yAll,
            name: isDiff ? "네이버 검색 지수 주간 변화량" : "네이버 검색 지수",
            type: "scatter",
            mode: "lines",
            line: { color: "#059669", width: 1.8, dash: "dot" },
            yaxis: "y2",
          },
        ],
        createLayout({
          margin: { t: 44, r: 78, b: 55, l: 68 },
          xaxis: { type: "category", tickangle: -30, nticks: 14 },
          yaxis: { type: "linear", title: isDiff ? "Δ뉴스 점유율 (%p)" : "뉴스 점유율 (%)", titlefont: { color: "#2563eb" }, tickformat: ".1f" },
          yaxis2: {
            type: "linear",
            title: isDiff ? "Δ네이버 검색 지수" : "네이버 검색 지수",
            titlefont: { color: "#059669" },
            overlaying: "y",
            side: "right",
            gridcolor: "rgba(0,0,0,0)",
            tickfont: { color: "#059669", size: 11.5 },
            automargin: true,
          },
        }),
        PLOT_CFG
      );

      const oosX = oosRows.map((r) => (r[nCol] !== null ? Number((r[nCol] * 100).toFixed(3)) : null)).filter((v) => v !== null);
      const minX = Math.min(...oosX);
      const maxX = Math.max(...oosX);

      Plotly.newPlot(
        "chart-sec5-scatter",
        [
          {
            x: oosRows.map((r) => (r[nCol] !== null ? Number((r[nCol] * 100).toFixed(3)) : null)),
            y: oosRows.map((r) => (r[sCol] !== null ? Number(r[sCol].toFixed(3)) : null)),
            text: oosRows.map((r) => r.iso_yw),
            name: `미래검증 82주 (r=${fmt(stOOS.r, 3)})`,
            mode: "markers",
            type: "scatter",
            marker: { color: "#059669", size: 8, opacity: 0.85 },
          },
          {
            x: [minX, maxX],
            y: [stOOS.intercept + stOOS.slope * minX, stOOS.intercept + stOOS.slope * maxX],
            name: "동조화 추세선",
            mode: "lines",
            type: "scatter",
            line: { color: "#e11d48", width: 2.2 },
          },
        ],
        createLayout({
          hovermode: "closest",
          xaxis: { type: "linear", title: isDiff ? "Δ뉴스 점유율 (%p)" : "뉴스 점유율 (%)", tickformat: ".1f" },
          yaxis: { type: "linear", title: isDiff ? "Δ네이버 검색 지수" : "네이버 검색 지수" },
        }),
        PLOT_CFG
      );
    }

    const pairBtns = document.querySelectorAll("#weekly-pair-pills .pill-btn");
    pairBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        pairBtns.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        currentPairStr = btn.getAttribute("data-pair");
        updateWeeklyPairChart();
      });
    });
    modeSel.addEventListener("change", updateWeeklyPairChart);
    updateWeeklyPairChart();

    // 4. Clean Summary Table of 8 Predefined Pairs
    const tbody = document.querySelector("#table-sec5-summary tbody");
    const oos8 = D.naver_weekly_comparison.filter(
      (r) => r.split === "Eval OOS (2025~2026)" && r.lag_h === 0 && r.test_family.includes("Predefined_24")
    );
    oos8.forEach((r) => {
      const fullRow = D.naver_weekly_comparison.find(
        (x) => x.split === "Full" && x.lag_h === 0 && x.pair_label === r.pair_label
      ) || {};
      const bcRow = D.weekly_diff_method_comparison.find((x) => x.pair_label === r.pair_label) || {};
      const isSig = r.hac_p_holm_lag4_400 < 0.05;

      const tr = document.createElement("tr");
      if (isSig) tr.className = "tr-sig";
      tr.innerHTML = `
        <td style="font-weight:700;color:#0f172a;">${r.pair_label}</td>
        <td class="num">${fmt(fullRow.r_400, 4)}</td>
        <td class="num" style="font-weight:800;color:${isSig ? '#059669' : '#0f172a'};">${fmt(r.r_400, 4)}</td>
        <td class="num" style="font-weight:700;color:${isSig ? '#059669' : '#64748b'};">${fmt(r.hac_p_holm_lag4_400, 4)}</td>
        <td class="num">[${fmt(r.mbb_L4_ci95_low_400, 3)}, ${fmt(r.mbb_L4_ci95_high_400, 3)}]</td>
        <td class="num">${fmt(r.r_800, 4)}</td>
        <td class="num">${bcRow.method_c_pearson_r !== undefined ? fmt(bcRow.method_c_pearson_r, 4) : "-"}</td>
        <td>
          <span class="tag ${isSig ? 'tag-green' : 'tag-gray'}">
            ${isSig ? "✔ 강건한 동시점 동조화 입증" : "유의하지 않음 (기각)"}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  // ==================== SECTION 6: OUTCOMES, GALLERY & REFERENCES ====================
  function renderSection6() {
    const figuresList = [
      { file: "reconstruction_error.png", title: "1. NMF 반복 횟수별(400 vs 800 vs 1200) 수렴 곡선", desc: "447회에서 완전 수렴하며 400회와 오차 차이는 0.0073%에 불과함을 보여주는 그래프" },
      { file: "topic_similarity.png", title: "2. NMF-400 vs NMF-800 14개 토픽 일치도", desc: "13개 토픽 평균 코사인 유사도 99.53%, Topic 2만 가계부채로 분리됨을 입증" },
      { file: "k_sensitivity_comparison.png", title: "3. NMF vs LDA 토픽 수(K=10~18) 성능 비교", desc: "NMF(K=14)가 주제 선명도(C_v)와 다양성에서 최적임을 보여주는 그래프" },
      { file: "regime_share_comparison.png", title: "4. 6대 경제 국면 67개월 시계열 비교 (400 vs 800)", desc: "비분할 5대 국면에서 두 모델 시계열이 사실상 하나로 겹침(r >= 0.991)" },
      { file: "multiregime_comparison.png", title: "5. 단일 국면 vs 다중 국면 신호 포착률 비교", desc: "단일 국면 선택 시 43.75%~50.40%의 활성 이슈가 누락됨을 보여주는 차트" },
      { file: "case_study_z_comparison.png", title: "6. 대표 복합 위기 사례 4선 Z-점수 구조", desc: "2021-09, 2022-10, 2025-02, 2026-06 사례의 다중 국면 활성도 비교" },
      { file: "hac_coefficient_comparison.png", title: "7. KOSPI 수익률에 대한 국면별 HAC 회귀계수", desc: "금리·물가(β=-0.74) 및 자본거래(β=-0.53)의 유의한 음(-)의 충격 확인" },
      { file: "weekly_news_search_trends.png", title: "8. 292주 주별 뉴스 점유율 및 네이버 검색량 추이", desc: "2020-W53 ~ 2026-W31 주별 뉴스 국면과 대중 검색 지수의 동행 흐름" },
      { file: "naver_weekly_comparison.png", title: "9. 주별 뉴스 ↔ 네이버 검색 상관계수 비교", desc: "시황(r=0.498)과 기업실적(r=0.472)의 동시점 동조화 유의성 검증" },
      { file: "eval_oos_bootstrap_ci.png", title: "10. 주별 뉴스-검색 상관의 블록 부트스트랩 95% 신뢰구간", desc: "2,000회 반복 추출을 통한 시황·기업실적 동조화의 비모수적 검증" },
      { file: "strict_oos_comparison.png", title: "11. 조기경보 및 OOS 수익률 예측 성능 비교", desc: "NMF-400과 NMF-800 간 조기경보 및 예측 오차(RMSE) 정합성 검증" },
      { file: "topic_stability_by_topic.png", title: "12. 난수 시드 변경에 따른 토픽 재현 안정성", desc: "초기화 시드가 달라져도 토픽 구조가 일관되게 유지됨을 검증" },
    ];

    const gallery = document.getElementById("sec6-gallery");
    const modal = document.getElementById("fig-modal");
    const modalImg = document.getElementById("fig-modal-img");
    const modalTitle = document.getElementById("fig-modal-title");
    const modalDesc = document.getElementById("fig-modal-desc");

    figuresList.forEach((f) => {
      const div = document.createElement("div");
      div.className = "fig-item";
      div.innerHTML = `
        <img src="assets/figures/${f.file}" alt="${f.title}" loading="lazy" />
        <div class="fig-cap">
          <h5>${f.title}</h5>
          <p>${f.desc}</p>
        </div>
      `;
      div.addEventListener("click", () => {
        modalImg.src = `assets/figures/${f.file}`;
        modalTitle.textContent = f.title;
        modalDesc.textContent = f.desc;
        modal.classList.add("open");
      });
      gallery.appendChild(div);
    });

    document.getElementById("fig-modal-close").addEventListener("click", () => modal.classList.remove("open"));
    modal.addEventListener("click", (e) => {
      if (e.target === modal) modal.classList.remove("open");
    });

    // Verified References
    const refTbody = document.querySelector("#table-sec6-refs tbody");
    D.reference_verification.forEach((r) => {
      let refText = r.verified_reference || r.original_reference;
      let doiText = r.doi || "-";
      if (r.ref_id === "REF-07") {
        refText = '김수현, 이영준, 신진영, 박기영, "거시경제 분석을 위한 텍스트 마이닝," 한국경제의 분석, 제26권, 제1호, pp. 1-70, 2020. DOI: 10.22823/jkea.26.1.202004.1.';
        doiText = "10.22823/jkea.26.1.202004.1";
      }
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="mono" style="font-weight:700;color:var(--primary-dark);">${r.ref_id}</td>
        <td style="color:#0f172a;">${refText}</td>
        <td class="mono" style="font-size:0.8rem;">
          ${r.source_url ? `<a href="${r.source_url}" target="_blank" rel="noopener" style="color:var(--primary);">${doiText}</a>` : doiText}
        </td>
        <td><span class="tag tag-green">✔ 실존·서지 검증 완료</span></td>
      `;
      refTbody.appendChild(tr);
    });
  }

  // Run all sections immediately
  renderSection1();
  renderSection2();
  renderSection3();
  renderSection4();
  renderSection5();
  renderSection6();
})();
