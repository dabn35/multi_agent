# GEMINI.md

이 저장소의 공통 작업 규칙은 루트의 `AGENTS.md`에 있습니다.

작업을 시작할 때 먼저 `AGENTS.md`, `context.md`, `todo.md`를 읽고 따르세요.

요약:

- 기본 실행 명령(개발): `python run_agents.py`
- 파일 수정 전에는 간단한 계획을 작성합니다.
- 한 번에 많은 파일을 바꾸지 않습니다. 작은 단위로 진행하세요.
- 외부 패키지는 최소화하고 추가 시 `requirements.txt`에 기록합니다.
- API 키는 `.env`에 보관하고 리포지토리에 직접 포함하지 않습니다.
- Playwright는 CLI 확인용으로만 사용합니다.

## 피부 상태 측정 관련 지침

- 개발 초기에는 사진·슬라이더·태그 수집 파이프라인을 간단히 구현해 빠르게 데이터 포맷을 확보하세요.
- 사진 데이터는 로컬에 암호화하여 저장하고, 외부 모델 연동 시 사용자의 명시적 동의를 받습니다.
- 분석에 투입되는 주요 필드는 `environment`, `exposures`, `internal`, `visual_metrics`, `subjective_scores`, `meta` 형식을 따릅니다.

이 문서는 `skin care tool` 개발 규칙과 실행 관행을 요약합니다.
