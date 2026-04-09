export type UUID = string;

export interface PersonSummary {
  id: UUID;
  name_ko: string;
  name_en: string | null;
  photo_url: string | null;
}

export interface PersonRead extends PersonSummary {
  birth_date: string | null;
  gender: string | null;
  bio: string | null;
  external_ids: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface DistrictSummary {
  id: UUID;
  name_ko: string;
  level: string;
  code: string;
}

export interface DistrictRead extends DistrictSummary {
  name_en: string | null;
  parent_id: UUID | null;
  geometry: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ElectionSummary {
  id: UUID;
  name: string;
  election_date: string;
}

export interface ElectionRead extends ElectionSummary {
  election_type: string;
  created_at: string;
  updated_at: string;
}

export interface ElectionDetail extends ElectionRead {
  races: RaceRead[];
}

export interface RaceRead {
  id: UUID;
  election_id: UUID;
  district_id: UUID;
  position_type: string;
  seat_count: number;
  created_at: string;
  updated_at: string;
}

export interface PartySummary {
  id: UUID;
  name_ko: string;
  abbreviation: string | null;
  color_hex: string | null;
}

export interface CandidacySummary {
  id: UUID;
  person_id: UUID;
  race_id: UUID;
  status: string;
  candidate_number: number | null;
}

export interface CandidacyDetail {
  id: UUID;
  person_id: UUID;
  race_id: UUID;
  party_id: UUID | null;
  status: string;
  registered_at: string | null;
  candidate_number: number | null;
  created_at: string;
  updated_at: string;
  person: PersonSummary;
  party: PartySummary | null;
  promises: PromiseRead[];
  claims: ClaimRead[];
}

export interface PromiseRead {
  id: UUID;
  candidacy_id: UUID;
  title: string;
  body: string;
  category: string | null;
  issue_id: UUID | null;
  source_doc_id: UUID | null;
  sort_order: number;
  created_at: string;
  updated_at: string;
}

export interface ClaimRead {
  id: UUID;
  candidacy_id: UUID;
  source_doc_id: UUID;
  claim_type: string;
  content: string;
  excerpt: string | null;
  created_at: string;
  updated_at: string;
}

export interface IssueSummary {
  id: UUID;
  name: string;
  slug: string;
  parent_id: UUID | null;
}

export interface IssueTreeNode {
  id: UUID;
  name: string;
  slug: string;
  parent_id: UUID | null;
  children: IssueTreeNode[];
}

export interface IssueRead extends IssueSummary {
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface IssuePromiseSummary {
  id: UUID;
  candidacy_id: UUID;
  title: string;
  sort_order: number;
  candidacy: CandidacySummary;
}

export interface IssueDetail extends IssueRead {
  related_promises: IssuePromiseSummary[];
}

export interface SourceDocRead {
  id: UUID;
  kind: string;
  title: string;
  url: string | null;
  published_at: string | null;
  content_hash: string | null;
  raw_s3_key: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

export interface SearchResponse {
  query: string;
  persons: PersonSummary[];
  issues: IssueSummary[];
  parties: PartySummary[];
}

export interface BallotRaceResult {
  race: RaceRead;
  candidacies: CandidacySummary[];
}

export interface BallotResolveResponse {
  district: DistrictRead;
  races: BallotRaceResult[];
}
