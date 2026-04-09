from __future__ import annotations

from polymap_ontology.enums import ElectionPhase

from common.polling_config import polling_tier_for_phase


def test_all_election_phases_have_polling_tiers() -> None:
    resolved = {phase: polling_tier_for_phase(phase) for phase in ElectionPhase}

    assert resolved[ElectionPhase.POLLING_BAN].interval_seconds == 86400
    assert resolved[ElectionPhase.POLLING_BAN].sources == ["nec"]
