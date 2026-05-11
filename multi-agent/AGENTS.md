# AGENTS.md

이 파일은 이 저장소에서 참고하는 에이전트 설계 규칙과 프로젝트 요건을 담습니다.

프로젝트 경로: C:\agenticai\multi-agent

## 프로젝트

- 이름: skin care tool
- 핵심 컨셉: 마케팅이 아닌, 데이터 증거로 피부의 인과관계를 밝히는 AI
- 목표: 사용자의 개인 피부 기록과 외부 환경·제품 데이터를 자동으로 결합해 인과관계 분석과 예측 기반 처방을 제공
- 기본 실행: `python run_agents.py`
- 기본 작업 파일: `run_agents.py`
- 입력 예시 파일: `sample_records.txt`
- 주요 출력 파일: `output_analysis.md`, `prescriptions.md`, `data_export.json`

## 에이전트 역할

1. 데이터 수집·태깅 에이전트: 사용자가 남긴 간단한 텍스트 입력을 받아 장소/시간 기반 환경 API(기상, 미세먼지, 자외선 등)를 호출해 자동으로 컨텍스트 태그를 추가합니다.
2. 기록 저장 에이전트: `사용자 상태 + 사용 제품 + 환경 태그`를 하나의 레코드로 데이터베이스에 적재합니다.
3. 분석 에이전트: 누적 데이터를 바탕으로 통계·상관분석과 인과추정(간단한 규칙 기반·회귀·인과추론 프로세스)을 실행합니다.
4. 처방/예측 에이전트: 예측 기반 예방 루틴과 알림을 생성합니다(예: 특정 환경에서 피해야 할 제품 추천).
5. 검토자 에이전트: 분석 결과의 신뢰도(데이터 수량, 편향 가능성)를 검토하고 사용자에게 불확실성을 명확히 표시합니다.

## 작업 방식

1. 작업 전 계획을 작성하고 작은 단위로 파일을 수정합니다.
2. 외부 API 키는 절대 리포지토리에 하드코딩하지 않습니다. `.env` 또는 비밀 관리자를 사용하세요。
3. 새로운 외부 패키지 추가는 최소화하고, 필요 시 `requirements.txt`에 기록합니다。
4. 변경 후 실행 커맨드와 샘플 입력/출력을 보고합니다。

## 금지

- 불필요한 패키지 설치
- API 키 하드코딩
- 사용자 동의 없이 민감한 개인 데이터를 외부로 전송
- Playwright MCP 연결 (CLI 확인용만 허용)

## 실행 예시(개발)

```bash
python run_agents.py --sample sample_records.txt
```

## 피부 상태 측정 매커니즘 (요약)

- **시각적 정량화 (Objective Data)**: 사용자가 촬영한 얼굴 사진에서 홍조도(RGB 기반), 트러블 개수/면적, 모공 상태, 유분(광택) 등 지표를 추출하는 이미지분석 에이전트를 둡니다. 촬영 시점의 기온/습도 데이터와 결합해 환경-피부 상호작용 추적을 지원합니다.
- **사용자 피어드백 (Subjective Data)**: 챗봇이나 앱 인터페이스에서 1~5점 슬라이더로 감각(따가움, 가려움, 속당김 등)을 수집하여 이미지 기반 지표와 비교·보정합니다.
- **맥락 태그 (Contextual Data)**: 생리 주기, 수면 시간, 음주, 스트레스, 운동 등 버튼형 태그로 빠르게 수집하며, 이 태그는 분석 에이전트의 공변량으로 사용됩니다.

## 데이터 구조 제안 (Data Architecture)

각 레코드는 하루 단위의 이벤트로 저장됩니다. 주요 필드는 다음과 같습니다.

- `environment` (X1): `temperature`, `humidity`, `pm25`, `uv_index` (날씨 API 자동 수집)
- `exposures` (X2): `products_used` (성분 리스트), `cleanses_per_day`, `mask_used` 등 (사용자 입력/영수증 인식)
- `internal` (X3): `sleep_hours`, `menstrual_phase`, `stress_level`, `exercise` (앱 연동/선택형 태그)
- `visual_metrics` (Y_obj): `redness_score`, `lesion_count`, `lesion_area`, `pore_score`, `shine_score` (사진 분석)
- `subjective_scores` (Y_subj): 슬라이더 1~5 점수들
- `meta`: `user_id`, `timestamp`, `photo_uri`, `location`

이 구조는 분석 에이전트에서 `X` → `Y` 회귀/인과모형 및 시계열 비교(예: 전일 대비 홍조 변화%)에 바로 투입될 수 있도록 설계되었습니다.

필요하면 `docs/`에 추가 설계 문서를 작성하고, 에이전트별 테스트 케이스를 `tests/`에 둡니다。
