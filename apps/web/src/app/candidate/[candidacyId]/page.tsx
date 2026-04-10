import { demoCandidateIds } from "@/lib/demo-params";
import { CandidateDetailClient } from "./candidate-detail-client";

export function generateStaticParams() {
  return demoCandidateIds.map((candidacyId) => ({ candidacyId }));
}

export default function CandidateDetailPage({
  params,
}: {
  params: { candidacyId: string };
}) {
  return <CandidateDetailClient candidacyId={params.candidacyId} />;
}
