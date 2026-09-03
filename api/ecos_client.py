"""한국은행 ECOS Open API 클라이언트.

  GET https://ecos.bok.or.kr/api/StatisticSearch/{KEY}/json/kr/{start}/{end}
      /{통계표코드}/{주기}/{시작시점}/{종료시점}/{항목코드1}[/{항목코드2}...]

주기(cycle)별 시점 표기가 다르다: 연 `YYYY`, 분기 `YYYYQn`, 월 `YYYYMM`, 일 `YYYYMMDD`.
"""

from __future__ import annotations

import os
import time
from typing import Any

import requests
from dotenv import load_dotenv

BASE_URL = "https://ecos.bok.or.kr/api"
PAGE_SIZE = 1000
# 조회 결과가 없을 때 ECOS가 돌려주는 코드. 오류가 아니라 빈 결과로 다룬다.
NO_DATA_CODES = {"INFO-200"}


class EcosError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class EcosClient:
    def __init__(self, api_key: str | None = None):
        load_dotenv()
        self.api_key = (api_key or os.getenv("ECOS_API_KEY") or "").strip()
        if not self.api_key or self.api_key.startswith("your_"):
            raise RuntimeError(".env에 ECOS_API_KEY를 넣으세요.")
        self.session = requests.Session()

    def _get(self, path: str, *, retries: int = 3) -> dict[str, Any]:
        url = f"{BASE_URL}/{path}"
        last: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                resp = self.session.get(url, timeout=60)
                resp.raise_for_status()
                return resp.json()
            except (requests.RequestException, ValueError) as e:
                last = e
                if attempt < retries:
                    time.sleep(1.5 * attempt)
        assert last is not None
        raise last

    def _rows(self, service: str, path: str) -> list[dict[str, Any]]:
        """페이지네이션하며 service의 row 목록을 모두 모은다."""
        rows: list[dict[str, Any]] = []
        start = 1
        while True:
            payload = self._get(f"{service}/{self.api_key}/json/kr/{start}/{start + PAGE_SIZE - 1}/{path}")
            if "RESULT" in payload:
                result = payload["RESULT"]
                code = result.get("CODE", "")
                if code in NO_DATA_CODES:
                    return rows
                raise EcosError(code, result.get("MESSAGE", ""))
            body = payload.get(service) or {}
            batch = body.get("row") or []
            rows.extend(batch)
            total = int(body.get("list_total_count") or 0)
            if len(rows) >= total or not batch:
                return rows
            start += PAGE_SIZE

    def statistic_search(
        self,
        stat_code: str,
        *,
        cycle: str,
        start: str,
        end: str,
        item_codes: list[str],
    ) -> list[dict[str, Any]]:
        if not item_codes:
            raise ValueError("item_codes는 1개 이상이어야 합니다.")
        if len(item_codes) > 4:
            raise ValueError("ECOS는 항목코드를 최대 4개까지 받습니다.")
        path = "/".join([stat_code, cycle, start, end, *item_codes])
        return self._rows("StatisticSearch", path)

    def item_list(self, stat_code: str) -> list[dict[str, Any]]:
        """통계표의 항목코드 목록. 새 지표를 추가할 때 코드를 찾는 용도."""
        return self._rows("StatisticItemList", stat_code)

    def table_list(self) -> list[dict[str, Any]]:
        """전체 통계표 목록."""
        return self._rows("StatisticTableList", "")
