## Todo — skin care tool

프로젝트: skin care tool (C:\agenticai\multi-agent)

- [ ] 샘플 레코드 파일 준비 (`sample_records.txt`)
- [ ] 입력 파서 에이전트 구현: 상태 라벨(발적/가려움/트러블 등) 추출
- [ ] 컨텍스트 태깅 API 연동 에이전트: 위치→기상/미세먼지/자외선 호출
- [ ] 저장 에이전트: 레코드 적재(로컬 JSON/간단 DB)
- [ ] 분석 에이전트: 상관분석·간단 회귀·인과 신호 탐색 모듈
- [ ] 처방 에이전트: 예측 기반 예방 루틴 생성 및 알림 포맷
- [ ] 검토자 에이전트: 결과 신뢰도/데이터 요구량 리포트
- [ ] `run_agents.py`로 전체 워크플로우 호출 가능한 엔트리 포인트 작성
- [ ] `requirements.txt` 및 `.env.example` 업데이트
- [ ] 간단한 샘플 실행과 결과 출력(`output_analysis.md`, `prescriptions.md`)

추가 구현 항목 — 피부 상태 측정 파이프라인

- [ ] 이미지 분석 프로토타입: 사진에서 `redness_score`, `lesion_count`, `lesion_area`, `pore_score`, `shine_score` 추출 (간단한 OpenCV/컬러 분석 + 마스크 연산)
- [ ] 주관적 입력 UI: 챗봇/앱에 1~5점 슬라이더 추가 및 응답 저장
- [ ] 맥락 태그 인터페이스: `menstrual_phase`, `sleep_hours`, `alcohol`, `stress`, `exercise` 버튼형 태그 추가
- [ ] 데이터 스키마 구현: 하루 단위 레코드로 `environment`, `exposures`, `internal`, `visual_metrics`, `subjective_scores`, `meta` 필드를 저장하는 로컬 JSON/DB 레이어
- [ ] 분석 파이프라인 연결: 전일 대비 변화 계산, X→Y 회귀/상관 분석 모듈 연결


## 12주차 개선 항목 (주간 목표)

- [ ] 핵심 정보 추출 고도화: 제품·성분 네임엔티티 정규화, 문장 전체 컨텍스트 기반 추출 규칙 추가
- [ ] 분류 기준 안정화: 환경 클러스터링 알고리즘 도입 검토(간단한 규칙→임계값/가중치 적용) 및 반응군 라벨 정교화
- [ ] 결과 파일 저장: 분석 결과 및 리포트를 `output.md`(또는 `output_analysis.md`)로 포맷 저장 기능 추가
- [ ] 외부 도구 연동 결정: Groq API 및 타사 분석도구 도입 비용/이점 평가 및 결정(POC 테스트 항목 포함)
- [ ] 불확실성 표기: 입력에 명시되지 않은 내용을 단정하지 않도록 불확실성/가정 표기 검토 및 보고서 반영

우선 순위: 입력 파서 → 태깅 API → 저장 → 분석 → 처방 → 검토
