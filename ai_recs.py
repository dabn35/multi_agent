import os
import logging
import json
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# 설정
USE_LLM_RECS = os.getenv("USE_LLM_RECS", "False").lower() in ("1", "true", "yes")
OPENAI_REVIEW_MODEL = os.getenv("OPENAI_REVIEW_MODEL", "gpt-5-mini")
OPENAI_ANALYSIS_MODEL = os.getenv("OPENAI_ANALYSIS_MODEL", OPENAI_REVIEW_MODEL)
OPENAI_GUIDE_MODEL = os.getenv("OPENAI_GUIDE_MODEL", OPENAI_REVIEW_MODEL)


def _safe_json_load(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def _call_openai(messages: list, model: str, max_tokens: int = 400, temperature: float = 0):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise RuntimeError('OPENAI_API_KEY가 설정되지 않음')

    import openai
    openai.api_key = openai_api_key

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )

    if isinstance(response, dict):
        choices = response.get('choices')
        if choices:
            return choices[0].get('message', {}).get('content') or choices[0].get('text', '')

    return getattr(response.choices[0].message, 'content', '')


def _build_analysis_prompt(context: dict) -> str:
    today = context.get('today', {})
    last7 = context.get('last7', {})
    food_stats = last7.get('food_stats', {})
    skin_stats = last7.get('skin_stats', {})

    prompt = (
        "당신은 고급 피부 케어 분석 에이전트입니다. 식습관과 피부 상태의 상관관계를 분석하는 전문가입니다.\n"
        "아래 정보를 바탕으로 깊이 있는 분석을 제공하세요.\n\n"
        "분석 시 고려사항:\n"
        "1. 음식 카테고리와 피부 증상의 연관성 분석\n"
        "   - 기름진 음식(고기/구이류, 패스트푸드)과 유분/트러블의 관계\n"
        "   - 당분(음료, 사탕, 초콜릿)과 염증/여드름의 관계\n"
        "   - 건강식(샐러드, 해산물)과 피부 개선의 관계\n"
        "2. 복합 증상의 근본 원인 파악\n"
        "3. 최근 추세와 패턴 분석\n\n"
        "입력 정보:\n"
        f"오늘 피부 상태: {today.get('skin_conditions')}\n"
        f"최근 7일 음식 섭취: {food_stats}\n"
        f"최근 7일 피부 증상 패턴: {skin_stats}\n\n"
        "JSON 출력 형식 (반드시 이 형식만 사용):\n"
        "{\n"
        "  \"summary\": \"종합적인 분석 요약 (2-3문장)\",\n"
        "  \"patterns\": [\"패턴1\", \"패턴2\", \"패턴3\"],\n"
        "  \"advice_context\": \"음식과 피부의 관계를 바탕으로 한 추천 근거\"\n"
        "}\n"
        "응답은 반드시 JSON 형식만 출력하세요."
    )
    return prompt


def _build_recommendation_prompt(context: dict) -> str:
    today = context.get('today', {})
    last7 = context.get('last7', {})
    analysis = context.get('analysis', {})

    prompt = (
        "당신은 고급 피부 케어 전문가 에이전트입니다. 사용자의 식습관과 피부 상태를 고려하여 "
        "맞춤형 스킨케어 처방을 제시합니다.\n\n"
        "처방 시 고려사항:\n"
        "1. 식습관 개선 제안 포함 (음식 선택 가이드)\n"
        "2. 단계별 스킨케어 루틴 (아침/저녁 구분)\n"
        "3. 제품 선택 시 주의사항\n"
        "4. 케어 기간 및 기대 효과\n"
        "5. 식습관 개선 후 예상 결과\n"
        "6. 상황별 대응 방법 (응급 상황, 악화 시 등)\n\n"
        "입력 정보:\n"
        f"오늘 피부 상태: {today.get('skin_conditions')}\n"
        f"최근 7일 요약: {last7.get('report', '')}\n"
        f"음식 섭취 패턴: {last7.get('food_stats', {})}\n"
        f"피부 증상 추이: {last7.get('skin_stats', {})}\n"
        f"분석 결과: {analysis.get('summary', '')}\n"
        f"주요 패턴: {analysis.get('patterns', [])}\n\n"
        "JSON 출력 형식 (2-3개의 처방):\n"
        "{\n"
        "  \"recommendations\": [\n"
        "    {\n"
        "      \"type\": \"처방 종류 (고보습/진정/트러블케어/유분조절 등)\",\n"
        "      \"ingredients\": [\"성분1\", \"성분2\"],\n"
        "      \"routine\": \"상세한 사용 방법 (아침/저녁/언제 사용할지)\",\n"
        "      \"reason\": \"이 처방이 필요한 이유 (음식과 피부의 관계 포함)\",\n"
        "      \"food_advice\": \"식습관 개선 제안\",\n"
        "      \"confidence\": 0.8,\n"
        "      \"warning\": \"주의사항 또는 피해야 할 습관\"\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "반드시 한국어로 작성하고, JSON 형식만 출력하세요."
    )
    return prompt


