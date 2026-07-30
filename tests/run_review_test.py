import runpy
import sys
from pathlib import Path

# .env 파일 경로 (파일에 Python 코드가 들어있음)
env_path = Path(__file__).resolve().parents[1] / '.env'
if not env_path.exists():
    print('.env 파일을 찾을 수 없습니다:', env_path)
    sys.exit(1)

# runpy로 실행하여 전역 네임스페이스 딕셔너리를 얻음
env_globals = runpy.run_path(str(env_path))

sample = (
    "안내문: 회의는 다음 주에 진행합니다.\n"
    "대상: 모든 직원\n"
    "제출물: 없음\n"
)

# review_guides 함수 호출
if 'review_guides' in env_globals:
    result = env_globals['review_guides'](sample)
    print('검토 결과:')
    print(result)
else:
    print('review_guides 함수가 .env에 정의되어 있지 않습니다.')
