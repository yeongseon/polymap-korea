export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
      <div className="mb-10">
        <p className="text-sm font-semibold uppercase tracking-widest text-blue-600">서비스 소개</p>
        <h1 className="mt-2 text-4xl font-black text-slate-900">
          폴리맵<span className="text-blue-600">코리아</span>
        </h1>
        <p className="mt-4 text-lg leading-relaxed text-slate-600">
          2026년 지방선거를 앞두고, 유권자가 더 나은 선택을 할 수 있도록 돕는 정보 서비스입니다.
        </p>
      </div>

      <div className="flex flex-col gap-8">
        <section className="rounded-2xl border border-slate-100 bg-white p-6">
          <h2 className="text-xl font-bold text-slate-900">서비스 목적</h2>
          <div className="mt-4 flex flex-col gap-3 text-sm leading-relaxed text-slate-600">
            <p>
              폴리맵코리아는 지방선거 유권자가 자신의 선거구에서 어떤 후보를 선택할 수 있는지,
              각 후보의 공약이 무엇인지, 그리고 그 근거는 무엇인지를 쉽게 파악할 수 있도록 돕기 위해
              만들어졌습니다.
            </p>
            <p>
              주소를 입력하면 해당 지역의 선거구를 자동으로 파악하고, 출마한 후보와
              선거 정보를 한눈에 확인할 수 있습니다.
            </p>
          </div>
        </section>

        <section className="rounded-2xl border border-slate-100 bg-white p-6">
          <h2 className="text-xl font-bold text-slate-900">데이터 출처</h2>
          <ul className="mt-4 flex flex-col gap-3">
            {[
              { name: "중앙선거관리위원회", desc: "후보자 정보, 선거구 정보, 공약 데이터" },
              { name: "국가공간정보포털", desc: "선거구 지도 데이터 (GeoJSON)" },
              { name: "행정안전부 도로명주소 API", desc: "주소 → 선거구 변환" },
              { name: "언론 공개 자료", desc: "후보자 발언 및 이력 검증" },
            ].map(({ name, desc }) => (
              <li key={name} className="flex gap-3">
                <span className="mt-0.5 h-2 w-2 shrink-0 rounded-full bg-blue-500" />
                <div>
                  <p className="font-semibold text-slate-800">{name}</p>
                  <p className="text-sm text-slate-500">{desc}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-2xl border border-amber-100 bg-amber-50 p-6">
          <h2 className="text-xl font-bold text-amber-900">면책 조항</h2>
          <div className="mt-4 flex flex-col gap-2 text-sm leading-relaxed text-amber-800">
            <p>
              폴리맵코리아는 특정 정당, 후보, 정치 단체를 지지하거나 추천하지 않습니다.
            </p>
            <p>
              제공되는 정보는 공개된 데이터를 기반으로 하며, 오류나 누락이 있을 수 있습니다.
              공식적인 선거 정보는 반드시 중앙선거관리위원회 공식 사이트를 통해 확인하시기 바랍니다.
            </p>
            <p>
              이 서비스는 선거 결과에 영향을 주기 위한 목적으로 운영되지 않습니다.
            </p>
          </div>
        </section>

        <section className="rounded-2xl border border-slate-100 bg-white p-6">
          <h2 className="text-xl font-bold text-slate-900">개인정보 처리</h2>
          <div className="mt-4 flex flex-col gap-2 text-sm leading-relaxed text-slate-600">
            <p>
              폴리맵코리아는 사용자의 주소 정보를 저장하지 않습니다.
              입력된 주소는 선거구 조회 목적으로만 사용되며, 서버에 기록되지 않습니다.
            </p>
            <p>
              서비스 개선을 위한 익명의 사용 통계(페이지뷰 등)는 수집될 수 있습니다.
            </p>
          </div>
        </section>

        <section className="rounded-2xl border border-slate-100 bg-white p-6">
          <h2 className="text-xl font-bold text-slate-900">오픈소스</h2>
          <p className="mt-4 text-sm leading-relaxed text-slate-600">
            폴리맵코리아의 소스코드는 공개되어 있습니다. 오류 제보, 기여, 피드백은 GitHub를 통해
            제출할 수 있습니다.
          </p>
        </section>
      </div>
    </div>
  );
}
