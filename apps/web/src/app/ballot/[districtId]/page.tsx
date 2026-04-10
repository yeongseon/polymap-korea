import { demoDistrictIds } from "@/lib/demo-params";
import { BallotPageClient } from "./ballot-page-client";

export function generateStaticParams() {
  return demoDistrictIds.map((districtId) => ({ districtId }));
}

export default function BallotPage({
  params,
}: {
  params: { districtId: string };
}) {
  return <BallotPageClient districtId={params.districtId} />;
}
