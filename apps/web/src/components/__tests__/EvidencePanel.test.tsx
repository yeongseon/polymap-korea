import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { EvidencePanel } from "../EvidencePanel";

const getSourceMock = vi.fn();

vi.mock("@/lib/api", () => ({
  getSource: (id: string) => getSourceMock(id),
}));

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}

describe("EvidencePanel", () => {
  it("renders nothing when closed", () => {
    const { container } = render(<EvidencePanel isOpen={false} onClose={vi.fn()} />, {
      wrapper,
    });

    expect(container.innerHTML).toBe("");
  });

  it("renders nothing when no claim or promise", () => {
    const { container } = render(<EvidencePanel isOpen={true} onClose={vi.fn()} />, {
      wrapper,
    });

    expect(container.innerHTML).toBe("");
  });

  it("shows promise detail when promise is provided", () => {
    const promise = {
      id: "p1",
      candidacy_id: "c1",
      title: "교통 확충",
      body: "지하철 연장",
      category: "교통",
      issue_id: null,
      source_doc_id: null,
      sort_order: 1,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    };

    render(<EvidencePanel isOpen={true} promise={promise} onClose={vi.fn()} />, { wrapper });

    expect(screen.getByText("교통 확충")).toBeTruthy();
    expect(screen.getByText("지하철 연장")).toBeTruthy();
  });

  it("shows claim detail when claim is provided", () => {
    getSourceMock.mockResolvedValue({
      id: "s1",
      kind: "news_article",
      title: "기사",
      url: null,
      published_at: "2026-01-01T00:00:00Z",
      is_poll_result: false,
      content_hash: null,
      raw_s3_key: null,
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
      deleted_at: null,
    });

    const claim = {
      id: "cl1",
      candidacy_id: "c1",
      source_doc_id: "s1",
      claim_type: "sourced_claim",
      content: "지하철 노선 추가 예정",
      excerpt: "관련 발언 인용",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-01T00:00:00Z",
    };

    render(<EvidencePanel isOpen={true} claim={claim} onClose={vi.fn()} />, { wrapper });

    expect(screen.getByText("지하철 노선 추가 예정")).toBeTruthy();
  });
});
