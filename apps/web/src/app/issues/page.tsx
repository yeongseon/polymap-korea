import { getIssuesISR } from "@/lib/api";
import { IssuesClient } from "./issues-client";

export const revalidate = 300;

export default async function IssuesPage() {
  let issues;
  try {
    issues = await getIssuesISR();
  } catch {
    issues = null;
  }

  return <IssuesClient initialIssues={issues} />;
}
