"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const NAV_LINKS = [
  { href: "/", label: "홈" },
  { href: "/issues", label: "이슈" },
  { href: "/search", label: "검색" },
  { href: "/about", label: "소개" },
];

export function Header() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6">
        <Link href="/" className="flex items-center gap-2">
          <span className="text-lg font-black tracking-tight text-slate-900">
            폴리맵<span className="text-blue-600">코리아</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-1 sm:flex">
          {NAV_LINKS.map(({ href, label }) => (
            <Link
              key={label}
              href={href}
              className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                pathname === href
                  ? "bg-blue-50 text-blue-700"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>

        <button
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 sm:hidden"
          onClick={() => setMenuOpen((o) => !o)}
          aria-label={menuOpen ? "메뉴 닫기" : "메뉴 열기"}
          aria-expanded={menuOpen}
        >
          {menuOpen ? (
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-slate-100 bg-white px-4 pb-3 sm:hidden">
          {NAV_LINKS.map(({ href, label }) => (
            <Link
              key={label}
              href={href}
              className={`block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                pathname === href
                  ? "bg-blue-50 text-blue-700"
                  : "text-slate-600 hover:bg-slate-50"
              }`}
              onClick={() => setMenuOpen(false)}
            >
              {label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}
