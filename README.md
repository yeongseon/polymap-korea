# 폴리맵 코리아 (PolyMap Korea)

> 2026 지방선거 유권자 정보 탐색 서비스

**"내 투표지에 누가 올라오지?"** — 주소를 입력하면 이번 선거의 모든 후보를 보여주고, 정당·경력·의정활동·공약·뉴스를 그래프와 비교 카드로 탐색하는 서비스입니다.

## 핵심 기능

1. **내 투표지 홈** — 주소 입력 → 선거별 투표지 스택 → 후보 카드
2. **후보자 관계 그래프** — 정당, 공직, 위원회, 공약, 뉴스 이슈를 1~2홉 그래프로 탐색
3. **공약 vs 기록 비교** — "말한 것"과 "실제로 한 것"을 같은 화면에서 비교
4. **이슈별 비교 보드** — 교통·주거·교육 등 주제별로 후보 공약과 기록 묶어 보기
5. **근거 패널** — 모든 노드/관계에 출처·수집 시각·원문 링크 표시

## 설계 원칙

- **사실/주장/AI요약 3층 분리** — Official Fact · Sourced Claim · AI Summary
- **출처가 보이는 근거 패널** — 모든 정보에 provenance 부착
- **선거법 안전장치** — 여론조사 금지기간, 후보자료 공개시한, 딥페이크 규제 준수

## 아키텍처

```
[Source Adapters] → [Raw Archive (S3/MinIO)] → [Parser/Extractor] → [Normalizer]
    → [Entity Resolver] → [Validation (Pydantic/SQL CHECK)]
    → [Curated Warehouse (PostgreSQL)] → [Search Index (OpenSearch)]
    → [REST API (FastAPI)] → [Frontend (Next.js 14)]
```

## 데이터 원천

| 계층 | 원천 | 용도 |
|------|------|------|
| 1차 | 선관위 OpenAPI (data.nec.go.kr) | 후보자, 선거구, 투개표, 공약 |
| 1차 | 선거통계시스템 (info.nec.go.kr) | 현재/역대 선거 통계 |
| 1차 | 정책공약마당 (policy.nec.go.kr) | 정당·후보 공약 PDF |
| 2차 | 국회사무처 OpenAPI (open.assembly.go.kr) | 의원정보, 표결, 회의록 |
| 3차 | 지방의회 (clik.nanet.go.kr) | 지방의원 의안, 회의록 |
| 4차 | BigKinds, 토론위 | 뉴스 메타, 토론 링크 |
| 보조 | 주소API, 브이월드 | 주소→선거구 매핑, 지도 |

## 기술 스택

- **수집/ETL**: Python, Prefect
- **저장**: PostgreSQL (curated), OpenSearch (search), MinIO (raw archive)
- **API**: FastAPI (REST + OpenAPI)
- **Frontend**: Next.js 14 + TypeScript + Cytoscape.js
- **Infra**: Docker Compose

## 개발 환경

```bash
make setup      # 의존성 설치 (uv, pnpm)
make dev-infra  # core 프로파일 시작 (PostgreSQL, MinIO, Prefect, API, Web, Pipeline)
make api        # API 서버 시작
make web        # 웹 프론트엔드 시작
make test       # 전체 테스트 실행
make lint       # 전체 린트 실행
```

## 선거 일정 (2026)

| 날짜 | 이벤트 |
|------|--------|
| 5월 14~15일 | 후보자 등록 |
| 5월 21일 | 공식 선거운동 시작 |
| 5월 28일 | 여론조사 공표 금지 시작 |
| 5월 29~30일 | 사전투표 |
| 6월 3일 | 선거일 |

## 라이선스

MIT License
