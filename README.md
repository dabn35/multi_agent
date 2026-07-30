# S.E.E. v2 (간단 README)

이 저장소는 "Skin & Eating Habits Experience" Streamlit 앱과 간단한 AI 보조 추천 기능을 포함합니다.

## 주요 파일
- `my_agent.py` : Streamlit 앱 메인
- `streamlit_app.py` : Streamlit 진입점(간단 래퍼)
- `ai_recs.py` : LLM 기반 추천 모듈 (환경변수로 활성화 가능)
- `.env` : 프로젝트 설정 및 review 함수(테스트용으로 파이썬 코드 포함)
- `output_user_guide.md`, `review_report.md` : 샘플 출력/리뷰 보고서

## 실행 방법 (Windows)
1. 가상환경 활성화
```powershell
& .\.venv\Scripts\Activate.ps1
```
2. 의존성 설치
```powershell
pip install -r requirements.txt
```
3. Streamlit 실행
```powershell
streamlit run streamlit_app.py
```

## 실행 방법 (macOS / Linux)
1. 가상환경 활성화
```bash
source .venv/bin/activate
```
2. 의존성 설치
```bash
pip install -r requirements.txt
```
3. Streamlit 실행
```bash
streamlit run streamlit_app.py
```

## Python 보조 실행 방법
- 테스트 스크립트 실행
```bash
python tests/run_review_test.py
```

## 역할 분리
- 분석 에이전트(Analyzer): `ai_recs.analyze_with_llm` — 최근 식습관과 피부 데이터를 해석하고 추천 컨텍스트를 생성
- 추천 에이전트(Recommender): `ai_recs.recommend_with_llm` — 분석 결과와 피부 상태를 바탕으로 케어 루틴 추천 생성
- 검토 에이전트(Reviewer): `ai_recs.review_recommendation` — 추천 결과를 다시 확인하여 모순이나 누락을 점검
- 안내문 에이전트(Explainer): `ai_recs.write_user_guide` — 추천 결과를 바탕으로 사용자 맞춤 안내문을 생성

## 외부 API 실패 시 동작
- `ai_recs`와 `.env`에 구현된 LLM 호출은 환경변수(`OPENAI_API_KEY`, `GROQ_API_KEY`)가 없거나 호출이 실패하면 규칙 기반 폴백을 사용합니다.
- 따라서 외부 API 실패 여부와 상관없이 Streamlit 앱은 기본 기능(기록·통계·규칙 기반 추천)으로 동작합니다.

## 기타
- 이 저장소는 과제용 MVP이며, LLM 프롬프트, 캐시, 로깅, A/B 테스트를 추가하면 더 견고해집니다.
