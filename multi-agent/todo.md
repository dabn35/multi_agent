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

우선 순위: 입력 파서 → 태깅 API → 저장 → 분석 → 처방 → 검토