def _build_review_prompt(context: dict, recommendations: list) -> str:
    today = context.get('today', {})
    last7 = context.get('last7', {})
    analysis = context.get('analysis', {})

    prompt = (
        "당신은 피부 케어 검토 에이전트입니다. 아래 사용자 정보와 추천 결과를 검토하고,"
        " 추천이 입력 정보와 일치하는지, 누락된 요소는 없는지, 과도한 권장이나 위험한 표현은 없는지 확인하세요."
        " 결과를 JSON으로 출력하세요. 키는 `valid`, `notes` 입니다.\n\n"
        "입력 정보:\n"
        f"오늘 피부 상태: {today.get('skin_conditions')}\n"
        f"최근 7일 음식 통계: {last7.get('food_stats', {})}\n"
        f"최근 7일 피부 증상: {last7.get('skin_stats', {})}\n"
        f"AI 분석 결과: {analysis.get('summary', '')}\n"
        f"추천 근거: {analysis.get('advice_context', '')}\n"
        f"추천 결과: {recommendations}\n\n"
        "출력 예시:\n"
        "{\n  \"valid\": true,\n  \"notes\": \"추천이 전체적으로 입력과 일치합니다.\"\n}\n"
        "응답은 반드시 위 JSON 형식만 출력하세요."
    )
    return prompt


def _build_guide_prompt(context: dict, recommendations: list) -> str:
    today = context.get('today', {})
    analysis = context.get('analysis', {})

    prompt = (
        "당신은 피부 케어 안내문 작성 에이전트입니다. 아래 정보를 바탕으로 사용자가 당장 실행할 수 있는"
        " 한국어 맞춤형 스킨케어 안내문을 작성하세요. 출력은 JSON으로, 키는 `guide` 입니다.\n\n"
        "입력 정보:\n"
        f"오늘 피부 상태: {today.get('skin_conditions')}\n"
        f"AI 분석 요약: {analysis.get('summary', '')}\n"
        f"추천 결과: {recommendations}\n\n"
        "출력 예시:\n"
        "{\n  \"guide\": \"오늘은 ...\"\n}\n"
        "응답은 반드시 위 JSON 형식만 출력하세요."
    )
    return prompt


def _fallback_analysis(context: dict):
    today = context.get('today', {})
    last7 = context.get('last7', {})
    report = last7.get('report', '') or '최근 7일 요약 정보가 부족합니다.'
    skin_conditions = today.get('skin_conditions', [])
    patterns = []
    if skin_conditions:
        patterns = [f"{symptom} 관련 케어 필요" for symptom in skin_conditions[:3]]
    return {
        'summary': report,
        'patterns': patterns,
        'advice_context': '기본 규칙 분석을 사용하여 추천 준비'
    }


