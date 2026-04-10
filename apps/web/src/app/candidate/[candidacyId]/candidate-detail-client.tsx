"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useCandidacy } from "@/lib/hooks";
import { CandidateGraph } from "@/components/CandidateGraph";
import { EvidencePanel } from "@/components/EvidencePanel";
import type { ClaimRead, PromiseRead } from "@/lib/types";

type PanelContent =
  | { kind: "promise"; promise: PromiseRead }
  | { kind: "claim"; claim: ClaimRead }
  | null;

const BASE_PATH = "/polymap-korea";

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

const STATUS_COLORS: Record<string, string> = {
  registered: "bg-blue-100 text-blue-800",
  elected: "bg-emerald-100 text-emerald-800",
  withdrawn: "bg-slate-100 text-slate-600",
  disqualified: "bg-red-100 text-red-800",
  defeated: "bg-slate-100 text-slate-600",
};

const CLAIM_TYPE_BADGE: Record<string, string> = {
  official_fact: "bg-blue-100 text-blue-800",
  sourced_claim: "bg-green-100 text-green-800",
  opinion: "bg-slate-100 text-slate-800",
  disputed: "bg-red-100 text-red-800",
  ai_summary: "bg-purple-100 text-purple-800",
};

function withBasePath(src: string) {
  return src.startsWith("/") ? `${BASE_PATH}${src}` : src;
}

