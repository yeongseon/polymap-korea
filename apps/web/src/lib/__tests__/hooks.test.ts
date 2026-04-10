import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import { createElement } from "react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

const getCompareBundleMock = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");

  return {
    ...actual,
    getCompareBundle: (ids: string[]) => getCompareBundleMock(ids),
  };
});

import { useCompare } from "../hooks";

function wrapper({ children }: { children: ReactNode }) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return createElement(QueryClientProvider, { client }, children);
}

describe("useCompare", () => {
  it("does not fetch when fewer than 2 ids", () => {
    const { result } = renderHook(() => useCompare(["one"]), { wrapper });

    expect(result.current.isFetching).toBe(false);
    expect(getCompareBundleMock).not.toHaveBeenCalled();
  });

  it("deduplicates and caps at 4 ids", async () => {
    getCompareBundleMock.mockResolvedValue({
      candidacies: [],
      comparison: { candidacy_ids: ["a", "b", "c", "d"], by_issue: {} },
    });

    const { result } = renderHook(() => useCompare(["a", "a", "b", "c", "d", "e"]), {
      wrapper,
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(getCompareBundleMock).toHaveBeenCalledWith(["a", "b", "c", "d"]);
  });
});
