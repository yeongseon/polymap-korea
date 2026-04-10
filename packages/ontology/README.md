# PolyMap Korea Ontology

This package will hold RDF, SHACL, and JSON-LD definitions used to model election entities, provenance, and validation rules.

Issue #1 keeps the package in place and documents its purpose for follow-up ontology work.

## Current usage boundary

- Runtime integration today is strongest around shared enums already consumed by the API and pipeline.
- `constraints.py` and `value_objects.py` currently serve as reusable validation building blocks for future schema hardening.
- They are intentionally lightweight until more API and ingestion paths can adopt them without forcing mismatched abstractions.
- When backend schema validation is expanded, prefer importing these helpers instead of re-encoding election date, color, and date-range rules in multiple services.
