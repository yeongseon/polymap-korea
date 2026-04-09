export function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-slate-50">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-bold text-slate-800">
              폴리맵<span className="text-blue-600">코리아</span>
            </p>
            <p className="mt-1 text-xs text-slate-500">
              2026 지방선거 유권자 정보 탐색 서비스
            </p>
          </div>
          <div className="text-xs leading-relaxed text-slate-500">
            <p>폴리맵 코리아는 특정 후보를 추천하지 않습니다.</p>
            <p>본 서비스는 공개 데이터를 기반으로 운영됩니다.</p>
          </div>
        </div>
        <p className="mt-6 text-center text-xs text-slate-400">
          © 2026 폴리맵코리아. 선거 정보는 선거관리위원회 공식 자료를 기준으로 합니다.
        </p>
      </div>
    </footer>
  );
}
