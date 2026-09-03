"""네이버 검색(뉴스) · 검색어 트렌드(데이터랩) 클라이언트.

- 뉴스: 개발자센터 OpenAPI (기존 키) 또는 NAVER API HUB
- 데이터랩(Search Trend): NAVER API HUB 전용
  POST https://naverapihub.apigw.ntruss.com/search-trend/v1/search
"""

from __future__ import annotations

import os
import time
from typing import Any

import requests
from dotenv import load_dotenv

NEWS_URL_LEGACY = "https://openapi.naver.com/v1/search/news.json"
NEWS_URL_HUB = "https://naverapihub.apigw.ntruss.com/search/v1/news"
DATALAB_URL_HUB = "https://naverapihub.apigw.ntruss.com/search-trend/v1/search"

NEWS_DISPLAY_MAX = 100
NEWS_START_MAX = 1000


def _env(*names: str) -> str:
    for name in names:
        val = (os.getenv(name) or "").strip()
        if val:
            return val
    return ""


class NaverClient:
    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        hub_client_id: str | None = None,
        hub_client_secret: str | None = None,
    ):
        load_dotenv()
        # 개발자센터 키 (뉴스 파일럿용, 선택)
        self.legacy_id = client_id or _env("NAVER_CLIENT_ID")
        self.legacy_secret = client_secret or _env("NAVER_CLIENT_SECRET")
        # NAVER API HUB 키 (검색어 트렌드 필수). 없으면 CLIENT_* 재사용
        self.hub_id = hub_client_id or _env(
            "NAVER_HUB_CLIENT_ID", "NCP_APIGW_API_KEY_ID", "NAVER_CLIENT_ID"
        )
        self.hub_secret = hub_client_secret or _env(
            "NAVER_HUB_CLIENT_SECRET", "NCP_APIGW_API_KEY", "NAVER_CLIENT_SECRET"
        )
        if not self.hub_id or not self.hub_secret:
            raise RuntimeError(
                "NAVER API HUB 키가 필요합니다. "
                ".env에 NAVER_HUB_CLIENT_ID / NAVER_HUB_CLIENT_SECRET "
                "(또는 NAVER_CLIENT_ID / NAVER_CLIENT_SECRET)을 넣으세요."
            )
        self.session = requests.Session()

    def _hub_headers(self) -> dict[str, str]:
        return {
            "X-NCP-APIGW-API-KEY-ID": self.hub_id,
            "X-NCP-APIGW-API-KEY": self.hub_secret,
            "Content-Type": "application/json",
        }

    def _legacy_headers(self) -> dict[str, str]:
        return {
            "X-Naver-Client-Id": self.legacy_id,
            "X-Naver-Client-Secret": self.legacy_secret,
        }

    def search_news(
        self,
        query: str,
        *,
        display: int = 100,
        start: int = 1,
        sort: str = "date",
    ) -> dict[str, Any]:
        display = max(1, min(int(display), NEWS_DISPLAY_MAX))
        start = max(1, min(int(start), NEWS_START_MAX))
        if start + display - 1 > NEWS_START_MAX:
            display = NEWS_START_MAX - start + 1
        params = {"query": query, "display": display, "start": start, "sort": sort}

        # 1) 개발자센터 키가 있으면 레거시 뉴스 API
        if self.legacy_id and self.legacy_secret:
            resp = self.session.get(
                NEWS_URL_LEGACY, params=params, headers=self._legacy_headers(), timeout=30
            )
            if resp.status_code != 401:
                resp.raise_for_status()
                return resp.json()

        # 2) HUB 뉴스
        resp = self.session.get(
            NEWS_URL_HUB,
            params=params,
            headers={
                "X-NCP-APIGW-API-KEY-ID": self.hub_id,
                "X-NCP-APIGW-API-KEY": self.hub_secret,
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def fetch_news_max(
        self,
        query: str,
        *,
        sort: str = "date",
        sleep_sec: float = 0.05,
    ) -> list[dict[str, Any]]:
        """한 쿼리에서 API가 허용하는 최대(최대 1000건)까지 페이지네이션."""
        items: list[dict[str, Any]] = []
        start = 1
        while start <= NEWS_START_MAX:
            data = self.search_news(query, display=NEWS_DISPLAY_MAX, start=start, sort=sort)
            batch = data.get("items") or []
            if not batch:
                break
            items.extend(batch)
            total = int(data.get("total") or 0)
            if start + len(batch) - 1 >= min(total, NEWS_START_MAX) or len(batch) < NEWS_DISPLAY_MAX:
                break
            start += NEWS_DISPLAY_MAX
            if sleep_sec:
                time.sleep(sleep_sec)
        return items

    def datalab_search(
        self,
        *,
        start_date: str,
        end_date: str,
        time_unit: str,
        keyword_groups: list[dict[str, Any]],
        device: str | None = None,
        gender: str | None = None,
        ages: list[str] | None = None,
    ) -> dict[str, Any]:
        if not keyword_groups or len(keyword_groups) > 5:
            raise ValueError("keywordGroups는 1~5개여야 합니다.")
        body: dict[str, Any] = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "keywordGroups": keyword_groups,
        }
        if device:
            body["device"] = device
        if gender:
            body["gender"] = gender
        if ages:
            body["ages"] = ages
        resp = self.session.post(
            DATALAB_URL_HUB,
            json=body,
            headers=self._hub_headers(),
            timeout=60,
        )
        if not resp.ok:
            raise requests.HTTPError(
                f"{resp.status_code} {resp.reason}: {resp.text[:500]}",
                response=resp,
            )
        return resp.json()
