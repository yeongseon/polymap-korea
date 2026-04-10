from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

import httpx

from polymap_api.config import settings
from polymap_api.models import District

logger = logging.getLogger(__name__)

_JUSO_API_URL = "https://business.juso.go.kr/addrlink/addrLinkApi.do"


class AddressResolver(Protocol):
    async def resolve(self, address_text: str, districts: Sequence[District]) -> District | None: ...


def _district_lineage(district: District, districts_by_id: Mapping[UUID, District]) -> list[District]:
    lineage = [district]
    current = district
    while current.parent_id is not None:
        current = districts_by_id[current.parent_id]
        lineage.append(current)
    return lineage


def _pick_best_district(address_text: str, districts: Sequence[District]) -> District | None:
    district_list = list(districts)
    districts_by_id = {district.id: district for district in district_list}
    matched_districts = [district for district in district_list if district.name_ko in address_text]
    if not matched_districts:
        return None

    def rank(district: District) -> tuple[int, int, int]:
        lineage = _district_lineage(district, districts_by_id)
        matching_ancestors = sum(1 for ancestor in lineage[1:] if ancestor.name_ko in address_text)
        return (matching_ancestors, len(lineage), len(district.name_ko))

    return max(matched_districts, key=rank)


@dataclass(slots=True)
class JusoAddressCandidate:
    road_address: str
    jibun_address: str
    region_tokens: tuple[str, ...]

    def combined_search_text(self) -> str:
        return " ".join(
            token
            for token in (
                self.jibun_address,
                *self.region_tokens,
                self.road_address,
            )
            if token
        )

    def search_texts(self) -> Iterable[str]:
        seen: set[str] = set()
        for value in (
            self.combined_search_text(),
            self.jibun_address,
            " ".join(token for token in self.region_tokens if token),
            self.road_address,
            " ".join(token for token in (self.road_address, *self.region_tokens) if token),
            " ".join(token for token in (self.jibun_address, *self.region_tokens) if token),
        ):
            normalized = value.strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                yield normalized


class JusoApiResolver:
    def __init__(
        self,
        api_key: str,
        client: httpx.AsyncClient | None = None,
        base_url: str = _JUSO_API_URL,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self._client = client
        self._owns_client = client is None

    async def aclose(self) -> None:
        if self._client is not None and self._owns_client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client

    async def resolve(self, address_text: str, districts: Sequence[District]) -> District | None:
        try:
            candidates = await self._fetch_candidates(address_text)
        except (httpx.HTTPError, httpx.TimeoutException, ValueError) as exc:
            logger.warning("Juso address lookup failed: %s", exc)
            return None

        for candidate in candidates:
            for search_text in candidate.search_texts():
                matched = _pick_best_district(search_text, districts)
                if matched is not None:
                    return matched
        return None

    async def _fetch_candidates(self, address_text: str) -> list[JusoAddressCandidate]:
        response = await self.client.get(
            self.base_url,
            params={
                "confmKey": self.api_key,
                "keyword": address_text,
                "currentPage": 1,
                "countPerPage": 10,
                "resultType": "json",
            },
        )
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results")
        if not isinstance(results, dict):
            raise ValueError("Unexpected Juso API response")

        common = results.get("common", {})
        if isinstance(common, dict):
            error_code = common.get("errorCode")
            if error_code not in (None, "0", 0):
                error_message = common.get("errorMessage", "unknown error")
                raise ValueError(f"Juso API error {error_code}: {error_message}")

        juso_items = results.get("juso", [])
        if not isinstance(juso_items, list):
            raise ValueError("Unexpected Juso API response")

        candidates: list[JusoAddressCandidate] = []
        for item in juso_items:
            if not isinstance(item, dict):
                continue
            candidates.append(
                JusoAddressCandidate(
                    road_address=str(item.get("roadAddrPart1", "") or ""),
                    jibun_address=str(item.get("jibunAddr", "") or ""),
                    region_tokens=tuple(
                        str(item.get(key, "") or "")
                        for key in ("siNm", "sggNm", "emdNm", "liNm")
                    ),
                )
            )
        return candidates


class FallbackResolver:
    async def resolve(self, address_text: str, districts: Sequence[District]) -> District | None:
        return _pick_best_district(address_text, districts)


class ChainResolver:
    def __init__(self, resolvers: Sequence[AddressResolver]) -> None:
        self.resolvers = tuple(resolvers)

    async def resolve(self, address_text: str, districts: Sequence[District]) -> District | None:
        for resolver in self.resolvers:
            district = await resolver.resolve(address_text, districts)
            if district is not None:
                return district
        return None


def build_address_resolver() -> ChainResolver:
    resolvers: list[AddressResolver] = []
    if settings.juso_api_key:
        resolvers.append(JusoApiResolver(api_key=settings.juso_api_key))
    resolvers.append(FallbackResolver())
    return ChainResolver(resolvers)
