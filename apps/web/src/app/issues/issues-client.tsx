"use client";

import Link from "next/link";
import type { IssueTreeNode } from "@/lib/types";

function IssueNode({
  issue,
  depth,
}: {
  issue: IssueTreeNode;
  depth: number;
}) {
  return (
    <div>
      <Link
        href={`/issues/${issue.id}`}
        className={`group flex items-center gap-2 rounded-xl px-4 py-3 transition hover:bg-blue-50 ${
          depth === 0
            ? "border border-slate-200 bg-white shadow-sm"
            : "border border-slate-100 bg-slate-50"
        }`}
        style={{ marginLeft: depth * 20 }}
      >
        <div
          className={`h-2 w-2 flex-shrink-0 rounded-full ${
            depth === 0 ? "bg-blue-500" : "bg-slate-300"
          }`}
        />
        <span
          className={`flex-1 font-medium transition group-hover:text-blue-700 ${
            depth === 0 ? "text-slate-900" : "text-sm text-slate-600"
          }`}
        >
          {issue.name}
        </span>
        {issue.children.length > 0 && (
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">
            {issue.children.length}개 하위
          </span>
        )}
        <svg
          className="h-4 w-4 text-slate-400 group-hover:text-blue-500 transition"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 5l7 7-7 7"
          />
        </svg>
      </Link>

      {issue.children.length > 0 && (
        <div className="mt-1.5 space-y-1.5 pl-5 border-l-2 border-slate-100 ml-4">
          {issue.children.map((child) => (
            <IssueNode key={child.id} issue={child} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export function IssuesClient({
  initialIssues,
}: {
  initialIssues: IssueTreeNode[] | null;
}) {
  if (!initialIssues) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <p className="text-4xl">😕</p>
        <p className="mt-4 text-lg font-semibold text-slate-700">
          이슈 목록을 불러올 수 없습니다
        </p>
        <p className="mt-2 text-sm text-slate-400">
          잠시 후 다시 시도해주세요.
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <div className="mb-8">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">
          정책 이슈
        </p>
        <h1 className="mt-1 text-3xl font-black text-slate-900">이슈 목록</h1>
        <p className="mt-2 text-slate-500">
          주요 정책 이슈별로 후보들의 입장을 확인하세요.
        </p>
      </div>

      {initialIssues.length === 0 ? (
        <div className="rounded-2xl border-2 border-dashed border-slate-200 p-12 text-center">
          <p className="text-4xl">📋</p>
          <p className="mt-4 text-lg font-semibold text-slate-700">
            등록된 이슈가 없습니다
          </p>
          <p className="mt-2 text-sm text-slate-400">
            이슈가 등록되면 여기에 표시됩니다.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {initialIssues.map((issue) => (
            <IssueNode key={issue.id} issue={issue} depth={0} />
          ))}
        </div>
      )}
    </div>
  );
}
