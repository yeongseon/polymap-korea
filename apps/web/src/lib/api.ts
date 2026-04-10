import type {
  BallotResolveResponse,
  CandidacyDetail,
  CandidacySummary,
  ClaimRead,
  ComparisonResult,
  DistrictRead,
  ElectionDetail,
  ElectionSummary,
  IssueDetail,
  IssueTreeNode,
  PartySummary,
  PersonRead,
  PersonSummary,
  PromiseRead,
  RaceRead,
  SearchResponse,
  SourceDocRead,
} from "@/lib/types";

const BASE_PATH = "/polymap-korea";

type DemoElectionsData = {
  summaries: ElectionSummary[];
  details: ElectionDetail[];
};

type DemoCandidaciesData = {
  details: CandidacyDetail[];
};

type DemoIssuesData = {
  tree: IssueTreeNode[];
  details: IssueDetail[];
};

type CompareBundle = {
  candidacies: CandidacyDetail[];
  comparison: ComparisonResult;
};

type BallotResolveEntry = {
  address_keywords: string[];
  response: BallotResolveResponse;
};

type DemoBallotResolveData = {
  default_address: string;
  responses: BallotResolveEntry[];
};

async function demoFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_PATH}/demo/${path}`, {
    headers: { "Content-Type": "application/json", ...init?.headers },
    cache: "force-cache",
    ...init,
  });
  if (!res.ok) {
    throw new Error(`요청을 처리할 수 없습니다 (${res.status})`);
  }
  return res.json() as Promise<T>;
}

function ensureFound<T>(item: T | undefined, message: string): T {
  if (!item) {
    throw new Error(message);
  }
  return item;
}

async function getElectionsData() {
  return demoFetch<DemoElectionsData>("elections.json");
}

async function getCandidaciesData() {
  return demoFetch<DemoCandidaciesData>("candidacies.json");
}

async function getIssuesData() {
  return demoFetch<DemoIssuesData>("issues.json");
}

async function getPersonsData() {
  return demoFetch<PersonRead[]>("persons.json");
}

async function getSourcesData() {
  return demoFetch<SourceDocRead[]>("sources.json");
}

async function getDistrictsData() {
  return demoFetch<DistrictRead[]>("districts.json");
}

async function getBallotResolveData() {
  return demoFetch<DemoBallotResolveData>("ballot-resolve.json");
}

async function getPartyIndex() {
  const { details } = await getCandidaciesData();
  const parties = new Map<string, PartySummary>();

  for (const candidacy of details) {
    if (candidacy.party) {
      parties.set(candidacy.party.id, candidacy.party);
    }
  }

  return Array.from(parties.values());
}

async function getRaceIndex() {
  const { details } = await getElectionsData();
  return new Map(details.flatMap((election) => election.races.map((race) => [race.id, race])));
}

function compareIssueKey(issueId: string | null) {
  return issueId ?? "unassigned";
}

async function buildCompareBundle(ids: string[]): Promise<CompareBundle> {
  const uniqueIds = Array.from(new Set(ids.filter(Boolean))).slice(0, 4);

  if (uniqueIds.length < 2) {
    throw new Error("비교하려면 후보 2명 이상이 필요합니다.");
  }

  const [candidaciesData, issuesData] = await Promise.all([
    getCandidaciesData(),
    getIssuesData(),
  ]);

  const candidacyIndex = new Map(
    candidaciesData.details.map((candidacy) => [candidacy.id, candidacy])
  );
  const candidacies = uniqueIds.map((id) =>
    ensureFound(candidacyIndex.get(id), "후보 정보를 찾을 수 없습니다")
  );
  const issueNameById = new Map(
    issuesData.details.map((issue) => [issue.id, issue.name])
  );
  const groupedPromises = new Map<string, Record<string, PromiseRead[]>>();

  for (const candidacy of candidacies) {
    for (const promise of candidacy.promises) {
      const issueKey = compareIssueKey(promise.issue_id);
      const issuePromises = groupedPromises.get(issueKey) ?? {};
      const existingPromises = issuePromises[candidacy.id] ?? [];

      issuePromises[candidacy.id] = [...existingPromises, promise].sort(
        (left, right) => left.sort_order - right.sort_order
      );
      groupedPromises.set(issueKey, issuePromises);
    }
  }

  const orderedIssues = Array.from(groupedPromises.keys()).sort((left, right) => {
    if (left === "unassigned") return 1;
    if (right === "unassigned") return -1;

    return (issueNameById.get(left) ?? "").localeCompare(issueNameById.get(right) ?? "", "ko");
  });

  const by_issue = Object.fromEntries(
    orderedIssues.map((issueKey) => [
      issueKey,
      {
        issue_name:
          issueKey === "unassigned"
            ? "기타"
            : issueNameById.get(issueKey) ?? "이슈 미분류",
        positions: candidacies.map((candidacy) => ({
          candidacy_id: candidacy.id,
          promises: groupedPromises.get(issueKey)?.[candidacy.id] ?? [],
        })),
      },
    ])
  );

  return {
    candidacies,
    comparison: {
      candidacy_ids: candidacies.map((candidacy) => candidacy.id),
      by_issue,
    },
  };
}

export function resolveBallot(addressText: string): Promise<BallotResolveResponse> {
  return getBallotResolveData().then((data) => {
    const normalized = addressText.replace(/\s+/g, "").toLowerCase();
    const match = data.responses.find((entry) =>
      entry.address_keywords.some((keyword) =>
        normalized.includes(keyword.replace(/\s+/g, "").toLowerCase())
      )
    );

    if (!match) {
      throw new Error("데모 데이터에 등록된 서울특별시 마포구 주소를 입력해주세요.");
    }

    return match.response;
  });
}

export function getElections(): Promise<ElectionSummary[]> {
  return getElectionsData().then((data) => data.summaries);
}

export function getElection(id: string): Promise<ElectionDetail> {
  return getElectionsData().then((data) =>
    ensureFound(data.details.find((election) => election.id === id), "선거 정보를 찾을 수 없습니다")
  );
}

export function getCandidacy(id: string): Promise<CandidacyDetail> {
  return getCandidaciesData().then((data) =>
    ensureFound(data.details.find((candidacy) => candidacy.id === id), "후보 정보를 찾을 수 없습니다")
  );
}

export function getSource(id: string): Promise<SourceDocRead> {
  return getSourcesData().then((sources) =>
    ensureFound(sources.find((source) => source.id === id), "출처 문서를 찾을 수 없습니다")
  );
}

export function getCandidacies(
  params: Record<string, string | number>
): Promise<CandidacySummary[]> {
  return Promise.all([getCandidaciesData(), getRaceIndex()]).then(([data, raceIndex]) => {
    const list = data.details.filter((candidacy) => {
      const race = raceIndex.get(candidacy.race_id);
      if (!race) return false;

      return Object.entries(params).every(([key, value]) => {
        const stringValue = String(value);

        switch (key) {
          case "district_id":
            return race.district_id === stringValue;
          case "race_id":
            return candidacy.race_id === stringValue;
          case "person_id":
            return candidacy.person_id === stringValue;
          case "status":
            return candidacy.status === stringValue;
          case "candidate_number":
            return String(candidacy.candidate_number) === stringValue;
          case "position_type":
            return race.position_type === stringValue;
          case "election_id":
            return race.election_id === stringValue;
          default:
            return true;
        }
      });
    });

    return list.map(({ id, person_id, race_id, status, candidate_number }) => ({
      id,
      person_id,
      race_id,
      status,
      candidate_number,
    }));
  });
}

export function getPersons(): Promise<PersonSummary[]> {
  return getPersonsData().then((persons) =>
    persons.map(({ id, name_ko, name_en, photo_url }) => ({
      id,
      name_ko,
      name_en,
      photo_url,
    }))
  );
}

export function getPerson(id: string): Promise<PersonRead> {
  return getPersonsData().then((persons) =>
    ensureFound(persons.find((person) => person.id === id), "인물 정보를 찾을 수 없습니다")
  );
}

export function getIssues(): Promise<IssueTreeNode[]> {
  return getIssuesData().then((data) => data.tree);
}

export function getIssue(id: string): Promise<IssueDetail> {
  return getIssuesData().then((data) =>
    ensureFound(data.details.find((issue) => issue.id === id), "이슈 정보를 찾을 수 없습니다")
  );
}

export function search(q: string, type?: string): Promise<SearchResponse> {
  const keyword = q.trim().toLowerCase();

  return Promise.all([getPersons(), getIssuesData(), getPartyIndex()]).then(
    ([persons, issuesData, parties]) => {
      const issueSummaries = issuesData.details.map(({ id, name, slug, parent_id }) => ({
        id,
        name,
        slug,
        parent_id,
      }));

      const matches = (values: Array<string | null | undefined>) =>
        values.some((value) => value?.toLowerCase().includes(keyword));

      const filteredPersons = keyword
        ? persons.filter((person) => matches([person.name_ko, person.name_en]))
        : [];
      const filteredIssues = keyword
        ? issueSummaries.filter((issue) => matches([issue.name, issue.slug]))
        : [];
      const filteredParties = keyword
        ? parties.filter((party) => matches([party.name_ko, party.abbreviation]))
        : [];

      if (type === "persons") {
        return { query: q, persons: filteredPersons, issues: [], parties: [] };
      }
      if (type === "issues") {
        return { query: q, persons: [], issues: filteredIssues, parties: [] };
      }
      if (type === "parties") {
        return { query: q, persons: [], issues: [], parties: filteredParties };
      }

      return {
        query: q,
        persons: filteredPersons,
        issues: filteredIssues,
        parties: filteredParties,
      };
    }
  );
}

export function getCandidacyPromises(id: string): Promise<PromiseRead[]> {
  return getCandidacy(id).then((candidacy) => candidacy.promises);
}

export function getCandidacyClaims(id: string): Promise<ClaimRead[]> {
  return getCandidacy(id).then((candidacy) => candidacy.claims);
}

export function compareCandidacies(ids: string[]): Promise<ComparisonResult> {
  return buildCompareBundle(ids).then((bundle) => bundle.comparison);
}

export function getCompareBundle(ids: string[]): Promise<CompareBundle> {
  return buildCompareBundle(ids);
}

export function getCandidaciesByDistrict(
  districtId: string
): Promise<CandidacySummary[]> {
  return getCandidacies({ district_id: districtId });
}

export function getIssuesISR(): Promise<IssueTreeNode[]> {
  return getIssues();
}

export function getIssueISR(id: string): Promise<IssueDetail> {
  return getIssue(id);
}

export function getDistricts(): Promise<DistrictRead[]> {
  return getDistrictsData();
}

export function getBallotByDistrict(districtId: string): Promise<BallotResolveResponse> {
  return getBallotResolveData().then((data) => {
    const match = data.responses.find(
      (entry) => entry.response.district.id === districtId
    );

    return ensureFound(match?.response, "선거구 정보를 찾을 수 없습니다");
  });
}
