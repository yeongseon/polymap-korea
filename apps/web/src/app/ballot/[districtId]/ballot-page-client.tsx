"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { getBallotByDistrict } from "@/lib/api";
import { useBallotResolve, useCandidacy } from "@/lib/hooks";
import type { BallotRaceResult, BallotResolveResponse, CandidacySummary } from "@/lib/types";

const POSITION_TYPE_KO: Record<string, string> = {
  mayor: "시장",
  governor: "도지사",
  council_member: "기초의원",
  superintendent: "교육감",
  proportional_council: "비례대표의원",
};

const STATUS_KO: Record<string, string> = {
  registered: "등록",
  withdrawn: "사퇴",
  disqualified: "무효",
  elected: "당선",
  defeated: "낙선",
};

function positionLabel(type: string): string {
  return POSITION_TYPE_KO[type] ?? type;
}

function EnrichedCandidateCard({
  candidacy,
  selected,
  onToggle,
}: {
  candidacy: CandidacySummary;
  selected: boolean;
  onToggle: (id: string) => void;
}) {
  const { data: detail } = useCandidacy(candidacy.id);

  const name = detail?.person.name_ko ?? `후보 ${candidacy.candidate_number ?? ""}`;
  const partyName = detail?.party?.name_ko;
  const partyColor = detail?.party?.color_hex ?? "#8b5cf6";

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
          <p className="font-semibold text-slate-900">{name}</p>
          <div className="mt-1 flex flex-wrap gap-1.5">
            {partyName && (
              <span
                className="rounded-full px-2 py-0.5 text-xs font-medium text-white"
                style={{ backgroundColor: partyColor }}
              >
                {partyName}
              </span>
            )}
            <span className="text-xs text-slate-500">
              {STATUS_KO[candidacy.status] ?? candidacy.status}
            </span>
          </div>
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
            <EnrichedCandidateCard
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

export function BallotPageClient({ districtId }: { districtId: string }) {
  const router = useRouter();
  const [address, setAddress] = useState("");
  const [ballotData, setBallotData] = useState<BallotResolveResponse | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [loadError, setLoadError] = useState<string | null>(null);
  const { mutate, isPending, isError } = useBallotResolve();

  useEffect(() => {
    let cancelled = false;

    async function loadBallot() {
      try {
        const cached = sessionStorage.getItem(`ballot:${districtId}`);
        if (cached) {
          if (!cancelled) {
            setBallotData(JSON.parse(cached) as BallotResolveResponse);
            setLoadError(null);
          }
          return;
        }
      } catch {
      }

      try {
        const data = await getBallotByDistrict(districtId);
        if (!cancelled) {
          setBallotData(data);
          setLoadError(null);
        }
      } catch (error) {
        if (!cancelled) {
          setLoadError(
            error instanceof Error ? error.message : "선거구 정보를 불러올 수 없습니다."
          );
        }
      }
    }

    void loadBallot();

    return () => {
      cancelled = true;
    };
  }, [districtId]);

  const toggleCandidate = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }, []);

  function handleSearch() {
    if (!address.trim()) return;
    mutate(address.trim(), {
      onSuccess(data) {
        setBallotData(data);
        setLoadError(null);
        try {
          sessionStorage.setItem(`ballot:${data.district.id}`, JSON.stringify(data));
        } catch {
        }
        if (data.district.id !== districtId) {
          router.push(`/ballot/${data.district.id}`);
        }
      },
    });
  }

  const districtLabel = ballotData?.district.name_ko ?? `선거구 ${districtId.slice(0, 8)}…`;

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
          투표지 확인
        </p>
        <h1 className="mt-1 text-3xl font-black text-slate-900">{districtLabel}</h1>
        {!ballotData && !loadError && (
          <p className="mt-2 text-slate-500">주소를 입력하여 선거구 정보를 불러오세요.</p>
        )}
      </div>

      <div className="mb-8 flex gap-3">
        <label htmlFor="ballot-address-input" className="sr-only">
          주소 입력
        </label>
        <input
          id="ballot-address-input"
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

      {loadError && (
        <p className="mb-6 rounded-xl bg-red-50 p-4 text-sm text-red-600">{loadError}</p>
      )}

      {selectedIds.size >= 2 && (
        <div className="mb-6 flex items-center justify-between rounded-xl border border-blue-200 bg-blue-50 p-4">
          <p className="text-sm font-semibold text-blue-800">
            {selectedIds.size}명의 후보를 선택했습니다
          </p>
          <button
            className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-bold text-white hover:bg-blue-500"
            onClick={() =>
              router.push(`/compare?ids=${Array.from(selectedIds).join(",")}`)
            }
          >
            비교하기
          </button>
        </div>
      )}

      {ballotData ? (
        <div className="flex flex-col gap-6">
          {ballotData.races.length === 0 ? (
            <p className="text-slate-500">해당 선거구에 등록된 선거가 없습니다.</p>
          ) : (
            ballotData.races.map((r) => (
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
          <p className="mt-4 text-lg font-semibold text-slate-700">투표지 정보 불러오는 중</p>
          <p className="mt-2 text-sm text-slate-400">
            위의 검색창에 주소를 입력하면 투표지 정보를 확인할 수 있습니다.
          </p>
        </div>
      )}
    </div>
  );
}
