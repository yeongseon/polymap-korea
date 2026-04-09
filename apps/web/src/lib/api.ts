import type {
  BallotResolveResponse,
  CandidacyDetail,
  CandidacySummary,
  ClaimRead,
  ElectionDetail,
  ElectionSummary,
  IssueDetail,
  IssueTreeNode,
  PersonRead,
  PersonSummary,
  PromiseRead,
  SearchResponse,
} from "@/lib/types";

const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const SERVER_BASE_URL =
  process.env.API_URL_INTERNAL ?? BASE_URL;

const ISR_REVALIDATE = 300;

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`요청을 처리할 수 없습니다 (${res.status})`);
  }
  return res.json() as Promise<T>;
}

async function serverFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${SERVER_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    next: { revalidate: ISR_REVALIDATE },
  });
  if (!res.ok) {
    throw new Error(`요청을 처리할 수 없습니다 (${res.status})`);
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

export function getIssues(): Promise<IssueTreeNode[]> {
  return apiFetch<IssueTreeNode[]>("/issues");
}

export function getIssue(id: string): Promise<IssueDetail> {
  return apiFetch<IssueDetail>(`/issues/${id}`);
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

export function getCandidaciesByDistrict(
  districtId: string
): Promise<CandidacySummary[]> {
  return apiFetch<CandidacySummary[]>(
    `/candidacies?district_id=${districtId}`
  );
}

export function getIssuesISR(): Promise<IssueTreeNode[]> {
  return serverFetch<IssueTreeNode[]>("/issues");
}

export function getIssueISR(id: string): Promise<IssueDetail> {
  return serverFetch<IssueDetail>(`/issues/${id}`);
}
