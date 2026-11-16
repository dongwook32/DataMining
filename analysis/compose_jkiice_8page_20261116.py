from pathlib import Path
import re, json, copy
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle, Image

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'paper_20261116'
OUT.mkdir(parents=True,exist_ok=True)
src=(ROOT/'docs/PAPER_DRAFT_JKIICE_8PAGE_REVIEW.md').read_text(encoding='utf-8')
old=[p.replace('<!-- column -->','').strip() for p in src.split('<!-- page -->')]

abstract='''This study examines how single-label summaries omit concurrent issues in Korean economic news. We analyze 931,709 articles from three business newspapers over 67 months, from January 2021 to July 2026. Vocabulary, TF-IDF weights, and a 14-topic non-negative matrix factorization basis were fitted on 48 training months and fixed for 19 evaluation months. Topics were mapped to six regimes, with activation defined by training-standardized scores of at least 0.5. Single-label summaries omitted 49 of 112 active signals (43.75%). A converged sensitivity specification retained a similar omission rate of 43.24%. Rates-and-inflation and capital-transaction regimes were negatively associated with contemporaneous volatility-scaled KOSPI returns. In 82 evaluation weeks, earnings news and related search changes showed positive co-movement that persisted across factorization settings. Market-news significance was sensitive to covariance settings. These findings quantify representation differences and contemporaneous associations; independent article labels and broader evaluation are required to establish semantic validity and practical usefulness.'''
p1=old[0].split('## ABSTRACT')[0]+'## ABSTRACT\n\n'+abstract+'\n\n**Keywords** Economic news, Multiple regimes, Non-negative matrix factorization, Out-of-sample evaluation, Search interest'
p1=p1.replace('**핵심어**','**키워드 :**').replace('**Keywords**','**Keywords :**')
p2=old[1].replace('Ⅴ절에서 적용 범위와 후속 검증 과제를 논의한다.','Ⅴ절에서 적용 범위와 한계를 논의하고, Ⅵ절에서 결론을 제시한다.')
p2=p2.replace('## Ⅱ. 관련 연구','## Ⅱ. 관련 연구\n\n### 2.1 경제 뉴스의 정량화와 이슈 표현')
p2=p2.replace('비음수 행렬 분해는','### 2.2 토픽 모델과 외부 지표의 비교\n\n비음수 행렬 분해는')
p2+='''

이상의 연구를 바탕으로 본 연구의 기여는 동일한 뉴스 특징과 임계값 아래에서 단일 대표 표시가 생략하는 활성 이슈의 수를 직접 계산하는 데 있다. 토픽 모형 자체의 새로운 알고리즘을 제안하기보다는, 학습과 평가 기간을 분리한 뉴스 표현 체계를 구성하고 그 표시 범위와 외부 지표의 동행성을 구분하여 평가한다. 따라서 응집도가 높거나 외부 지표와 상관이 있다는 사실을 곧바로 개별 기사 분류의 정확도로 해석하지 않는다.
'''
p2=p2.replace('이상의 연구를 바탕으로', '한국정보통신학회논문지의 김윤하·황보준권[13]은 빅카인즈 기사에 LDA를 적용하여 연도별 주제 변화를 분석하였다. 이처럼 뉴스 토픽의 해석과 시기별 비교는 정보통신 분야에서도 활용된다. 이상의 연구를 바탕으로')
p2=re.sub(r'시장 분석에서는 수익률에.*?활용하였다\.\s*','',p2,flags=re.S)
p2=p2.replace('이처럼 뉴스 토픽의 해석과 시기별 비교는 정보통신 분야에서도 활용된다. ','')
p3=old[2]
p3=p3.replace('> z(d,t) = [s(d,t) − μ(d)] / σ(d)    (1)','> z(d,t) = [s(d,t) − μ(d)] / σ(d)    (1)')
p3+='''

학습 내부 검증 표본은 적합 표본에 포함되지 않은 학습 기간 기사에서 매월 1,000건씩 추출하였다. 따라서 토픽 품질 비교에 사용한 48,000건과 시간적으로 분리된 19개월 평가 자료는 서로 역할이 다르다. 전자는 동일 기간 내 모형 비교이며, 후자는 고정된 특징 추출기의 이후 기간 적용 결과다. 이 구분을 유지해야 학습 내부의 높은 응집도를 미래 구간의 성능으로 잘못 해석하는 일을 피할 수 있다.
'''
p3=p3[:p3.index('\n\n학습 내부 검증 표본은')]
p4=old[3]
p4+='''

**Table 4. Convergence and representation sensitivity**

| 설정 | 반복 수 | 활성 신호 | 미표시 비율 |
| --- | ---: | ---: | ---: |
| NMF-400, 6국면 | 400 | 112 | 43.75% |
| NMF-800, 통합 6국면 | 447 | 111 | 43.24% |
| NMF-800, 7국면 | 447 | 125 | 50.40% |

표 4에서 반복 수는 실제 최적화 종료 시점이다. 기준 모형은 반복 상한에 도달했으므로 수렴이 확인된 모형으로 표현하지 않았다. 동일한 6국면 비교에서 미표시 비율의 차이는 0.51%포인트로 작지만, 이는 토픽별 단어 구성과 개별 월의 활성 판정이 모두 같다는 뜻은 아니다. 특히 가계대출과 부동산의 분리 여부는 지표의 경제적 해석에 영향을 주므로 분류 체계와 수치 변화를 함께 제시하였다.
'''
p5=old[4].split('### 4.4')[0].replace('Table 4.','Table 5.')
p5=p5.replace('하락 조기경보는','### 4.4 하락 경보와 수익률 예측의 구분\n\n하락 조기경보는')
p5+='''

**Table 6. Out-of-sample warning and forecast results**

| 평가 항목 | 표본 | 기준선 | 뉴스 포함 |
| --- | ---: | ---: | ---: |
| 확장창 RMSE | 19개월 | 15.2825 | 13.8687 |
| 고정창 RMSE | 19개월 | 15.6018 | 15.3919 |
| 하락 경보 적중 | 17개월 | 해당 없음 | TP=0, FP=1 |
| 하락 경보 누락 | 17개월 | 해당 없음 | FN=9, TN=7 |

표 6의 RMSE는 NMF-800에서 가계대출 비중을 포함한 보조 예측의 결과이며, 경보 혼동행렬은 기준 국면의 금리·물가 활성 규칙에 대한 결과다. 두 실험은 설명변수, 예측 대상과 평가 가능 월수가 다르므로 동일 모형의 성공·실패 비율로 결합할 수 없다. 기준 NMF-400 산출물에는 KOSPI 뉴스 결합 예측값이 평가 19개월 모두 결측이어서 해당 모형의 RMSE 우위를 주장하지 않았다.

확장창은 과거 관측치를 누적하여 모형을 추정하며, 고정창은 일정 길이의 최근 관측치를 사용한다. 창 선택에 따라 오차 감소 폭이 달라진다는 점은 자료가 짧을 때 예측 결과가 추정 구간의 구성에 민감할 수 있음을 보여 준다. 따라서 이 보조 실험은 뉴스 변수를 추가했을 때의 가능성을 살피는 민감도 분석으로 해석하며, 예측력을 확정하는 근거로 사용하지 않는다.

### 4.5 시장 결과의 해석 범위

동시점 회귀에는 평가 기간의 수익률도 포함된다. 뉴스 어휘와 기저를 학습 기간에 고정한 절차는 특징 추출의 시간적 분리를 보장하지만, 전체 67개월에서 추정한 회귀계수까지 표본 외 예측 계수로 만드는 것은 아니다. 또한 금리·물가와 자본거래의 음의 계수는 보도 내용의 긍정·부정 감성을 직접 측정한 결과가 아니다. 같은 국면에 호재와 악재가 함께 포함될 수 있으며, 시장 하락으로 관련 보도가 늘어나는 역방향 반응도 가능하다.

표준화 국면 점수는 각 분야의 평균 보도 비중을 기준으로 변화의 크기를 측정한다. 이 때문에 회귀계수 비교에는 국면별 학습 분산이 반영된다. 표 5의 보정 유의확률은 여섯 국면 계수의 검정에 대한 것으로, 뒤의 검색 분석에서 사용하는 24개 검정 집합과 구분된다. 통계적 유의성은 효과의 경제적 크기나 투자 전략의 수익성을 대신하지 않으며, 거래비용과 실시간 가용성은 본 분석에서 평가하지 않았다.
'''
search= '### 4.6 검색 관심도의 동시점 변화\n\n'+old[4].split('### 4.4 검색 관심도의 동시점 변화\n\n')[1]
sens=old[5].split('### 4.6 결과의 해석')[0]
p6=search+'\n\n'+sens
p6=p6.replace('### 4.5 검색 결과의 민감도','### 4.7 검색 결과의 민감도').replace('Table 5.','Table 7.').replace('표 5','표 7')
p6=p6.replace('| NMF-400 r | 보정 p | NMF-800 r | 보정 p |','| 400회 r | 보정 p | 800회 r | 보정 p |')
p6+='''

주별 1차 차분은 해당 주의 수준에서 직전 주의 수준을 빼서 정의한다. 이는 뉴스 비중이나 검색 관심도의 장기적인 수준 차이를 줄이고 단기 변화가 함께 발생하는지를 살피기 위한 변환이다. 다만 차분만으로 정상성이나 인과관계가 입증되는 것은 아니다. 시차를 포함한 검정과 보정 후 유의확률을 함께 제시하여 공통 사건에 대한 일시적 반응을 지속적인 선행 관계로 확대 해석하지 않았다.
'''
p6+='''

**Table 8. Sensitivity to HAC lag length and search scaling**

| 비교 조건 | 시황 보정 p | 기업실적 보정 p |
| --- | ---: | ---: |
| HAC 2주 | 0.0339 | 0.0015 |
| HAC 4주 | 0.0432 | 0.0011 |
| HAC 8주 | 0.0616 | 0.0013 |
| 앵커 미사용 | 0.0327 | 0.00016 |
| 앵커 차분 통제 | 0.0713 | 0.0047 |

표 8은 기준 NMF-400에서 검정의 공분산 시차와 검색 지수 구성에 대한 민감도를 요약한다. 앵커 미사용 및 앵커 차분 통제 행은 기본 HAC 4주 설정에 해당한다. 시황의 판정은 5% 경계 부근에서 달라지지만, 기업실적의 보정 유의확률은 제시된 조건에서 모두 0.05 미만이다. 이 비교는 유의한 설정만 선택하기 위한 절차가 아니라, 결론이 어떤 분석 조건에 의존하는지 드러내기 위한 것이다.

동일한 상관계수라도 불확실성의 계산 방식에 따라 판정은 달라질 수 있다. 이동 블록 부트스트랩은 인접한 주의 관측을 묶어 재추출하여 시계열 의존 구조를 일부 보존한다. 그림 2의 구간이 0을 포함하지 않는다는 사실과 Holm 보정 검정이 유의하다는 판정은 동일한 통계량이 아니므로 구분하였다. 여러 이슈와 시차를 함께 검정한 결과에서는 보정 전 유의확률만으로 특정 관계를 확정하지 않는다.
'''
p6=p6[:p6.index('\n\n동일한 상관계수라도')]
p6+='\n\n이동 블록 부트스트랩은 인접한 주의 관측을 묶어 재추출하여 시계열 의존 구조를 일부 보존한다. 개별 상관계수의 신뢰구간과 여러 가설에 대한 Holm 보정 유의확률은 서로 다른 불확실성 평가이므로 각각 해석하였다.\n'
p7='''## Ⅴ. 논의 및 연구의 한계

### 5.1 지표의 의미와 활용 범위

'''+old[5].split('### 4.6 결과의 해석\n\n')[1]
p7+='\n\n### 5.2 의미 타당성과 자료의 대표성\n\n'+old[6].split('### 4.7 적용상의 한계\n\n')[1].split('## Ⅴ. 결론')[0]
p7+='''

뉴스 비중은 경제 활동의 실제 규모가 아니라 선택된 매체의 보도 구성이다. 본 연구의 경제 일간지 세 곳은 전문적인 경제 보도를 제공하지만 지역 매체, 방송 및 일반 종합지의 관심 구성을 모두 대표하지 않는다. 매체별 기사 발행량 차이가 문서 평균에 반영되므로, 후속 분석에서는 동일 매체 가중 집계와 매체를 하나씩 제외한 결과를 함께 비교할 필요가 있다. 이는 현재 결과를 확장하기 위한 검증 과제이며 본 원고의 실험 결과에는 포함하지 않았다.

### 5.3 표본 외 적용과 재현성

학습 자료에만 적합한 어휘, IDF, 토픽 기저 및 표준화 모수는 평가 구간의 새로운 보도에 동일하게 적용된다. 이 설계는 평가 기간의 단어 빈도를 특징 추출에 소급 반영하지 않도록 한다. 반면 학습 사전에 없는 신조어와 새로운 산업 이슈는 기존 어휘로 충분히 표현되지 않을 수 있다. 따라서 고정 기저의 안정성과 이후 시기의 표현 손실을 함께 고려해야 하며, 일정 주기로 기저를 재학습하는 체계는 별도의 시간 순서 검증이 필요하다.

재현을 위해서는 원자료와 전처리된 기사 집합, 적합·내부 검증 표본의 식별자, 토픽 기저, 국면 매핑 및 시간 집계 규칙을 연결해 보관해야 한다. 특히 월별 패널과 ISO 주별 패널은 관측 단위가 다르다. 평가 첫 주의 차분에 직전 학습 주를 포함하는지에 따라 유효 주수가 달라지므로, 82주 기준과 83주 민감도 결과를 구분하여 보고하였다. 검색 지수의 고정 조회 기간과 앵커 처리 방식도 함께 기록해야 결과를 대조할 수 있다.

### 5.4 후속 검증 설계

독립적인 기사 평가에서는 평가자가 모형의 국면 점수를 보지 않은 상태에서 하나 이상의 경제 이슈를 선택하도록 해야 한다. 국면별 기사와 경합·잔차 기사를 포함해 표본을 구성하고, 평가자 간 일치도와 모델의 다중 라벨 적합성을 구분하여 보고할 필요가 있다. 월별 주요 사건 목록을 별도로 작성하면 추가 표시가 실제 주요 이슈를 회수하는지, 부수적 이슈를 과도하게 표시하는지도 비교할 수 있다.

이때 단일 방식과 다중 방식에 같은 기사, 같은 평가 월, 같은 사건 기준을 적용해야 한다. 임계값 조정으로 표시 수가 늘면 회수율과 과잉 표시율이 함께 변할 수 있으므로 두 지표를 병행 평가하는 것이 적절하다. 외부 평가에서는 최근 기간을 순차적으로 추가하면서 특징 추출과 검정 조건을 사전에 고정하여, 모형 선택에 사용하지 않은 구간에서도 결과가 재현되는지 확인해야 한다.
'''
p8='## Ⅵ. 결론\n\n'+old[6].split('## Ⅴ. 결론\n\n')[1].split('### 후속 검증')[0]+'\n\n'+old[7]
# Keep the conclusion compact enough to share its page with the references.
paras=p8.split('## REFERENCES')[0].split('\n\n')
p8='\n\n'.join(paras[:3])+'\n\n'+'''기업실적 뉴스와 검색 관심도의 주별 동행성은 NMF 설정 변경에도 유지되었으나, 시황의 유의성은 일부 추정 조건에 민감하였다. 시장 회귀는 동시점 관계를 나타내며 하락 조기경보의 적중은 확인되지 않았다. 이 연구는 여러 이슈를 함께 표시하는 요약의 표현 차이를 정량화하였고, 실제 활용도를 확정하려면 독립 기사 라벨과 더 긴 평가 기간이 필요하다.\n\n'''+old[7]
p8=p8.replace('## REFERENCES','''학습 기간 고정 방식은 뉴스 특징의 정의를 평가 기간에도 유지하여 표시 규칙 간 차이를 같은 척도에서 비교하게 한다. 다만 잔차·경합 비중이 크다는 점에서 여섯 국면은 전체 경제 뉴스의 모든 주제를 포괄하지 않는다. 또한 기사 비중은 보도 관심의 구성이지 경제 현상의 규모나 방향 자체가 아니다. 이에 따라 본 연구의 국면 시계열은 월별 보도 구성을 살펴보고 추가 검토할 이슈를 찾는 보조 지표로 해석하는 것이 적절하다.

## REFERENCES''')
p8+='\n[13] Y. Kim and J. K. Hwangbo, “The Trend Analysis of Drug-Related News Articles with Topic Modeling,” *Journal of the Korea Institute of Information and Communication Engineering*, vol. 28, no. 3, pp. 356-359, Mar. 2024. DOI: 10.6109/jkiice.2024.28.3.356.\n'
p8=p8.replace('## REFERENCES','''향후에는 모형 출력을 가린 독립 평가자의 복수 이슈 라벨과 월별 사건 목록을 구축하여 의미 타당성을 평가할 필요가 있다. 같은 평가 기준에서 단일·다중 표시의 주요 이슈 회수율과 과잉 표시율을 비교하고, 언론사 구성 및 학습 창을 바꾸었을 때의 안정성을 검토해야 한다. 이 절차가 추가되어야 표시 수의 증가가 독자에게 유용한 정보의 증가로 이어지는지 판단할 수 있다.

## REFERENCES''')
pages=[p1,p2,p3,p4,p5,p6,p7,p8]
text='\n\n<!-- page -->\n\n'.join(pages)
# Use ASCII minus where necessary so mathematical subtraction is unambiguous.
text=text.replace('−','-').replace('–','-').replace('—','-')
(OUT/'JKIICE_경제뉴스_8페이지_원고.md').write_text(text,encoding='utf-8')
pages=text.split('<!-- page -->')

