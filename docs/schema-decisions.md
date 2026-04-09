# Schema Decisions

- **No `Candidate` table**: the model is `Person -> Candidacy -> Race` so a person can run in multiple races over time without duplicating identity records.
- **`Promise` belongs to `Candidacy`**: promises are campaign-contextual and must attach to a specific run for office, not to the person globally.
- **`SourceDoc.kind` replaces `NewsArticle`**: all source artifacts live in one table, with `kind` distinguishing news, PDFs, official gazettes, API responses, and web pages.
- **No `confidence_score` on `Claim`**: claims are labeled with `claim_type` from the ontology, matching the approved architecture and avoiding a misleading numeric confidence field.
- **`AuditLog` is append-only**: it has a UUID primary key and `created_at` only, with no `updated_at` column.
- **Soft delete scope is limited**: only `Person`, `Party`, and `SourceDoc` carry `deleted_at`, per the approved lifecycle policy.
