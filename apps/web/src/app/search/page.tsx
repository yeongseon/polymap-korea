"use client";

import Link from "next/link";
import { useSearchParams, useRouter, usePathname } from "next/navigation";
import { useState, useEffect, useCallback, Suspense } from "react";
import { useSearch } from "@/lib/hooks";
import type { IssueSummary, PartySummary, PersonSummary } from "@/lib/types";

type TabKey = "all" | "persons" | "issues" | "parties";

const TABS: { key: TabKey; label: string }[] = [
  { key: "all", label: "전체" },
  { key: "persons", label: "인물" },
  { key: "issues", label: "이슈" },
  { key: "parties", label: "정당" },
];

const URL_TYPE_TO_TAB: Record<string, TabKey> = {
  persons: "persons",
  person: "persons",
  issues: "issues",
  issue: "issues",
  parties: "parties",
  party: "parties",
};

const TAB_TO_API_TYPE: Record<TabKey, string | undefined> = {
  all: undefined,
  persons: "persons",
  issues: "issues",
  parties: "parties",
};

function PersonItem({ person }: { person: PersonSummary }) {
  return (
    <Link
      href={`/search?q=${encodeURIComponent(person.name_ko)}&type=persons`}
      className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-4 transition hover:border-blue-200 hover:bg-blue-50/40"
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-600">
        {person.name_ko.slice(0, 1)}
      </div>
      <div>
        <p className="font-semibold text-slate-900">{person.name_ko}</p>
        {person.name_en && <p className="text-xs text-slate-500">{person.name_en}</p>}
      </div>
    </Link>
  );
}

function IssueItem({ issue }: { issue: IssueSummary }) {
  return (
    <Link
      href={`/issues/${issue.id}`}
      className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-4 transition hover:border-blue-200 hover:bg-blue-50/40"
    >
      <span className="text-2xl">📌</span>
      <div>
        <p className="font-semibold text-slate-900">{issue.name}</p>
        <p className="text-xs text-slate-500">/{issue.slug}</p>
      </div>
    </Link>
  );
}

function PartyItem({ party }: { party: PartySummary }) {
  return (
    <div className="flex items-center gap-3 rounded-xl border border-slate-100 bg-white p-4">
      <div
        className="h-4 w-4 shrink-0 rounded-full"
        style={{ background: party.color_hex ?? "#94a3b8" }}
      />
      <div>
        <p className="font-semibold text-slate-900">{party.name_ko}</p>
        {party.abbreviation && (
          <p className="text-xs text-slate-500">{party.abbreviation}</p>
        )}
      </div>
    </div>
  );
}

function SearchContent() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const initialQ = searchParams.get("q") ?? "";
  const urlType = searchParams.get("type") ?? "";
  const initialTab = URL_TYPE_TO_TAB[urlType] ?? "all";

  const [input, setInput] = useState(initialQ);
  const [activeTab, setActiveTab] = useState<TabKey>(initialTab);

  useEffect(() => {
    setInput(initialQ);
  }, [initialQ]);

  useEffect(() => {
    setActiveTab(URL_TYPE_TO_TAB[urlType] ?? "all");
  }, [urlType]);

  const apiType = TAB_TO_API_TYPE[activeTab];
  const { data, isFetching, isError } = useSearch(initialQ, apiType);

  const updateUrl = useCallback(
    (q: string, type?: string) => {
      const params = new URLSearchParams();
      if (q) params.set("q", q);
      if (type && type !== "all") params.set("type", type);
      router.push(`${pathname}?${params.toString()}`);
    },
    [router, pathname]
  );

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    updateUrl(input.trim(), activeTab === "all" ? undefined : activeTab);
  }

  function handleTabChange(tab: TabKey) {
    setActiveTab(tab);
    if (initialQ) {
      updateUrl(initialQ, tab === "all" ? undefined : tab);
    }
  }

  const persons = data?.persons ?? [];
  const issues = data?.issues ?? [];
  const parties = data?.parties ?? [];
  const totalCount = persons.length + issues.length + parties.length;

  const showPersons = activeTab === "all" || activeTab === "persons";
  const showIssues = activeTab === "all" || activeTab === "issues";
  const showParties = activeTab === "all" || activeTab === "parties";

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <h1 className="mb-6 text-3xl font-black text-slate-900">검색</h1>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <label htmlFor="search-input" className="sr-only">
          검색어 입력
        </label>
        <input
          id="search-input"
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="후보자, 이슈, 정당 검색…"
          className="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
        />
        <button
          type="submit"
          className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-500"
        >
          검색
        </button>
      </form>

      {initialQ && (
        <div className="mt-6">
          <div className="flex gap-1 border-b border-slate-200">
            {TABS.map(({ key, label }) => (
              <button
                key={key}
                onClick={() => handleTabChange(key)}
                className={`px-4 py-2 text-sm font-semibold transition ${
                  activeTab === key
                    ? "border-b-2 border-blue-600 text-blue-600"
                    : "text-slate-500 hover:text-slate-900"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {isFetching ? (
            <div className="mt-10 flex justify-center">
              <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
            </div>
          ) : isError ? (
            <p className="mt-6 text-sm text-red-500">검색 중 오류가 발생했습니다.</p>
          ) : totalCount === 0 ? (
            <div className="mt-12 text-center">
              <p className="text-4xl">🔍</p>
              <p className="mt-3 text-lg font-semibold text-slate-700">결과가 없습니다</p>
              <p className="mt-1 text-sm text-slate-400">
                &ldquo;{initialQ}&rdquo;에 대한 검색 결과가 없습니다.
              </p>
            </div>
          ) : (
            <div className="mt-6 flex flex-col gap-3">
              {showPersons && persons.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
                    인물 ({persons.length})
                  </p>
                  {persons.map((p) => (
                    <div key={p.id} className="mb-2">
                      <PersonItem person={p} />
                    </div>
                  ))}
                </div>
              )}
              {showIssues && issues.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
                    이슈 ({issues.length})
                  </p>
                  {issues.map((i) => (
                    <div key={i.id} className="mb-2">
                      <IssueItem issue={i} />
                    </div>
                  ))}
                </div>
              )}
              {showParties && parties.length > 0 && (
                <div>
                  <p className="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
                    정당 ({parties.length})
                  </p>
                  {parties.map((p) => (
                    <div key={p.id} className="mb-2">
                      <PartyItem party={p} />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {!initialQ && (
        <div className="mt-16 text-center">
          <p className="text-5xl">🗺️</p>
          <p className="mt-4 text-lg font-semibold text-slate-700">무엇을 찾고 계신가요?</p>
          <p className="mt-2 text-sm text-slate-400">
            후보자 이름, 정당명, 이슈 키워드를 입력해보세요.
          </p>
        </div>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
      </div>
    }>
      <SearchContent />
    </Suspense>
  );
}
