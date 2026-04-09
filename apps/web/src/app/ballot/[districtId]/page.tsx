"use client";

import { use, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useBallotResolve } from "@/lib/hooks";
import type { BallotRaceResult, CandidacySummary } from "@/lib/types";

const POSITION_TYPE_KO: Record<string, string> = {
  mayor: "시장",
  governor: "도지사",
  district_mayor: "구청장",
  county_head: "군수",
  city_head: "시장",
  assembly_metro: "광역의원",
  assembly_local: "기초의원",
  superintendent: "교육감",
  education_director: "교육감",
};

function positionLabel(type: string): string {
  return POSITION_TYPE_KO[type] ?? type;
}

function CandidateCard({
  candidacy,
  selected,
  onToggle,
}: {
  candidacy: CandidacySummary;
  selected: boolean;
  onToggle: (id: string) => void;
}) {
  return (
    <div
      className={`rounded-xl border-2 p-4 transition ${
        selected
          ? "border-blue-500 bg-blue-50"
          : "border-slate-200 bg-white hover:border-slate-300"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          {candidacy.candidate_number !== null && (
            <span className="mb-1 inline-block rounded-md bg-slate-100 px-2 py-0.5 text-xs font-bold text-slate-600">
              기호 {candidacy.candidate_number}번
            </span>
          )}
          <p className="font-semibold text-slate-900">후보 ID: {candidacy.person_id.slice(0, 8)}…</p>
          <p className="mt-0.5 text-xs text-slate-500">상태: {candidacy.status}</p>
        </div>
        <div className="flex flex-col gap-2">
          <button
            onClick={() => onToggle(candidacy.id)}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
              selected
                ? "bg-blue-600 text-white"
                : "border border-slate-200 text-slate-600 hover:bg-slate-50"
            }`}
          >
            {selected ? "✓ 선택됨" : "비교"}
          </button>
          <Link
            href={`/candidate/${candidacy.id}`}
            className="rounded-lg border border-slate-200 px-3 py-1.5 text-center text-xs font-semibold text-slate-600 hover:bg-slate-50"
          >
            상세보기
          </Link>
        </div>
      </div>
    </div>
  );
}

function RaceSection({
  result,
  selectedIds,
  onToggle,
}: {
  result: BallotRaceResult;
  selectedIds: Set<string>;
  onToggle: (id: string) => void;
}) {
  return (
    <section className="rounded-2xl border border-slate-100 bg-white p-6 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-900">
            {positionLabel(result.race.position_type)}
          </h3>
          <p className="text-sm text-slate-500">
            {result.race.seat_count}명 선출 · 후보 {result.candidacies.length}명
          </p>
        </div>
      </div>

      {result.candidacies.length === 0 ? (
        <p className="text-sm text-slate-400">등록된 후보가 없습니다.</p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2">
          {result.candidacies.map((c) => (
            <CandidateCard
              key={c.id}
              candidacy={c}
              selected={selectedIds.has(c.id)}
              onToggle={onToggle}
            />
          ))}
        </div>
      )}
    </section>
  );
}

export default function BallotPage({
  params,
}: {
  params: Promise<{ districtId: string }>;
}) {
  const { districtId } = use(params);
  const router = useRouter();
  const [address, setAddress] = useState("");
  const [resolved, setResolved] = useState<{
    districtName: string;
    races: BallotRaceResult[];
  } | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const { mutate, isPending, isError } = useBallotResolve();

  function toggleCandidate(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  function handleSearch() {
    if (!address.trim()) return;
    mutate(address.trim(), {
      onSuccess(data) {
        setResolved({
          districtName: data.district.name_ko,
          races: data.races,
        });
      },
    });
  }

  const districtLabel = resolved?.districtName ?? `선거구 ${districtId.slice(0, 8)}…`;

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
          투표지 확인
        </p>
        <h1 className="mt-1 text-3xl font-black text-slate-900">{districtLabel}</h1>
        <p className="mt-2 text-slate-500">
          주소를 다시 입력하여 선거구 정보를 불러오세요.
        </p>
      </div>

      <div className="mb-8 flex gap-3">
        <input
          type="text"
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          placeholder="주소 입력 (예: 서울특별시 마포구 합정동)"
          className="flex-1 rounded-xl border border-slate-200 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
        />
        <button
          onClick={handleSearch}
          disabled={isPending}
          className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-bold text-white transition hover:bg-blue-500 disabled:opacity-50"
        >
          {isPending ? "검색 중…" : "검색"}
        </button>
      </div>

      {isError && (
        <p className="mb-6 rounded-xl bg-red-50 p-4 text-sm text-red-600">
          주소를 찾을 수 없습니다. 정확한 도로명 주소나 지번 주소를 입력해주세요.
        </p>
      )}

      {selectedIds.size >= 2 && (
        <div className="mb-6 flex items-center justify-between rounded-xl border border-blue-200 bg-blue-50 p-4">
          <p className="text-sm font-semibold text-blue-800">
            {selectedIds.size}명의 후보를 선택했습니다
          </p>
          <button
            className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-bold text-white hover:bg-blue-500"
            onClick={() =>
              router.push(
                `/compare?ids=${Array.from(selectedIds).join(",")}`
              )
            }
          >
            비교하기
          </button>
        </div>
      )}

      {resolved ? (
        <div className="flex flex-col gap-6">
          {resolved.races.length === 0 ? (
            <p className="text-slate-500">해당 선거구에 등록된 선거가 없습니다.</p>
          ) : (
            resolved.races.map((r) => (
              <RaceSection
                key={r.race.id}
                result={r}
                selectedIds={selectedIds}
                onToggle={toggleCandidate}
              />
            ))
          )}
        </div>
      ) : (
        <div className="rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center">
          <p className="text-4xl">🗳️</p>
          <p className="mt-4 text-lg font-semibold text-slate-700">주소를 입력해주세요</p>
          <p className="mt-2 text-sm text-slate-400">
            위의 검색창에 주소를 입력하면 투표지 정보를 확인할 수 있습니다.
          </p>
        </div>
      )}
    </div>
  );
}