def _fallback_recommendation(skin_conditions: list, food_stats: dict = None, skin_stats: dict = None):
    """식습관과 피부 상태를 고려한 개선된 폴백 처방"""
    if not skin_conditions:
        return {'recommendations': [{
            'type': '기본 케어',
            'ingredients': ['클렌징', '토닝', '모이스처'],
            'routine': '아침저녁 매일 클렌징-토닝-모이스처 기본 3스텝 루틴을 진행하세요.',
            'reason': '피부 상태 정보가 없으므로 가장 안전한 기본 케어를 권장합니다.',
            'food_advice': '균형 잡힌 식단 유지 (채소, 단백질, 수분)',
            'confidence': 0.6,
            'warning': '기본 권장 사항입니다. 피부 변화를 관찰하며 조정하세요.'
        }]}

    recommendations = []
    
    # 식습관 분석
    has_fatty_food = any(key in str(food_stats or {}).lower() for key in ['고기', '구이', '패스트푸드', '분식'])
    has_sweet_food = any(key in str(food_stats or {}).lower() for key in ['음료', '초콜릿', '사탕', '아이스'])
    has_healthy_food = any(key in str(food_stats or {}).lower() for key in ['샐러드', '다이어트', '해산물'])
    
    dry_keywords = ['속당김', '전체적인 극건조', '각질 들뜸']
    sensitive_keywords = ['홍조/붉어짐', '따가움/가려움', '화끈거리는 열감']
    trouble_keywords = ['좁쌀 여드름', '화농성 여드름', '결절성(단단한 아픈 여드름)']
    oily_keywords = ['유분 과다(개기름)', '화이트헤드/블랙헤드', '모공 확장']

    # 1. 수분/건조 관련
    if any(cond in skin_conditions for cond in dry_keywords):
        recommendations.append({
            'type': '고보습 및 장벽 강화 케어',
            'ingredients': ['히알루론산', '세라마이드', '스쿠알란'],
            'routine': (
                '아침: 토너 - 에센스 - 히알루론산 세럼 - 보습 크림 순서로 진행. '
                '저녁: 클렌징 - 토너 - 에센스 - 세라마이드 나이트 크림 - 오일 마무리. '
                '주 2-3회 수분팩 추가.'
            ),
            'reason': '수분 부족과 장벽 약화 징후가 있어 집중 보습이 필수적입니다. 세라마이드와 히알루론산 조합으로 효과를 높입니다.',
            'food_advice': (
                '수분 섭취 증가 (하루 2L 이상). '
                '견과류(아몬드, 아보카도), 해산물(연어) 등 오메가-3 음식 추가. '
                '카페인과 알코올 최소화.'
            ),
            'confidence': 0.9,
            'warning': '너무 많은 제품 사용은 피하세요. 1-2주 간격으로 하나씩 추가 적응 시킵니다. 건조함이 악화되면 전문가 상담 필요.'
        })

    # 2. 민감/자극 관련
    if any(cond in skin_conditions for cond in sensitive_keywords):
        recommendations.append({
            'type': '진정 및 진정 강화 케어',
            'ingredients': ['시카(병풀)', '어성초', '판테놀', 'β-글루칸'],
            'routine': (
                '아침: 순한 클렌징 - 약산성 토너 - 시카 에센스 - 진정 크림. '
                '저녁: 미지라인 클렌징 - 토너 - 어성초 앰플 - 판테놀 크림 - 시카 밤. '
                '자극 받은 부위에 시카 스팟 에센스 집중 사용.'
            ),
            'reason': (
                '홍조와 따가움 증상이 있어 진정과 진정이 매우 중요합니다. '
                '시카, 어성초, 판테놀은 피부 진정의 3대 성분입니다.'
            ),
            'food_advice': (
                '자극적인 음식 피하기 (맵고 자극적인 양념, 카페인, 술). '
                '항염 음식 증가 (베리류, 녹차, 생강, 강황). '
                '충분한 수면 (밤 11시 전 수면, 7시간 이상).'
            ),
            'confidence': 0.85,
            'warning': '자극적인 스크럽, 필링 제품 완전 중단. 마사지는 부드럽게만 진행하세요. 증상 악화 시 즉시 전문가 상담.'
        })

    # 3. 트러블/염증 관련
    if any(cond in skin_conditions for cond in trouble_keywords):
        recommendations.append({
            'type': '항염 및 유분 조절 케어',
            'ingredients': ['살리실산(BHA)', '아하(AHA)', '티트리', '나이아신아마이드'],
            'routine': (
                '아침: 저자극 클렌징 - BHA 토너 - 나이아신아마이드 세럼 - 라이트 젤크림. '
                '저녁: 젤 클렌징 - AHA 토너 (격일) 또는 토너 - 티트리 스팟 에센스 - 논코메도제닉 젤 크림. '
                '주 1-2회 클레이 팩.'
            ),
            'reason': (
                f'여드름과 염증 증상이 있어 각질 제거와 유분 조절이 필수입니다. '
                f'{"기름진 음식이 많이 섭취되어 " if has_fatty_food else ""}'
                f'이를 관리해야 합니다.'
            ),
            'food_advice': (
                '유분진 음식 최소화 (튀김, 고기, 버터). '
                '당분 줄이기 (단 음료, 과자, 빵 등). '
                '잡곡, 채소, 유산균 음식 증가. 수분 섭취 충분히.'
            ),
            'confidence': 0.87,
            'warning': (
                '처음에는 반응성이 있을 수 있으므로 천천히 시작 (일주일 1-2회 사용). '
                '과도한 필링 제품 사용 금지. 필요시 스팟 케어로만 사용하세요. '
                '3주 이상 개선 없으면 피부과 상담 권장.'
            )
        })

    # 4. 유분/모공 관련
    if any(cond in skin_conditions for cond in oily_keywords):
        recommendations.append({
            'type': '유분 조절 및 모공 관리 케어',
            'ingredients': ['나이아신아마이드', '살리실산(BHA)', '비타민C', '아로에'],
            'routine': (
                '아침: 거품 클렌징 - BHA 토너 - 나이아신아마이드 세럼 - 라이트 수분 젤 크림. '
                '저녁: 클렌징 - BHA 에센스 - 비타민C 세럼 - 라이트 크림. '
                '일주일 2회 클레이 팩 (T-존 집중).'
            ),
            'reason': (
                f'과다한 유분 분비로 모공 확장과 염증이 있습니다. '
                f'{"기름진 음식 섭취가 많아 " if has_fatty_food else ""}'
                '이를 조절하며 피지 관리 제품 사용이 필요합니다.'
            ),
            'food_advice': (
                '유분진 음식 제한 (튀김, 고기, 치즈, 버터). '
                '기름기 없는 단백질 (흰살 생선, 두부, 계란흰자). '
                '섬유소 많은 음식 (채소, 과일, 현미). 아로에음료 시도.'
            ),
            'confidence': 0.82,
            'warning': (
                '과도한 세정은 더 많은 유분 분비를 유발합니다. 하루 2회만 클렌징. '
                '매끈함을 원해 강한 제품 사용은 자제하세요. 결국 피부 자극으로 더 악화될 수 있습니다.'
            )
        })

    # 5. 좋은 피부 유지
    if '피부 상태 아주 좋음' in skin_conditions and not recommendations:
        recommendations.append({
            'type': '유지 및 예방 케어',
            'ingredients': ['토너', '에센스', '라이트 크림', '자외선 차단제'],
            'routine': (
                '아침: 순한 클렌징 - 토너 - 에센스 - 라이트 크림 - SPF 50+ 자외선 차단제 필수. '
                '저녁: 순한 클렌징 - 토너 - 에센스 - 나이트 크림. '
                '주 1회 가벼운 시트팩.'
            ),
            'reason': '현재 피부 상태가 우수하므로, 큰 변화를 주지 않으면서 유지 관리가 가장 중요합니다.',
            'food_advice': '현재의 좋은 식습관 유지. 항산화 음식(베리, 다크초콜릿, 녹차) 꾸준히 섭취. 수분 섭취 유지.',
            'confidence': 0.95,
            'warning': '과도한 제품 사용은 오히려 피부를 악화시킬 수 있습니다. 지금의 루틴을 유지하세요.'
        })

    # 기본 케어 (특수 증상 없을 때)
    if not recommendations:
        recommendations.append({
            'type': '기본 밸런스 케어',
            'ingredients': ['토너', '에센스', '크림', '자외선 차단제'],
            'routine': '아침: 클렌징 - 토너 - 에센스 - 크림 - 자외선 차단제. 저녁: 클렌징 - 토너 - 에센스 - 크림.',
            'reason': '특별한 피부 징후가 없으므로 기본적이고 안정적인 케어 루틴을 권장합니다.',
            'food_advice': '균형 잡힌 식단 유지. 물 충분히 마시기. 규칙적인 운동.',
            'confidence': 0.7,
            'warning': '피부 변화를 관찰하면서 필요에 따라 조정하세요.'
        })

    return {'recommendations': recommendations}


