"use client";

import { useIssues } from "@/lib/hooks";
import { IssuesClient } from "./issues-client";

export default function IssuesPage() {
  const { data, isLoading, isError } = useIssues();

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-20 text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="mt-4 text-slate-500">이슈 목록을 불러오는 중…</p>
      </div>
    );
  }

  return <IssuesClient initialIssues={isError ? null : data ?? []} />;
}
