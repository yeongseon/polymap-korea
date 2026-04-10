"use client";

import Link from "next/link";
import { useIssue } from "@/lib/hooks";

export function IssueDetailClient({
  issueId,
}: {
  issueId: string;
}) {
  const { data: issue, isLoading, isError } = useIssue(issueId);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="mt-4 text-slate-500">이슈 정보를 불러오는 중…</p>
      </div>
    );
  }

  if (isError || !issue) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <p className="text-4xl">😕</p>
        <p className="mt-4 text-lg font-semibold text-slate-700">
          이슈를 찾을 수 없습니다
        </p>
        <p className="mt-2 text-sm text-slate-400">
          주소가 올바른지 확인하거나 이슈 목록으로 돌아가세요.
        </p>
        <Link
          href="/issues"
          className="mt-6 inline-block rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-bold text-white hover:bg-blue-500"
        >
          이슈 목록으로
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <div className="mb-6">
        <Link
          href="/issues"
          className="inline-flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700 transition"
        >
          <svg
            className="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
          이슈 목록
        </Link>
      </div>

      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
          정책 이슈
        </p>
        <h1 className="mt-1 text-3xl font-black text-slate-900">{issue.name}</h1>
        <p className="mt-1 text-xs text-slate-400 font-mono">/{issue.slug}</p>
      </div>

      {issue.description ? (
        <div className="mb-8 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-base leading-relaxed text-slate-700 whitespace-pre-wrap">
            {issue.description}
          </p>
        </div>
      ) : (
        <div className="mb-8 rounded-2xl border-2 border-dashed border-slate-200 p-8 text-center">
          <p className="text-sm text-slate-400">이슈 설명이 아직 없습니다.</p>
        </div>
      )}

      {issue.related_promises && issue.related_promises.length > 0 && (
        <section className="mb-8">
          <h2 className="mb-4 text-lg font-bold text-slate-900">
            관련 공약{" "}
            <span className="text-base font-normal text-slate-400">
              ({issue.related_promises.length}개)
            </span>
          </h2>
          <div className="flex flex-col gap-3">
            {issue.related_promises.map((rp) => (
              <Link
                key={rp.id}
                href={`/candidate/${rp.candidacy.id}`}
                className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:border-green-300 hover:shadow-md"
              >
                <p className="font-semibold text-slate-800">{rp.title}</p>
                <p className="mt-1 text-xs text-slate-500">
                  후보 상세 보기 →
                </p>
              </Link>
            ))}
          </div>
        </section>
      )}

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-base font-bold text-slate-800">이슈 정보</h2>
        <dl className="space-y-3">
          <div className="flex justify-between text-sm">
            <dt className="font-medium text-slate-500">이슈 슬러그</dt>
            <dd className="font-mono text-slate-700">{issue.slug}</dd>
          </div>
          {issue.parent_id && (
            <div className="flex justify-between text-sm">
              <dt className="font-medium text-slate-500">상위 이슈 ID</dt>
              <dd className="truncate max-w-[200px] font-mono text-xs text-slate-700">
                {issue.parent_id}
              </dd>
            </div>
          )}
          <div className="flex justify-between text-sm">
            <dt className="font-medium text-slate-500">등록일</dt>
            <dd className="text-slate-700">
              {new Date(issue.created_at).toLocaleDateString("ko-KR")}
            </dd>
          </div>
          <div className="flex justify-between text-sm">
            <dt className="font-medium text-slate-500">최근 업데이트</dt>
            <dd className="text-slate-700">
              {new Date(issue.updated_at).toLocaleDateString("ko-KR")}
            </dd>
          </div>
        </dl>
      </div>

      <div className="mt-6 rounded-2xl border border-slate-100 bg-slate-50 p-6">
        <p className="text-sm text-slate-500">
          이 이슈와 관련된 후보 공약 및 주장 정보는 후보 검색을 통해 확인할 수
          있습니다.
        </p>
        <Link
          href="/search"
          className="mt-3 inline-block rounded-xl bg-blue-600 px-5 py-2 text-sm font-bold text-white hover:bg-blue-500"
        >
          후보 검색하기
        </Link>
      </div>
    </div>
  );
}
