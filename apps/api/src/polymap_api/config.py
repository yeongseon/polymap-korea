from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    app_version: str = "0.1.0"
    debug: bool = False
    database_url: str = "postgresql+asyncpg://polymap:polymap_dev@localhost:5432/polymap"
    redis_url: str = "redis://localhost:6379/0"
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
