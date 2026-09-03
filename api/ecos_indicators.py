"""반응 분석에 쓸 ECOS 지표 정의.

통계표·항목 코드는 ECOS StatisticTableList / StatisticItemList로 확인한 값이다
(`python -m api.collect_ecos --list-items 511Y002` 로 재확인 가능).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Indicator:
    name: str
    stat_code: str
    item_codes: list[str]
    cycle: str = "M"
    desc: str = ""
    # 시점 축이 여러 개인 통계표는 항목명으로 한 계열만 남긴다.
    expect_item_name: str = ""
    extra: dict[str, str] = field(default_factory=dict)


INDICATORS: list[Indicator] = [
    Indicator(
        name="CCSI",
        stat_code="511Y002",
        item_codes=["FME", "99988"],
        desc="소비자심리지수 (소비자동향조사, 전국·전체)",
        expect_item_name="소비자심리지수",
    ),
    Indicator(
        name="KOSPI",
        stat_code="901Y014",
        item_codes=["1070000"],
        desc="KOSPI 월말 종가 (1980.01.04=100)",
        expect_item_name="KOSPI_종가",
    ),
    Indicator(
        name="USD_KRW",
        stat_code="731Y004",
        item_codes=["0000001", "0000200"],
        desc="원/미국달러 매매기준율 월말 (KOSPI 월말종가와 시점 축을 맞춤)",
        expect_item_name="원/미국달러(매매기준율)",
    ),
    Indicator(
        name="BASE_RATE",
        stat_code="722Y001",
        item_codes=["0101000"],
        desc="한국은행 기준금리 (월, 연%)",
        expect_item_name="한국은행 기준금리",
    ),
    Indicator(
        name="CPI",
        stat_code="901Y009",
        item_codes=["0"],
        desc="소비자물가지수 총지수 (2020=100)",
        expect_item_name="총지수",
    ),
]

BY_NAME = {ind.name: ind for ind in INDICATORS}
