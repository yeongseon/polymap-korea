from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PersonName(BaseModel):
    """Normalized bilingual person naming fields for future shared schema reuse."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name_ko: str = Field(min_length=1, max_length=200)
    name_en: str | None = Field(default=None, max_length=200)


class DateRange(BaseModel):
    """Immutable date interval used by ontology constraints and downstream validators."""

    model_config = ConfigDict(frozen=True)

    start_date: date
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_bounds(self) -> DateRange:
        if self.end_date is not None and self.start_date > self.end_date:
            msg = "start_date must be less than or equal to end_date"
            raise ValueError(msg)
        return self
