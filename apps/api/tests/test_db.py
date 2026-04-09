from __future__ import annotations

from collections.abc import AsyncIterator
from inspect import isasyncgenfunction

from polymap_api.db import (
    Base,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
    async_session_factory,
    convention,
    engine,
    get_session,
)


def test_db_exports_are_importable() -> None:
    assert Base is not None
    assert engine is not None
    assert async_session_factory is not None
    assert isasyncgenfunction(get_session)


def test_naming_convention_is_set() -> None:
    assert convention == {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    assert Base.metadata.naming_convention == convention


def test_mixin_columns_exist() -> None:
    assert "id" in UUIDPrimaryKeyMixin.__dict__
    assert "created_at" in TimestampMixin.__dict__
    assert "updated_at" in TimestampMixin.__dict__
    assert "deleted_at" in SoftDeleteMixin.__dict__


def test_get_session_return_annotation() -> None:
    assert get_session.__annotations__["return"] == AsyncIterator[object] or "AsyncIterator" in str(
        get_session.__annotations__["return"]
    )