pdfmetrics.registerFont(TTFont('Batang','C:/Windows/Fonts/HANBatang.ttf'))
pdfmetrics.registerFont(TTFont('Gothic','C:/Windows/Fonts/malgun.ttf'))
pdfmetrics.registerFont(TTFont('GothicB','C:/Windows/Fonts/malgunbd.ttf'))
pdfmetrics.registerFont(TTFont('TimesR','C:/Windows/Fonts/times.ttf'))
pdfmetrics.registerFont(TTFont('TimesB','C:/Windows/Fonts/timesbd.ttf'))
pdfmetrics.registerFontFamily('Batang',normal='Batang',bold='GothicB',italic='Batang',boldItalic='GothicB')
pdfmetrics.registerFontFamily('TimesR',normal='TimesR',bold='TimesB',italic='TimesR',boldItalic='TimesB')
W,H=595.276,841.89
LEFT=72; GAP=18; CW=(W-2*LEFT-GAP)/2
TOP=744; BOTTOM=77; HEIGHT=TOP-BOTTOM

def inline(s):
    s=escape(s)
    s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'\*(.*?)\*',r'<i>\1</i>',s)
    return s

def flows(md,leading=13.8,cover=False):
    md=re.sub(r'(?m)^(#{1,3} .+)$',r'\1\n',md)
    body=ParagraphStyle('body',fontName='Batang',fontSize=9.2,leading=leading,alignment=TA_JUSTIFY,wordWrap='CJK',firstLineIndent=9.2,spaceAfter=2)
    eng=ParagraphStyle('en',parent=body,fontName='TimesR',wordWrap=None,firstLineIndent=0)
    head=ParagraphStyle('head',parent=body,fontName='GothicB',fontSize=11,leading=16,firstLineIndent=0,spaceBefore=9,spaceAfter=9,keepWithNext=True)
    sub=ParagraphStyle('sub',parent=head,fontSize=9.5,leading=14,spaceBefore=7,spaceAfter=4)
    cap=ParagraphStyle('cap',parent=eng,fontName='TimesB',fontSize=8,leading=10.4,spaceAfter=4,keepWithNext=True)
    ref=ParagraphStyle('ref',parent=eng,fontSize=8.5,leading=12,spaceAfter=4,leftIndent=12,firstLineIndent=-12,alignment=TA_LEFT)
    cell=ParagraphStyle('cell',parent=body,fontName='Gothic',fontSize=7.4,leading=10,firstLineIndent=0,spaceAfter=0,alignment=TA_LEFT)
    width=W-2*LEFT if cover else CW
    chunks=re.split(r'\n\s*\n',md.strip()); result=[]
    in_abstract=False
    for chunk in chunks:
        chunk=chunk.strip()
        if not chunk:continue
        if chunk.startswith('|'):
            rows=[[x.strip() for x in row.strip().strip('|').split('|')] for row in chunk.splitlines()]
            rows=[r for r in rows if not all(re.match(r'^[-: ]+$',x) for x in r)]
            n=len(rows[0]); ratios={3:[.46,.27,.27],4:[.30,.26,.14,.30],5:[.22,.16,.20,.18,.24]}.get(n,[1/n]*n)
            if '반복 수' in rows[0]:ratios=[.43,.16,.18,.23]
            if '평가 항목' in rows[0]:ratios=[.34,.16,.25,.25]
            if '월 범위' in rows[0]:ratios=[.14,.45,.13,.28]
            if '추가 활성 국면' in rows[0]:ratios=[.24,.28,.48]
            if '400회 r' in rows[0]:ratios=[.32,.17,.16,.18,.17]
            data=[[Paragraph(inline(x),cell) for x in row] for row in rows]
            t=Table(data,colWidths=[width*x for x in ratios],hAlign='LEFT')
            t.setStyle(TableStyle([('LINEABOVE',(0,0),(-1,0),.7,colors.black),('LINEBELOW',(0,0),(-1,0),.45,colors.black),('LINEBELOW',(0,-1),(-1,-1),.7,colors.black),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            t.spaceAfter=8;result.append(t)
        elif chunk.startswith('!['):
            m=re.match(r'!\[(.*?)\]\((.*?)\)',chunk)
            im=Image(str(ROOT/'docs'/m[2])); im.drawHeight*=width/im.drawWidth;im.drawWidth=width;im.spaceAfter=4
            result.extend([im,Paragraph(inline(m[1]),cap)])
        elif chunk.startswith('# '):
            sty=ParagraphStyle('title',parent=head,fontSize=17,leading=23,spaceBefore=0,spaceAfter=17)
            result.append(Paragraph(inline(chunk[2:]),sty))
        elif chunk.startswith('### Detecting'):
            sty=ParagraphStyle('titleen',parent=eng,fontSize=12.5,leading=16,spaceAfter=28)
            result.append(Paragraph(inline(chunk[4:]),sty))
        elif chunk.startswith('## '):
            in_abstract=chunk=='## ABSTRACT'
            result.append(Paragraph(inline(chunk[3:]),head))
        elif chunk.startswith('### '):result.append(Paragraph(inline(chunk[4:]),sub))
        elif chunk.startswith('**Table'):result.append(Paragraph(inline(chunk.strip('*')),cap))
        elif chunk.startswith('> '):
            sty=ParagraphStyle('eq',parent=body,alignment=1,firstLineIndent=0,spaceBefore=6,spaceAfter=8,fontName='Gothic',fontSize=8.4)
            result.append(Paragraph(inline(chunk[2:]),sty))
        elif re.match(r'^\[\d+\]',chunk):
            for line in chunk.splitlines():result.append(Paragraph(inline(line),ref))
        elif chunk.startswith('**키워드') or chunk.startswith('**Keywords'):
            result.append(Paragraph(inline(chunk),ParagraphStyle('key',parent=body,fontSize=8.5,firstLineIndent=0,spaceBefore=8,spaceAfter=8)))
        else:result.append(Paragraph(inline(chunk.replace('\n',' ')),eng if in_abstract else body))
    return result

def layout(items,width,height):
    remaining=copy.deepcopy(items); placed=[];y=height
    while remaining:
        f=remaining.pop(0); before=f.getSpaceBefore() if placed else 0
        w,h=f.wrap(width,y-before)
        after=f.getSpaceAfter()
        if f.getKeepWithNext() and remaining:
            _,nh=remaining[0].wrap(width,10000)
            if h+before+min(nh,28)+after>y:remaining.insert(0,f);break
        if h+before<=y+0.01:
            y-=before+h;placed.append((f,y));y-=after
        else:
            if isinstance(f,Paragraph):
                spl=f.split(width,max(0,y-before))
                if len(spl)>1:
                    _,sh=spl[0].wrap(width,y-before);y-=before+sh;placed.append((spl[0],y));remaining=spl[1:]+remaining
                else:remaining.insert(0,f)
            else:remaining.insert(0,f)
            break
    if remaining:
        while placed and placed[-1][0].getKeepWithNext():
            f,old_y=placed.pop();remaining.insert(0,f)
        y=placed[-1][1]-placed[-1][0].getSpaceAfter() if placed else height
    return placed,remaining,height-y

def two_columns(items,height):
    left,rest,hl=layout(items,CW,height)
    right,rest,hr=layout(rest,CW,height)
    return left,right,rest,hl,hr

def render():
    dest=OUT/'JKIICE_경제뉴스_8페이지_편집본.pdf'
    c=canvas.Canvas(str(dest),pagesize=(W,H))
    c.setTitle('한국 경제 뉴스의 다중 이슈 국면 탐지와 시장·검색 지표의 동행성 분석')
    metrics=[]
    for i,md in enumerate(pages):
        c.setFillColor(colors.black)
        if i==0:
            c.setFont('GothicB',21);c.drawString(LEFT,786,'JKIICE')
            c.setFont('TimesR',8.5);c.drawString(LEFT+91,795,'Journal of the Korea Institute of Information and')
            c.drawString(LEFT+91,783,'Communication Engineering')
            fs=flows(md,14.8,True)
            placed,rest,used=layout(fs,W-2*LEFT,HEIGHT)
            if rest:raise ValueError(('cover overflow',len(rest),used))
            for f,y in placed:f.drawOn(c,LEFT,TOP-HEIGHT+y)
            metrics.append({'page':1,'used':used,'height':HEIGHT})
        else:
            c.setFont('Gothic',7);c.drawString(LEFT,771,'한국 경제 뉴스의 다중 이슈 국면 탐지와 시장·검색 지표의 동행성 분석')
            chosen=None
            for leading in [13.8,13.6,13.4,13.2,13.0]:
                fs=flows(md,leading)
                a,b,rest,ha,hb=two_columns(fs,HEIGHT)
                if not rest:chosen=(fs,leading);break
            if not chosen:
                print('OVERFLOW',i+1,len(rest),ha,hb)
                raise ValueError('page overflow')
            # Balance columns to within one line without arbitrary internal white gaps.
            lo,hi=100,HEIGHT
            for _ in range(16):
                mid=(lo+hi)/2
                a,b,rest,ha,hb=two_columns(fs,mid)
                if rest:lo=mid
                else:hi=mid
            useheight=hi+.05
            a,b,rest,ha,hb=two_columns(fs,useheight)
            for x,items in [(LEFT,a),(LEFT+CW+GAP,b)]:
                for f,y in items:f.drawOn(c,x,TOP-useheight+y)
            metrics.append({'page':i+1,'leading':leading,'left':ha,'right':hb,'fill':round(max(ha,hb)/HEIGHT,3)})
        c.setFont('TimesR',9);c.drawCentredString(W/2,53,str(i+1));c.showPage()
    c.save()
    (OUT/'layout_metrics.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    print(json.dumps(metrics,indent=2));print('ABSTRACT_WORDS',len(abstract.split()))

if __name__=='__main__':render()