def _fallback_review(recommendations: list):
    if not recommendations:
        return {'valid': False, 'notes': '추천이 없습니다. 기본 폴백을 사용했습니다.'}
    return {'valid': True, 'notes': '추천이 입력 정보와 대체로 일치합니다. 추가 검토가 필요할 수 있습니다.'}


def _fallback_guide(recommendations: list):
    if not recommendations:
        return '추천 정보가 없어 맞춤 안내문을 생성할 수 없습니다.'
    lines = []
    for rec in recommendations[:2]:
        lines.append(f"{rec.get('type')}은 {rec.get('reason', '기본 케어')}\n루틴: {rec.get('routine', '')}")
    return ' '.join(lines)


def analyze_with_llm(context: dict):
    if not USE_LLM_RECS:
        logging.info('USE_LLM_RECS is False — falling back to analysis rules')
        return _fallback_analysis(context)

    try:
        prompt = _build_analysis_prompt(context)
        text = _call_openai([{'role': 'user', 'content': prompt}], model=OPENAI_ANALYSIS_MODEL, max_tokens=300)
        data = _safe_json_load(text)
        if data:
            return data
        logging.warning('LLM 분석 결과 JSON 파싱 실패 — 폴백 사용')
    except Exception as e:
        logging.warning('analyze_with_llm 실패: %s', e)

    return _fallback_analysis(context)


