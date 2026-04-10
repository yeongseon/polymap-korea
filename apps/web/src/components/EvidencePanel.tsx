"use client";

import { useQuery } from "@tanstack/react-query";
import { getSource } from "@/lib/api";
import type { ClaimRead, PromiseRead } from "@/lib/types";

interface EvidencePanelProps {
  claim?: ClaimRead;
  promise?: PromiseRead;
  onClose: () => void;
  isOpen: boolean;
}

const CLAIM_TYPE_KO: Record<string, string> = {
  official_fact: "공식 사실",
  sourced_claim: "출처 확인",
  opinion: "의견",
  disputed: "논쟁 중",
  ai_summary: "AI 요약",
};

const CLAIM_TYPE_COLORS: Record<string, string> = {
  official_fact: "bg-blue-100 text-blue-800",
  sourced_claim: "bg-green-100 text-green-800",
  opinion: "bg-slate-100 text-slate-800",
  disputed: "bg-red-100 text-red-800",
  ai_summary: "bg-purple-100 text-purple-800",
};

export function EvidencePanel({
  claim,
  promise,
  onClose,
  isOpen,
}: EvidencePanelProps) {
  const sourceIds = Array.from(
    new Set(
      [promise?.source_doc_id, claim?.source_doc_id].filter(
        (value): value is string => Boolean(value)
      )
    )
  );
  const { data: sources, isLoading, isError } = useQuery({
    queryKey: ["sources", sourceIds],
    queryFn: () => Promise.all(sourceIds.map((id) => getSource(id))),
    enabled: sourceIds.length > 0,
  });

  if (!isOpen || (!claim && !promise)) return null;

  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm md:hidden"
        onClick={onClose}
        aria-hidden="true"
      />

      <aside
        className={`
          fixed bottom-0 left-0 right-0 z-50 max-h-[70vh] overflow-y-auto rounded-t-2xl bg-white shadow-2xl
          md:bottom-auto md:right-0 md:top-0 md:h-screen md:max-h-full md:w-96 md:rounded-l-2xl md:rounded-r-none
          transition-transform duration-300
        `}
        role="complementary"
        aria-label="근거 상세 패널"
      >
        <div className="sticky top-0 flex items-center justify-between border-b border-slate-100 bg-white/95 px-5 py-4 backdrop-blur-sm">
          <h2 className="text-base font-bold text-slate-900">근거 상세</h2>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition"
            aria-label="패널 닫기"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="p-5 space-y-5">
          {promise && <PromiseDetail promise={promise} />}
          {claim && <ClaimDetail claim={claim} />}
          <SourceDetails
            isLoading={isLoading}
            isError={isError}
            sources={sources ?? []}
            hasRequestedSources={sourceIds.length > 0}
          />
        </div>
      </aside>
    </>
  );
}

