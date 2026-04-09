from __future__ import annotations

from enum import Enum


class _StrEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class Gender(_StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ElectionType(_StrEnum):
    LOCAL_GENERAL = "local_general"
    LOCAL_BYELECTION = "local_byelection"


class CandidacyStatus(_StrEnum):
    REGISTERED = "registered"
    WITHDRAWN = "withdrawn"
    DISQUALIFIED = "disqualified"
    ELECTED = "elected"
    DEFEATED = "defeated"


class PositionType(_StrEnum):
    MAYOR = "mayor"
    GOVERNOR = "governor"
    COUNCIL_MEMBER = "council_member"
    SUPERINTENDENT = "superintendent"
    PROPORTIONAL_COUNCIL = "proportional_council"


class SourceDocKind(_StrEnum):
    OFFICIAL_GAZETTE = "official_gazette"
    NEWS_ARTICLE = "news_article"
    PDF = "pdf"
    WEB_PAGE = "web_page"
    API_RESPONSE = "api_response"


class IssueRelationType(_StrEnum):
    BROADER = "broader"
    NARROWER = "narrower"
    RELATED = "related"


class ClaimType(_StrEnum):
    OFFICIAL_FACT = "official_fact"
    SOURCED_CLAIM = "sourced_claim"
    OPINION = "opinion"
    DISPUTED = "disputed"
    AI_SUMMARY = "ai_summary"


class BillStatus(_StrEnum):
    PROPOSED = "proposed"
    COMMITTEE_REVIEW = "committee_review"
    PLENARY = "plenary"
    PASSED = "passed"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ElectionPhase(_StrEnum):
    PRE_CANDIDACY = "pre_candidacy"
    CANDIDACY_REGISTRATION = "candidacy_registration"
    CAMPAIGN = "campaign"
    POLLING_BAN = "polling_ban"
    ELECTION_DAY = "election_day"
    POST_ELECTION = "post_election"
