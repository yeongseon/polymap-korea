import type {
  BallotResolveResponse,
  CandidacyDetail,
  CandidacySummary,
  ClaimRead,
  ElectionDetail,
  ElectionSummary,
  IssueRead,
  IssueSummary,
  PersonRead,
  PersonSummary,
  PromiseRead,
  SearchResponse,
} from "@/lib/types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function resolveBallot(addressText: string): Promise<BallotResolveResponse> {
  return apiFetch<BallotResolveResponse>("/ballots/resolve", {
    method: "POST",
    body: JSON.stringify({ address_text: addressText }),
  });
}

export function getElections(): Promise<ElectionSummary[]> {
  return apiFetch<ElectionSummary[]>("/elections");
}

export function getElection(id: string): Promise<ElectionDetail> {
  return apiFetch<ElectionDetail>(`/elections/${id}`);
}

export function getCandidacy(id: string): Promise<CandidacyDetail> {
  return apiFetch<CandidacyDetail>(`/candidacies/${id}`);
}

export function getCandidacies(
  params: Record<string, string | number>
): Promise<CandidacySummary[]> {
  const qs = new URLSearchParams(
    Object.entries(params).map(([k, v]) => [k, String(v)])
  ).toString();
  return apiFetch<CandidacySummary[]>(`/candidacies${qs ? `?${qs}` : ""}`);
}

export function getPersons(): Promise<PersonSummary[]> {
  return apiFetch<PersonSummary[]>("/persons");
}

export function getPerson(id: string): Promise<PersonRead> {
  return apiFetch<PersonRead>(`/persons/${id}`);
}

export function getIssues(): Promise<IssueSummary[]> {
  return apiFetch<IssueSummary[]>("/issues");
}

export function getIssue(id: string): Promise<IssueRead> {
  return apiFetch<IssueRead>(`/issues/${id}`);
}

export function search(q: string, type?: string): Promise<SearchResponse> {
  const params = new URLSearchParams({ q });
  if (type) params.set("type", type);
  return apiFetch<SearchResponse>(`/search?${params.toString()}`);
}

export function getCandidacyPromises(id: string): Promise<PromiseRead[]> {
  return apiFetch<PromiseRead[]>(`/candidacies/${id}/promises`);
}

export function getCandidacyClaims(id: string): Promise<ClaimRead[]> {
  return apiFetch<ClaimRead[]>(`/candidacies/${id}/claims`);
}
