from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
AI_DISCLAIMER_KO = "이 요약은 중앙선거관리위원회 등 원문 자료를 바탕으로 인공지능이 생성한 참고용 요약입니다. 원문과 차이가 있을 수 있으므로 출처 문서를 함께 확인하세요."


class Settings(BaseSettings):
    app_version: str = "0.1.0"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://polymap:polymap_dev@localhost:5432/polymap"
    opensearch_url: str = "http://localhost:9200"
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "polymap"
    s3_secret_key: str = "polymap_dev"
    s3_bucket_raw: str = "polymap-raw"
    nec_api_key: str = ""
    assembly_api_key: str = ""
    prefect_api_url: str = "http://localhost:4200/api"

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="POLYMAP_",
        env_file=str(_PROJECT_ROOT / ".env"),
    )


settings = Settings()
