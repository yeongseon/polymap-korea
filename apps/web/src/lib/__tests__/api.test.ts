import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  compareCandidacies,
  getCandidacy,
  getElections,
  resolveBallot,
  search,
} from "@/lib/api";

const demoFixtures = {
  "elections.json": {
    summaries: [{ id: "election-1", name: "2026 서울시장 선거", election_date: "2026-06-03" }],
    details: [
      {
        id: "election-1",
        name: "2026 서울시장 선거",
        election_type: "local",
        election_date: "2026-06-03",
        created_at: "2026-01-01T00:00:00+09:00",
        updated_at: "2026-01-02T00:00:00+09:00",
        races: [
          {
            id: "race-1",
            election_id: "election-1",
            district_id: "district-1",
            position_type: "mayor",
            seat_count: 1,
            created_at: "2026-01-01T00:00:00+09:00",
            updated_at: "2026-01-02T00:00:00+09:00",
          },
        ],
      },
    ],
  },
  "candidacies.json": {
    details: [
      {
        id: "candidacy-1",
        person_id: "person-1",
        race_id: "race-1",
        party_id: "party-1",
        status: "registered",
        registered_at: "2026-02-01T00:00:00+09:00",
        candidate_number: 1,
        created_at: "2026-02-01T00:00:00+09:00",
        updated_at: "2026-02-02T00:00:00+09:00",
        person: {
          id: "person-1",
          name_ko: "김민수",
          name_en: "Kim Min-su",
          photo_url: null,
        },
        party: {
          id: "party-1",
          name_ko: "더불어민주당",
          abbreviation: "민주",
          color_hex: "#1d70b8",
        },
        promises: [
          {
            id: "promise-1",
            candidacy_id: "candidacy-1",
            title: "청년 일자리 확대",
            body: "공공 인턴십을 확대합니다.",
            category: "일자리",
            issue_id: "issue-jobs",
            source_doc_id: "source-1",
            sort_order: 1,
            created_at: "2026-02-03T00:00:00+09:00",
            updated_at: "2026-02-04T00:00:00+09:00",
          },
        ],
        claims: [
          {
            id: "claim-1",
            candidacy_id: "candidacy-1",
            source_doc_id: "source-1",
            claim_type: "official_fact",
            content: "대중교통 개편 경험이 있습니다.",
            excerpt: null,
            created_at: "2026-02-05T00:00:00+09:00",
            updated_at: "2026-02-06T00:00:00+09:00",
          },
        ],
      },
      {
        id: "candidacy-2",
        person_id: "person-2",
        race_id: "race-1",
        party_id: "party-2",
        status: "registered",
        registered_at: "2026-02-01T00:00:00+09:00",
        candidate_number: 2,
        created_at: "2026-02-01T00:00:00+09:00",
        updated_at: "2026-02-02T00:00:00+09:00",
        person: {
          id: "person-2",
          name_ko: "이지은",
          name_en: "Lee Ji-eun",
          photo_url: null,
        },
        party: {
          id: "party-2",
          name_ko: "국민의힘",
          abbreviation: "국힘",
          color_hex: "#e61e2b",
        },
        promises: [
          {
            id: "promise-2",
            candidacy_id: "candidacy-2",
            title: "심야버스 증편",
            body: "심야버스 배차를 늘립니다.",
            category: "교통",
            issue_id: "issue-transport",
            source_doc_id: "source-2",
            sort_order: 1,
            created_at: "2026-02-03T00:00:00+09:00",
            updated_at: "2026-02-04T00:00:00+09:00",
          },
        ],
        claims: [],
      },
    ],
  },
  "issues.json": {
    tree: [],
    details: [
      {
        id: "issue-jobs",
        name: "일자리",
        slug: "jobs",
        parent_id: null,
        description: null,
        created_at: "2026-01-01T00:00:00+09:00",
        updated_at: "2026-01-01T00:00:00+09:00",
        related_promises: [],
      },
      {
        id: "issue-transport",
        name: "교통",
        slug: "transport",
        parent_id: null,
        description: null,
        created_at: "2026-01-01T00:00:00+09:00",
        updated_at: "2026-01-01T00:00:00+09:00",
        related_promises: [],
      },
    ],
  },
  "persons.json": [
    {
      id: "person-1",
      name_ko: "김민수",
      name_en: "Kim Min-su",
      photo_url: null,
      birth_date: null,
      gender: null,
      bio: null,
      external_ids: {},
      created_at: "2026-01-01T00:00:00+09:00",
      updated_at: "2026-01-02T00:00:00+09:00",
      deleted_at: null,
    },
    {
      id: "person-2",
      name_ko: "이지은",
      name_en: "Lee Ji-eun",
      photo_url: null,
      birth_date: null,
      gender: null,
      bio: null,
      external_ids: {},
      created_at: "2026-01-01T00:00:00+09:00",
      updated_at: "2026-01-02T00:00:00+09:00",
      deleted_at: null,
    },
  ],
  "ballot-resolve.json": {
    default_address: "서울특별시 마포구 월드컵북로 1",
    responses: [
      {
        address_keywords: ["서울 마포구", "월드컵북로"],
        response: {
          district: {
            id: "district-1",
            name_ko: "서울특별시 마포구",
            level: "basic",
            code: "11044",
            name_en: "Mapo-gu",
            parent_id: null,
            geometry: {},
            created_at: "2026-01-01T00:00:00+09:00",
            updated_at: "2026-01-02T00:00:00+09:00",
          },
          races: [
            {
              race: {
                id: "race-1",
                election_id: "election-1",
                district_id: "district-1",
                position_type: "mayor",
                seat_count: 1,
                created_at: "2026-01-01T00:00:00+09:00",
                updated_at: "2026-01-02T00:00:00+09:00",
              },
              candidacies: [
                {
                  id: "candidacy-1",
                  person_id: "person-1",
                  race_id: "race-1",
                  status: "registered",
                  candidate_number: 1,
                },
              ],
            },
          ],
        },
      },
    ],
  },
} as const;

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: string | URL | Request) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
      const path = url.split("/demo/")[1];
      const fixture = demoFixtures[path as keyof typeof demoFixtures];

      if (!fixture) {
        return new Response("not found", { status: 404 });
      }

      return new Response(JSON.stringify(fixture), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    })
  );
});

