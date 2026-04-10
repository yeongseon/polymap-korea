import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { Header } from "@/components/Header";

vi.mock("next/navigation", () => ({
  usePathname: () => "/issues",
}));

describe("Header", () => {
  it("renders primary navigation", () => {
    render(<Header />);

    expect(screen.getByRole("link", { name: /폴리맵 코리아/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "이슈" })).toHaveAttribute("href", "/issues");
    expect(screen.getByRole("button", { name: "메뉴 열기" })).toBeInTheDocument();
  });
});
