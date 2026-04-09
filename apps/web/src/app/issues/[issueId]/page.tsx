import { getIssueISR } from "@/lib/api";
import { IssueDetailClient } from "./issue-detail-client";

export const revalidate = 300;

export default async function IssueDetailPage({
  params,
}: {
  params: Promise<{ issueId: string }>;
}) {
  const { issueId } = await params;

  let issue;
  try {
    issue = await getIssueISR(issueId);
  } catch {
    issue = null;
  }

  return <IssueDetailClient issue={issue} />;
}
