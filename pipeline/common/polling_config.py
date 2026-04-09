from __future__ import annotations

from dataclasses import dataclass

from polymap_ontology.enums import ElectionPhase


@dataclass(frozen=True)
class PollingTier:
    phase: ElectionPhase
    interval_seconds: int
    sources: list[str]


POLLING_TIERS = [
    PollingTier(ElectionPhase.PRE_CANDIDACY, 86400, ["nec", "assembly"]),
    PollingTier(ElectionPhase.CANDIDACY_REGISTRATION, 3600, ["nec"]),
    PollingTier(ElectionPhase.CAMPAIGN, 3600, ["nec", "assembly", "local_council"]),
    PollingTier(ElectionPhase.POLLING_BAN, 86400, ["nec"]),
    PollingTier(ElectionPhase.ELECTION_DAY, 300, ["nec"]),
    PollingTier(ElectionPhase.POST_ELECTION, 86400, ["nec"]),
]


def polling_tier_for_phase(phase: ElectionPhase) -> PollingTier:
    for tier in POLLING_TIERS:
        if tier.phase is phase:
            return tier
    msg = f"unsupported election phase: {phase}"
    raise ValueError(msg)
