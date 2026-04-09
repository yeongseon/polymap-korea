"use client";

import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useBallotResolve } from "@/lib/hooks";

const ELECTION_DATE = new Date("2026-06-03T00:00:00+09:00");

function useDDay() {
  const [days, setDays] = useState<number | null>(null);

  useEffect(() => {
    function calc() {
      const now = new Date();
      const diff = ELECTION_DATE.getTime() - now.getTime();
      setDays(Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24))));
    }
    calc();
    const id = setInterval(calc, 60_000);
    return () => clearInterval(id);
  }, []);

  return days;
}

export default function HomePage() {
  const router = useRouter();
  const dday = useDDay();
  const [address, setAddress] = useState("");
  const { mutate, isPending, isError, error } = useBallotResolve();

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!address.trim()) return;
    mutate(address.trim(), {
      onSuccess(data) {
        try {
          sessionStorage.setItem(
            `ballot:${data.district.id}`,
            JSON.stringify(data)
          );
        } catch {
          // sessionStorage may be unavailable
        }
        router.push(`/ballot/${data.district.id}`);
      },
    });
  }

  return (
    <div className="flex flex-col">
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 px-4 py-20 sm:py-32">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-20"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 50%, #3b82f6 0%, transparent 50%), radial-gradient(circle at 80% 20%, #1d4ed8 0%, transparent 40%)",
          }}
        />

        <div className="relative mx-auto max-w-3xl text-center">
          {dday !== null && (
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-400/30 bg-blue-500/10 px-4 py-1.5">
              <span className="h-2 w-2 animate-pulse rounded-full bg-blue-400" />
              <span className="text-sm font-semibold text-blue-300">
                {dday === 0 ? "오늘이 선거일입니다!" : `D-${dday} · 2026년 6월 3일 지방선거`}
              </span>
            </div>
          )}

          <h1 className="text-4xl font-black tracking-tight text-white sm:text-6xl">
            2026 지방선거
            <span className="mt-2 block text-blue-400">투표지 미리보기</span>
          </h1>

          <p className="mt-6 text-lg leading-relaxed text-slate-300 sm:text-xl">
            주소를 입력하면 내 선거구의 후보자 정보를 확인할 수 있습니다.
            <br className="hidden sm:block" />
            공약과 이슈를 비교하고, 현명한 선택을 해보세요.
          </p>

          <form onSubmit={handleSubmit} className="mt-10 flex flex-col gap-3 sm:flex-row sm:gap-0">
            <label htmlFor="address-input" className="sr-only">
              주소 입력
            </label>
            <input
              id="address-input"
              type="text"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="예: 서울특별시 마포구 합정동"
              className="flex-1 rounded-xl border border-white/20 bg-white/10 px-5 py-4 text-white placeholder-slate-400 backdrop-blur-sm transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-400/50 sm:rounded-r-none sm:rounded-l-xl"
            />
            <button
              type="submit"
              disabled={isPending || !address.trim()}
              className="rounded-xl bg-blue-500 px-8 py-4 font-bold text-white transition hover:bg-blue-400 disabled:cursor-not-allowed disabled:opacity-50 sm:rounded-l-none sm:rounded-r-xl"
            >
              {isPending ? (
                <span className="flex items-center gap-2">
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  검색 중
                </span>
              ) : (
                "내 투표지 확인"
              )}
            </button>
          </form>

          {isError && (
            <p className="mt-3 text-sm text-red-400">
              {error instanceof Error ? error.message : "주소를 찾을 수 없습니다. 다시 시도해주세요."}
            </p>
          )}

          <p className="mt-4 text-xs text-slate-500">
            본 서비스는 특정 후보를 추천하거나 지지하지 않습니다.
          </p>
        </div>
      </section>

      <section className="bg-white px-4 py-16 sm:py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="text-center text-2xl font-bold text-slate-900 sm:text-3xl">
            폴리맵코리아로 할 수 있는 것
          </h2>
          <div className="mt-12 grid gap-6 sm:grid-cols-3">
            {[
              {
                icon: "🗳️",
                title: "투표지 미리보기",
                desc: "내 주소 기반으로 실제 투표용지에 올라오는 후보자를 미리 확인하세요.",
              },
              {
                icon: "📋",
                title: "공약 비교",
                desc: "후보자별 공약을 이슈 카테고리별로 비교하고 차이점을 파악하세요.",
              },
              {
                icon: "🔍",
                title: "근거 확인",
                desc: "언론 보도와 공식 문서를 통해 후보자의 발언과 행적을 검증하세요.",
              },
            ].map(({ icon, title, desc }) => (
              <div
                key={title}
                className="rounded-2xl border border-slate-100 bg-slate-50 p-6 transition hover:border-blue-200 hover:bg-blue-50/50"
              >
                <span className="text-3xl">{icon}</span>
                <h3 className="mt-4 text-lg font-bold text-slate-900">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-slate-100 bg-slate-50 px-4 py-12">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-sm leading-relaxed text-slate-500">
            폴리맵코리아는 특정 정당이나 후보를 지지하지 않습니다.
            제공되는 모든 정보는 공개된 자료에 기반하며, 선거관리위원회 공식 자료를 우선합니다.
          </p>
        </div>
      </section>
    </div>
  );
}
