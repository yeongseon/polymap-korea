import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Footer } from "@/components/Footer";

describe("Footer", () => {
  it("renders service disclaimer copy", () => {
    render(<Footer />);

    expect(screen.getByText(/2026 지방선거 유권자 정보 탐색 서비스/)).toBeInTheDocument();
    expect(screen.getByText(/특정 후보를 추천하지 않습니다/)).toBeInTheDocument();
  });
});