def recommend_with_llm(context: dict):
    if not USE_LLM_RECS:
        logging.info('USE_LLM_RECS is False — falling back to rules')
        skin_conditions = context.get('today', {}).get('skin_conditions', [])
        food_stats = context.get('last7', {}).get('food_stats', {})
        skin_stats = context.get('last7', {}).get('skin_stats', {})
        return _fallback_recommendation(skin_conditions, food_stats, skin_stats)

    try:
        prompt = _build_recommendation_prompt(context)
        text = _call_openai([{'role': 'user', 'content': prompt}], model=OPENAI_REVIEW_MODEL, max_tokens=600)
        data = _safe_json_load(text)
        if data and isinstance(data.get('recommendations'), list):
            return data
        logging.warning('LLM 추천 결과 JSON 파싱 실패 — 폴백 사용')
    except Exception as e:
        logging.warning('recommend_with_llm 실패: %s', e)

    skin_conditions = context.get('today', {}).get('skin_conditions', [])
    food_stats = context.get('last7', {}).get('food_stats', {})
    skin_stats = context.get('last7', {}).get('skin_stats', {})
    return _fallback_recommendation(skin_conditions, food_stats, skin_stats)


def review_recommendation(context: dict, recommendations: list):
    if not USE_LLM_RECS:
        logging.info('USE_LLM_RECS is False — falling back to review rules')
        return _fallback_review(recommendations)

    try:
        prompt = _build_review_prompt(context, recommendations)
        text = _call_openai([{'role': 'user', 'content': prompt}], model=OPENAI_REVIEW_MODEL, max_tokens=250)
        data = _safe_json_load(text)
        if data and 'valid' in data:
            return data
        logging.warning('LLM 검토 결과 JSON 파싱 실패 — 폴백 사용')
    except Exception as e:
        logging.warning('review_recommendation 실패: %s', e)

    return _fallback_review(recommendations)


def write_user_guide(context: dict, recommendations: list):
    if not USE_LLM_RECS:
        logging.info('USE_LLM_RECS is False — falling back to guide rules')
        return _fallback_guide(recommendations)

    try:
        prompt = _build_guide_prompt(context, recommendations)
        text = _call_openai([{'role': 'user', 'content': prompt}], model=OPENAI_GUIDE_MODEL, max_tokens=250)
        data = _safe_json_load(text)
        if data and 'guide' in data:
            return data['guide']
        logging.warning('LLM 안내문 결과 JSON 파싱 실패 — 폴백 사용')
    except Exception as e:
        logging.warning('write_user_guide 실패: %s', e)

    return _fallback_guide(recommendations)



