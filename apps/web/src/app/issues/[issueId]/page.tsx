import { demoIssueIds } from "@/lib/demo-params";
import { IssueDetailClient } from "./issue-detail-client";

export function generateStaticParams() {
  return demoIssueIds.map((issueId) => ({ issueId }));
}

export default function IssueDetailPage({
  params,
}: {
  params: { issueId: string };
}) {
  return <IssueDetailClient issueId={params.issueId} />;
}
