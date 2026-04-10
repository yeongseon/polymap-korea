"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, type ReactNode } from "react";
import Link from "next/link";
import { useCompare } from "@/lib/hooks";
import type { CandidacyDetail, PromiseRead } from "@/lib/types";

const CLAIM_TYPE_KO: Record<string, string> = {
  official_fact: "공식 사실",
  sourced_claim: "출처 확인",
  opinion: "의견",
  disputed: "논쟁 중",
  ai_summary: "AI 요약",
};

const STATUS_KO: Record<string, string> = {
  registered: "등록",
  withdrawn: "사퇴",
  disqualified: "무효",
  elected: "당선",
  defeated: "낙선",
};

function CandidacyCard({
  candidacy,
  index,
}: {
  candidacy: CandidacyDetail;
  index: number;
}) {
  const accentColors = [
    "border-blue-400",
    "border-purple-400",
    "border-green-400",
    "border-amber-400",
  ];
  const accentColor = accentColors[index % accentColors.length];

  return (
    <div
      className={`rounded-2xl border-2 ${accentColor} bg-white overflow-hidden shadow-sm`}
    >
      <div className="border-b border-slate-100 p-5">
        <div className="flex items-center gap-3">
          <div
            className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-slate-400 to-slate-600 text-lg font-black text-white"
          >
            {candidacy.person.name_ko.slice(0, 1)}
          </div>
          <div>
            <h3 className="text-lg font-black text-slate-900">
              {candidacy.person.name_ko}
            </h3>
            {candidacy.candidate_number !== null && (
              <span className="text-xs text-slate-500">
                기호 {candidacy.candidate_number}번
              </span>
            )}
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-1.5">
          <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700">
            {STATUS_KO[candidacy.status] ?? candidacy.status}
          </span>
          {candidacy.party && (
            <span
              className="rounded-full px-2.5 py-0.5 text-xs font-medium text-white"
              style={{ backgroundColor: candidacy.party.color_hex ?? "#8b5cf6" }}
            >
              {candidacy.party.name_ko}
            </span>
          )}
        </div>

        <Link
          href={`/candidate/${candidacy.id}`}
          className="mt-3 inline-block text-xs font-medium text-blue-600 hover:underline"
        >
          상세보기 →
        </Link>
      </div>

      <div className="p-5">
        <h4 className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-500">
          핵심 공약
        </h4>
        {candidacy.promises.length === 0 ? (
          <p className="text-sm text-slate-400">공약 정보 없음</p>
        ) : (
          <ol className="space-y-2">
            {candidacy.promises.map((p, i) => (
              <li key={p.id} className="flex gap-2">
                <span className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full bg-green-100 text-xs font-bold text-green-700">
                  {i + 1}
                </span>
                <div>
                  <p className="text-sm font-medium text-slate-800 line-clamp-2">
                    {p.title}
                  </p>
                  {p.category && (
                    <span className="text-xs text-slate-400">{p.category}</span>
                  )}
                </div>
              </li>
            ))}
          </ol>
        )}
      </div>

      {candidacy.claims.length > 0 && (
        <div className="border-t border-slate-100 p-5">
          <h4 className="mb-3 text-xs font-bold uppercase tracking-wider text-slate-500">
            관련 주장 ({candidacy.claims.length}건)
          </h4>
          <div className="space-y-2">
            {candidacy.claims.slice(0, 3).map((c) => (
              <div
                key={c.id}
                className="rounded-lg bg-amber-50 p-2.5"
              >
                <span className="text-xs font-bold text-amber-700">
                  {CLAIM_TYPE_KO[c.claim_type] ?? c.claim_type}
                </span>
                <p className="mt-1 text-xs text-slate-600 line-clamp-2">
                  {c.content}
                </p>
              </div>
            ))}
            {candidacy.claims.length > 3 && (
              <p className="text-xs text-slate-400">
                +{candidacy.claims.length - 3}건 더 있음
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function CompareTableRow({
  label,
  values,
}: {
  label: string;
  values: ReactNode[];
}) {
  return (
    <tr className="border-b border-slate-100">
      <td className="w-28 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-600">
        {label}
      </td>
      {values.map((v, i) => (
        <td key={i} className="px-4 py-3 text-sm text-slate-800">
          {v}
        </td>
      ))}
    </tr>
  );
}

function PromiseList({ promises }: { promises: PromiseRead[] }) {
  if (promises.length === 0) {
    return <p className="text-sm text-slate-400">해당 이슈 공약 없음</p>;
  }

  return (
    <ul className="space-y-2">
      {promises.map((promise) => (
        <li key={promise.id} className="rounded-xl border border-slate-200 bg-white p-3">
          <p className="text-sm font-semibold text-slate-900">{promise.title}</p>
          {promise.body && <p className="mt-1 text-xs leading-relaxed text-slate-500">{promise.body}</p>}
        </li>
      ))}
    </ul>
  );
}

function CompareContent({ ids }: { ids: string[] }) {
  const normalizedIds = Array.from(new Set(ids)).slice(0, 4);
  const { data, isLoading, isError } = useCompare(normalizedIds);

  if (ids.length === 0) {
    return (
      <div className="rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center">
        <p className="text-4xl">⚖️</p>
        <p className="mt-4 text-lg font-semibold text-slate-700">
          비교할 후보를 선택해주세요
        </p>
        <p className="mt-2 text-sm text-slate-400">
          투표지 페이지에서 후보를 2명 이상 선택한 후 비교하기를 누르세요.
        </p>
        <Link
          href="/"
          className="mt-6 inline-block rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-bold text-white hover:bg-blue-500"
        >
          홈으로
        </Link>
      </div>
    );
  }

  if (normalizedIds.length < 2) {
    return (
      <div className="rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center">
        <p className="text-sm font-semibold text-amber-800">비교는 최소 2명의 후보가 필요합니다.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <span className="ml-3 text-slate-500">비교 데이터를 불러오는 중…</span>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="rounded-2xl border border-red-200 bg-red-50 p-6 text-center">
        <p className="text-sm font-semibold text-red-700">비교 데이터를 불러오지 못했습니다.</p>
      </div>
    );
  }

  const candidacies = data.candidacies;
  const issues = Object.entries(data.comparison.by_issue);

  return (
    <div>
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
          후보 비교
        </p>
        <h1 className="mt-1 text-3xl font-black text-slate-900">
          {ids.length}명 후보 비교
        </h1>
        <p className="mt-2 text-slate-500">
          선택한 후보들의 공약과 주요 정보를 비교합니다.
        </p>
      </div>

      <>
        <div
          className={`grid gap-4 ${
            candidacies.length === 2
              ? "md:grid-cols-2"
              : candidacies.length === 3
              ? "md:grid-cols-3"
              : "md:grid-cols-4"
          }`}
        >
          {candidacies.map((candidacy, index) => (
            <CandidacyCard key={candidacy.id} candidacy={candidacy} index={index} />
          ))}
        </div>

        <div className="mt-10">
          <h2 className="mb-4 text-lg font-bold text-slate-900">상세 비교표</h2>
          <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
            <table className="w-full min-w-[500px]">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50">
                  <th className="w-28 px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-500">
                    항목
                  </th>
                  {candidacies.map((candidacy) => (
                    <th key={candidacy.id} className="px-4 py-3 text-left text-sm font-bold text-slate-800">
                      {candidacy.person.name_ko}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <CompareTableRow
                  label="기호"
                  values={candidacies.map((candidacy) =>
                    candidacy.candidate_number !== null ? `${candidacy.candidate_number}번` : "–"
                  )}
                />
                <CompareTableRow
                  label="정당"
                  values={candidacies.map((candidacy) =>
                    candidacy.party ? candidacy.party.name_ko : "무소속"
                  )}
                />
                <CompareTableRow
                  label="상태"
                  values={candidacies.map((candidacy) => STATUS_KO[candidacy.status] ?? candidacy.status)}
                />
                <CompareTableRow
                  label="공약 수"
                  values={candidacies.map((candidacy) => `${candidacy.promises.length}개`)}
                />
                <CompareTableRow
                  label="주장 수"
                  values={candidacies.map((candidacy) => `${candidacy.claims.length}건`)}
                />
              </tbody>
            </table>
          </div>
        </div>

        {issues.length > 0 && (
          <div className="mt-10 space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">이슈별 공약 비교</h2>
              <p className="mt-1 text-sm text-slate-500">비교 API 결과를 기준으로 이슈별 입장을 나란히 정리했습니다.</p>
            </div>

            {issues.map(([issueKey, issue]) => (
              <section key={issueKey} className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <h3 className="text-base font-bold text-slate-900">{issue.issue_name}</h3>
                  <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-500 ring-1 ring-slate-200">
                    {issue.positions.reduce((count, position) => count + position.promises.length, 0)}개 공약
                  </span>
                </div>

                <div
                  className={`grid gap-4 ${
                    candidacies.length === 2
                      ? "md:grid-cols-2"
                      : candidacies.length === 3
                      ? "md:grid-cols-3"
                      : "md:grid-cols-4"
                  }`}
                >
                  {issue.positions.map((position) => {
                    const candidacy = candidacies.find(
                      (candidate) => candidate.id === position.candidacy_id
                    );

                    if (!candidacy) {
                      return null;
                    }

                    return (
                      <div key={position.candidacy_id} className="space-y-3 rounded-2xl border border-slate-200 bg-white p-4">
                        <div>
                          <p className="text-sm font-bold text-slate-900">{candidacy.person.name_ko}</p>
                          <p className="text-xs text-slate-500">
                            {candidacy.party?.name_ko ?? "무소속"}
                          </p>
                        </div>
                        <PromiseList promises={position.promises} />
                      </div>
                    );
                  })}
                </div>
              </section>
            ))}
          </div>
        )}
      </>
    </div>
  );
}

function ComparePageInner() {
  const searchParams = useSearchParams();
  const idsParam = searchParams.get("ids") ?? "";
  const ids = idsParam
    .split(",")
    .map((id) => id.trim())
    .filter(Boolean)
    .slice(0, 4);

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <CompareContent ids={ids} />
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        </div>
      }
    >
      <ComparePageInner />
    </Suspense>
  );
}
