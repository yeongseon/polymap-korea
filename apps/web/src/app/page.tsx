export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-20">
      <div className="max-w-3xl rounded-3xl border border-slate-200 bg-white p-10 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-blue-600">
          2026 지방선거
        </p>
        <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900">폴리맵 코리아</h1>
        <p className="mt-6 text-lg leading-8 text-slate-600">
          주소 기반 투표지 확인, 후보자 프로필 탐색, 공약 비교, 근거 패널 제공을 위한 한국형
          선거 정보 서비스의 초기 프로젝트 셸입니다.
        </p>
        <div className="mt-8 rounded-2xl bg-slate-50 p-6 text-sm leading-7 text-slate-700">
          프론트엔드, API, 데이터 파이프라인, 계약 생성, 인프라 서비스 구성이 Issue #1에서
          정리되었습니다.
        </div>
      </div>
    </main>
  );
}