function SourceDetails({
  hasRequestedSources,
  isError,
  isLoading,
  sources,
}: {
  hasRequestedSources: boolean;
  isError: boolean;
  isLoading: boolean;
  sources: Array<{
    id: string;
    title: string;
    url: string | null;
    publisher: string;
    published_at: string | null;
    doc_type: string;
  }>;
}) {
  return (
    <section className="space-y-3 rounded-2xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-bold text-slate-900">출처 문서</h3>
        {hasRequestedSources && (
          <span className="text-[11px] font-medium uppercase tracking-[0.2em] text-slate-400">
            provenance
          </span>
        )}
      </div>

      {!hasRequestedSources && (
        <p className="text-sm text-slate-500">연결된 출처 문서가 아직 없습니다.</p>
      )}

      {isLoading && (
        <div className="space-y-2">
          {[0, 1].map((item) => (
            <div key={item} className="animate-pulse rounded-xl bg-white p-3">
              <div className="h-4 w-3/4 rounded bg-slate-200" />
              <div className="mt-2 h-3 w-1/2 rounded bg-slate-200" />
            </div>
          ))}
        </div>
      )}

      {!isLoading && isError && (
        <p className="text-sm text-red-600">출처 문서를 불러오지 못했습니다.</p>
      )}

      {!isLoading && !isError && hasRequestedSources && sources.length === 0 && (
        <p className="text-sm text-slate-500">확인 가능한 출처 문서가 없습니다.</p>
      )}

      {!isLoading && !isError && sources.length > 0 && (
        <ul className="space-y-3">
          {sources.map((source) => (
            <li key={source.id} className="rounded-xl bg-white p-3 shadow-sm ring-1 ring-slate-200">
              <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-400">
                {source.doc_type}
              </p>
              {source.url ? (
                <a
                  href={source.url}
                  target="_blank"
                  rel="noreferrer"
                  className="mt-1 block text-sm font-semibold text-blue-700 hover:text-blue-600 hover:underline"
                >
                  {source.title}
                </a>
              ) : (
                <p className="mt-1 text-sm font-semibold text-slate-900">{source.title}</p>
              )}
              <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500">
                <span>{source.publisher}</span>
                {source.published_at && (
                  <span>{new Date(source.published_at).toLocaleDateString("ko-KR")}</span>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function PromiseDetail({ promise }: { promise: PromiseRead }) {
  return (
    <div className="space-y-4">
      <div>
        <span className="mb-2 inline-block rounded-full bg-green-100 px-3 py-1 text-xs font-bold text-green-700">
          공약
        </span>
        {promise.category && (
          <span className="ml-2 inline-block rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
            {promise.category}
          </span>
        )}
      </div>

      <div>
        <h3 className="text-lg font-bold text-slate-900">{promise.title}</h3>
      </div>

      {promise.body && (
        <div>
          <p className="text-sm leading-relaxed text-slate-700 whitespace-pre-wrap">
            {promise.body}
          </p>
        </div>
      )}

      <div className="rounded-xl bg-slate-50 p-4 space-y-2">
        <div className="flex justify-between text-xs">
          <span className="font-medium text-slate-500">순서</span>
          <span className="text-slate-700">{promise.sort_order}</span>
        </div>
        {promise.source_doc_id && (
          <div className="flex justify-between text-xs">
            <span className="font-medium text-slate-500">출처 문서 ID</span>
            <span className="truncate max-w-[180px] text-slate-700 font-mono text-xs">
              {promise.source_doc_id.slice(0, 8)}…
            </span>
          </div>
        )}
        <div className="flex justify-between text-xs">
          <span className="font-medium text-slate-500">등록일</span>
          <span className="text-slate-700">
            {new Date(promise.created_at).toLocaleDateString("ko-KR")}
          </span>
        </div>
      </div>
    </div>
  );
}

function ClaimDetail({ claim }: { claim: ClaimRead }) {
  const typeColorClass =
    CLAIM_TYPE_COLORS[claim.claim_type] ?? "bg-slate-100 text-slate-800";
  const typeLabel = CLAIM_TYPE_KO[claim.claim_type] ?? claim.claim_type;

  return (
    <div className="space-y-4">
      <div>
        <span
          className={`inline-block rounded-full px-3 py-1 text-xs font-bold ${typeColorClass}`}
        >
          {typeLabel}
        </span>
      </div>

      <div>
        <p className="text-sm leading-relaxed text-slate-800 whitespace-pre-wrap">
          {claim.content}
        </p>
      </div>

      {claim.excerpt && (
        <blockquote className="border-l-4 border-amber-400 pl-4">
          <p className="text-sm italic leading-relaxed text-slate-600">
            &ldquo;{claim.excerpt}&rdquo;
          </p>
        </blockquote>
      )}

      <div className="rounded-xl bg-slate-50 p-4 space-y-2">
        <div className="flex justify-between text-xs">
          <span className="font-medium text-slate-500">출처 문서 ID</span>
          <span className="truncate max-w-[180px] text-slate-700 font-mono text-xs">
            {claim.source_doc_id.slice(0, 8)}…
          </span>
        </div>
        <div className="flex justify-between text-xs">
          <span className="font-medium text-slate-500">등록일</span>
          <span className="text-slate-700">
            {new Date(claim.created_at).toLocaleDateString("ko-KR")}
          </span>
        </div>
      </div>
    </div>
  );
}
