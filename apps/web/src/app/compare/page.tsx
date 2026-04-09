"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import Link from "next/link";
import { useCandidacy } from "@/lib/hooks";
import type { CandidacyDetail } from "@/lib/types";

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

function CandidacyColumn({
  candidacyId,
  index,
}: {
  candidacyId: string;
  index: number;
}) {
  const { data, isLoading, isError } = useCandidacy(candidacyId);

  if (isLoading) {
    return (
      <div className="flex min-h-[200px] items-center justify-center rounded-2xl border border-slate-200 bg-white">
        <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex min-h-[200px] items-center justify-center rounded-2xl border border-red-200 bg-red-50 p-4 text-center">
        <p className="text-sm text-red-600">불러오기 실패</p>
      </div>
    );
  }

  return <CandidacyCard candidacy={data} index={index} />;
}

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
  values: React.ReactNode[];
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

function CompareContent({ ids }: { ids: string[] }) {
  const q0 = useCandidacy(ids[0] ?? "");
  const q1 = useCandidacy(ids[1] ?? "");
  const q2 = useCandidacy(ids[2] ?? "");
  const q3 = useCandidacy(ids[3] ?? "");

  const queries = [q0, q1, q2, q3].slice(0, ids.length);
  const isLoading = queries.some((q) => q.isLoading);
  const candidacies = queries
    .map((q) => q.data)
    .filter((d): d is CandidacyDetail => d !== undefined);

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

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <span className="ml-3 text-slate-500">불러오는 중…</span>
        </div>
      ) : (
        <>
          <div
            className={`grid gap-4 ${
              ids.length === 2
                ? "md:grid-cols-2"
                : ids.length === 3
                ? "md:grid-cols-3"
                : "md:grid-cols-4"
            }`}
          >
            {ids.map((id, i) => (
              <CandidacyColumn key={id} candidacyId={id} index={i} />
            ))}
          </div>

          {candidacies.length >= 2 && (
            <div className="mt-10">
              <h2 className="mb-4 text-lg font-bold text-slate-900">
                상세 비교표
              </h2>
              <div className="overflow-x-auto rounded-2xl border border-slate-200 bg-white">
                <table className="w-full min-w-[500px]">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50">
                      <th className="w-28 px-4 py-3 text-left text-xs font-bold uppercase tracking-wider text-slate-500">
                        항목
                      </th>
                      {candidacies.map((c) => (
                        <th
                          key={c.id}
                          className="px-4 py-3 text-left text-sm font-bold text-slate-800"
                        >
                          {c.person.name_ko}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    <CompareTableRow
                      label="기호"
                      values={candidacies.map((c) =>
                        c.candidate_number !== null
                          ? `${c.candidate_number}번`
                          : "–"
                      )}
                    />
                    <CompareTableRow
                      label="정당"
                      values={candidacies.map((c) =>
                        c.party ? c.party.name_ko : "무소속"
                      )}
                    />
                    <CompareTableRow
                      label="상태"
                      values={candidacies.map(
                        (c) => STATUS_KO[c.status] ?? c.status
                      )}
                    />
                    <CompareTableRow
                      label="공약 수"
                      values={candidacies.map((c) => `${c.promises.length}개`)}
                    />
                    <CompareTableRow
                      label="주장 수"
                      values={candidacies.map((c) => `${c.claims.length}건`)}
                    />
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
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