describe("demo api", () => {
  it("loads election summaries", async () => {
    await expect(getElections()).resolves.toEqual(demoFixtures["elections.json"].summaries);
  });

  it("loads candidacy detail", async () => {
    const candidacy = await getCandidacy("candidacy-1");

    expect(candidacy.person.name_ko).toBe("김민수");
    expect(candidacy.promises).toHaveLength(1);
  });

  it("searches across people, issues, and parties", async () => {
    const result = await search("교통");

    expect(result.issues).toHaveLength(1);
    expect(result.issues[0]?.name).toBe("교통");

    const partyResult = await search("국힘", "parties");
    expect(partyResult.parties[0]?.name_ko).toBe("국민의힘");
  });

  it("resolves a ballot from a supported address", async () => {
    const result = await resolveBallot("서울특별시 마포구 월드컵북로 1");

    expect(result.district.name_ko).toBe("서울특별시 마포구");
    expect(result.races[0]?.candidacies[0]?.id).toBe("candidacy-1");
  });

  it("groups comparison data by issue", async () => {
    const result = await compareCandidacies(["candidacy-1", "candidacy-2"]);

    expect(result.candidacy_ids).toEqual(["candidacy-1", "candidacy-2"]);
    expect(result.by_issue["issue-jobs"]?.positions[0]?.promises[0]?.title).toBe("청년 일자리 확대");
    expect(result.by_issue["issue-transport"]?.positions[1]?.promises[0]?.title).toBe("심야버스 증편");
  });
});