export function CandidateDetailClient({ candidacyId }: { candidacyId: string }) {
  const { data: candidacy, isLoading, isError } = useCandidacy(candidacyId);
  const [panelContent, setPanelContent] = useState<PanelContent>(null);

  function openPromisePanel(promise: PromiseRead) {
    setPanelContent({ kind: "promise", promise });
  }

  function openClaimPanel(claim: ClaimRead) {
    setPanelContent({ kind: "claim", claim });
  }

  function closePanel() {
    setPanelContent(null);
  }

  if (isLoading) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-20 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="mt-4 text-slate-500">후보 정보를 불러오는 중…</p>
      </div>
    );
  }

  if (isError || !candidacy) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-20 text-center">
        <p className="text-4xl">😕</p>
        <p className="mt-4 text-lg font-semibold text-slate-700">
          후보 정보를 찾을 수 없습니다
        </p>
        <p className="mt-2 text-sm text-slate-400">
          ID가 올바른지 확인하거나 이전 페이지로 돌아가세요.
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

  const statusLabel = STATUS_KO[candidacy.status] ?? candidacy.status;
  const statusColor =
    STATUS_COLORS[candidacy.status] ?? "bg-slate-100 text-slate-600";

  return (
    <div className="relative mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <div className="mb-6">
        <Link
          href="/"
          className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 transition"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          돌아가기
        </Link>
      </div>

      <div className="mb-8 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col gap-4 p-6 sm:flex-row sm:items-start sm:gap-6">
          {candidacy.person.photo_url ? (
            <div className="relative h-24 w-24 flex-shrink-0 overflow-hidden rounded-2xl bg-slate-100">
              <Image
                src={withBasePath(candidacy.person.photo_url)}
                alt={candidacy.person.name_ko}
                fill
                className="object-cover"
              />
            </div>
          ) : (
            <div className="flex h-24 w-24 flex-shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-400 to-blue-600 text-3xl font-black text-white">
              {candidacy.person.name_ko.slice(0, 1)}
            </div>
          )}

          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-2xl font-black text-slate-900 sm:text-3xl">
                {candidacy.person.name_ko}
              </h1>
              {candidacy.person.name_en && (
                <span className="text-sm text-slate-400">
                  ({candidacy.person.name_en})
                </span>
              )}
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              <span className={`rounded-full px-3 py-1 text-xs font-bold ${statusColor}`}>
                {statusLabel}
              </span>

              {candidacy.candidate_number !== null && (
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-700">
                  기호 {candidacy.candidate_number}번
                </span>
              )}

              {candidacy.party && (
                <span
                  className="rounded-full px-3 py-1 text-xs font-bold text-white"
                  style={{
                    backgroundColor: candidacy.party.color_hex ?? "#8b5cf6",
                  }}
                >
                  {candidacy.party.name_ko}
                </span>
              )}
            </div>

            <div className="mt-3 grid grid-cols-2 gap-x-6 gap-y-1 text-sm sm:grid-cols-3">
              <div>
                <span className="text-slate-500">공약 수</span>{" "}
                <span className="font-semibold text-slate-800">
                  {candidacy.promises.length}개
                </span>
              </div>
              <div>
                <span className="text-slate-500">관련 주장</span>{" "}
                <span className="font-semibold text-slate-800">
                  {candidacy.claims.length}건
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <section className="mb-8">
        <h2 className="mb-3 text-lg font-bold text-slate-900">관계 그래프</h2>
        <CandidateGraph
          candidacy={candidacy}
          onNodeClick={(node) => {
            if (node.type === "promise") {
              openPromisePanel(node.item);
            } else if (node.type === "claim") {
              openClaimPanel(node.item);
            }
          }}
        />
      </section>

      {candidacy.promises.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-4 text-lg font-bold text-slate-900">
            핵심 공약{" "}
            <span className="text-base font-normal text-slate-400">
              ({candidacy.promises.length}개)
            </span>
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {candidacy.promises.map((p, i) => (
              <button
                key={p.id}
                onClick={() => openPromisePanel(p)}
                className="group rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-green-300 hover:shadow-md"
              >
                <div className="mb-2 flex items-start justify-between gap-2">
                  <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-green-100 text-xs font-bold text-green-700">
                    {i + 1}
                  </span>
                  {p.category && (
                    <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
                      {p.category}
                    </span>
                  )}
                </div>
                <p className="font-semibold text-slate-800 group-hover:text-green-700 transition line-clamp-2">
                  {p.title}
                </p>
                {p.body && (
                  <p className="mt-1.5 text-xs leading-relaxed text-slate-500 line-clamp-3">
                    {p.body}
                  </p>
                )}
                <p className="mt-2 text-xs font-medium text-green-600 opacity-0 group-hover:opacity-100 transition">
                  근거 보기 →
                </p>
              </button>
            ))}
          </div>
        </section>
      )}

      {candidacy.claims.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-4 text-lg font-bold text-slate-900">
            관련 주장 및 검증{" "}
            <span className="text-base font-normal text-slate-400">
              ({candidacy.claims.length}건)
            </span>
          </h2>
          <div className="flex flex-col gap-3">
            {candidacy.claims.map((c) => {
              const badgeColor =
                CLAIM_TYPE_BADGE[c.claim_type] ?? "bg-slate-100 text-slate-800";
              return (
                <button
                  key={c.id}
                  onClick={() => openClaimPanel(c)}
                  className="group rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:border-amber-300 hover:shadow-md"
                >
                  <div className="mb-2 flex items-center gap-2">
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${badgeColor}`}
                    >
                      {CLAIM_TYPE_KO[c.claim_type] ?? c.claim_type}
                    </span>
                  </div>
                  <p className="text-sm leading-relaxed text-slate-700 line-clamp-3">
                    {c.content}
                  </p>
                  {c.excerpt && (
                    <p className="mt-2 border-l-2 border-amber-300 pl-3 text-xs italic text-slate-500 line-clamp-2">
                      &ldquo;{c.excerpt}&rdquo;
                    </p>
                  )}
                  <p className="mt-2 text-xs font-medium text-amber-600 opacity-0 group-hover:opacity-100 transition">
                    출처 보기 →
                  </p>
                </button>
              );
            })}
          </div>
        </section>
      )}

      <EvidencePanel
        promise={
          panelContent?.kind === "promise" ? panelContent.promise : undefined
        }
        claim={panelContent?.kind === "claim" ? panelContent.claim : undefined}
        onClose={closePanel}
        isOpen={panelContent !== null}
      />
    </div>
  );
}
