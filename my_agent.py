import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import os
from ai_recs import (
    USE_LLM_RECS,
    analyze_with_llm,
    recommend_with_llm,
    review_recommendation,
    write_user_guide
)

# ═══════════════════════════════════════════════════════════════
# 설정 및 초기화
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="S.E.E. v2 - 피부 & 식습관 추적",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 데이터 디렉토리
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "daily_records.json"

# 식사 카테고리
MEAL_CATEGORIES = {
    '아침': ['한식 (일반)', '고기/구이류', '면류 (밀가루)', '패스트푸드/분식', '일식/해산물', '샐러드/다이어트식', '아시안/기타'],
    '점심': ['한식 (일반)', '고기/구이류', '면류 (밀가루)', '패스트푸드/분식', '일식/해산물', '샐러드/다이어트식', '아시안/기타'],
    '저녁': ['한식 (일반)', '고기/구이류', '면류 (밀가루)', '패스트푸드/분식', '일식/해산물', '샐러드/다이어트식', '아시안/기타'],
}

SNACK_CATEGORIES = ['과자/스낵류', '빵/케이크/구움과자', '아이스크림/빙수', '초콜릿/사탕/젤리', '음료 (가당)', '야식/안주류']

# 피부 상태 분류
SKIN_CONDITIONS = {
    '수분계열': ['속당김', '전체적인 극건조', '각질 들뜸'],
    '유분계열': ['유분 과다(개기름)', '화이트헤드/블랙헤드', '모공 확장'],
    '민감계열': ['홍조/붉어짐', '따가움/가려움', '화끈거리는 열감'],
    '트러블계열': ['좁쌀 여드름', '화농성 여드름', '결절성(단단한 아픈 여드름)'],
    '기타': ['안색 칙칙함', '피부 상태 아주 좋음'],
}

#본인이 가지고 있는 화장품 입력하면 추천 가능
PRODUCT_EXAMPLES = {
    '히알루론산': ['아이소이 히알루모이스트 앰플', '닥터자르트 시카페어 세럼'],
    '세라마이드': ['세타필 모이스처라이징 로션', '피지오겔 데일리 모이스처 크림'],
    '시카(병풀)': ['닥터자르트 시카페어 크림', '아벤느 시칼파트 밤 B5'],
    '어성초': ['숨37° 어성초 진정 토너', '이니스프리 어성초 수딩 젤'],
    '판테놀': ['메디힐 판테놀 크림', '스킨푸드 판테놀 수딩 젤'],
    '살리실산(BHA)': ['코스알엑스 BHA 블랙헤드 파워 리퀴드', '니오 딥 클렌징 토너'],
    '티트리': ['파파레서피 티트리 시카 밤', '더페이스샵 티트리 케어 토너'],
    '아하(AHA)': ['바닐라코 인텐시브 AHA 필링 토너', '닥터자르트 AHA/BHA 필링 패드'],
    '토너': ['아벤느 소르스 떼르말 토너', '피지오겔 데일리 모이스처 테라피 토너'],
    '에센스': ['아이오페 바이오 에센스', '헤라 셀 에센스'],
    '크림': ['라로슈포제 시카플라스트 밤', '피지오겔 데일리 모이스처 크림'],
    '클렌징': ['비오레 스킨 퍼펙트 클렌징 워터', '킨더마일드 저자극 클렌저'],
    '모이스처': ['세타필 모이스처라이징 로션', '아벤느 수딩 크림']
}

WEATHER_CITY = 'Seoul'

# CSS for toggle buttons and improved design
TOGGLE_BUTTON_CSS = """
<style>
:root {
    --primary-color: #D4A5A5;
    --secondary-color: #FFF9A6;
    --accent-color: #FFE66D;
    --text-dark: #2C3E50;
    --bg-light: #F8F9FA;
    --border-light: #E0E0E0;
}

/* 기본 배경 */
.stApp {
    background-color: #FFFFFF;
}

/* 토글 버튼 스타일 */
.toggle-btn {
    display: inline-block;
    padding: 10px 14px;
    margin: 5px;
    border: 2px solid #E0E0E0;
    border-radius: 8px;
    background-color: #FFFFFF;
    color: #5DADE2;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    user-select: none;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}

.toggle-btn:hover {
    border-color: #FFF9A6;
    background-color: #F5F5F5;
    box-shadow: 0 2px 6px rgba(78, 205, 196, 0.1);
    transform: translateY(-1px);
}

.toggle-btn.active {
    background-color: #FF6B9D;
    color: white;
    border-color: #FF6B9D;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(255, 107, 157, 0.2);
}

/* 버튼 스타일 */
.stButton > button {
    background-color: #F4B6C2;
    color: black;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    box-shadow: 0 2px 6px rgba(255, 107, 157, 0.15);
    transition: all 0.3s ease;
}


.stButton > button:hover {
    box-shadow: 0 4px 12px rgba(255, 107, 157, 0.25);
    transform: translateY(-1px);
}


.stButton > button[kind="secondary"] {
    background-color: #FFF9A6;
    color: ##5DADE2;
}


/* 체크박스 */
.stCheckbox {
    padding: 8px;
    border-radius: 6px;
}

/* 정보 박스들 */
.stInfo, .stSuccess, .stWarning {
    border-radius: 8px;
    padding: 12px !important;
}

/* 테이블 */
table {
    width: 100% !important;
    border-collapse: collapse !important;
}

thead {
    background-color: #FFB3D9 !important;
    color: #2C3E50 !important;
    font-weight: 700 !important;
}

tbody tr {
    background-color: #FFFFFF !important;
    border-bottom: 1px solid #E0E0E0 !important;
}

tbody tr:hover {
    background-color: #F5F5F5 !important;
}

/* 헤더 스타일 */
h1, h2, h3 {
    color: #2C3E50 !important;
}

h3 {
    color: #D4A5A5 !important;
}

</style>
"""

st.markdown(TOGGLE_BUTTON_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# 데이터 관리 함수
# ═══════════════════════════════════════════════════════════════
def load_all_records():
    """모든 기록 로드"""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_records(records):
    """기록 저장"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def get_date_key(date_obj):
    """날짜 객체를 문자열 키로 변환"""
    return date_obj.strftime('%Y-%m-%d')

def get_today_record(all_records, date_key):
    """특정 날짜의 기록 가져오기"""
    return all_records.get(date_key, {
        'breakfast': {},
        'lunch': {},
        'dinner': {},
        'snacks': {},
        'skin_conditions': []
    })


def reset_date_selection_state():
    """날짜가 바뀔 때 이전 선택을 초기화"""
    meal_names = ['아침', '점심', '저녁']
    for meal_name in meal_names:
        for key in (f"did_not_eat_{meal_name}", f"cat_{meal_name}", f"menu_{meal_name}"):
            if key in st.session_state:
                del st.session_state[key]

    for cat in SNACK_CATEGORIES:
        snack_key = f"snack_{cat}"
        if snack_key in st.session_state:
            del st.session_state[snack_key]

    for category in SKIN_CONDITIONS:
        session_key = f"skin_{category}"
        st.session_state[session_key] = set()


def load_record_into_session(today_record):
    """선택한 날짜의 저장된 기록을 세션 상태로 로드"""
    
    # 💡 데이터가 없을 때만 빈 딕셔너리로 초기화하고, 
    # 자기 자신을 호출하는 루프(Recursion)를 완전히 제거합니다.
    if today_record is None:
        today_record = {}

    meal_map = {'아침': 'breakfast', '점심': 'lunch', '저녁': 'dinner'}
    for meal_name, record_key in meal_map.items():
        saved = today_record.get(record_key, {})
        if saved.get('category') == '안 했음':
            st.session_state[f"did_not_eat_{meal_name}"] = True
        else:
            st.session_state[f"did_not_eat_{meal_name}"] = False
            if saved.get('category'):
                st.session_state[f"cat_{meal_name}"] = saved.get('category')
            st.session_state[f"menu_{meal_name}"] = saved.get('menu', '')

    for cat in SNACK_CATEGORIES:
        snack_entry = today_record.get('snacks', {}).get(cat, {})
        st.session_state[f"snack_{cat}"] = snack_entry.get('menu', '') if snack_entry else ''

    # 🚨 [핵심 수정] 불러온 데이터가 리스트나 세트가 아니라 None일 경우를 대비해 확실하게 안전장치를 만듭니다.
    raw_conditions = today_record.get('skin_conditions', [])
    saved_conditions = set(raw_conditions) if isinstance(raw_conditions, (list, set)) else set()
    
    for category, items in SKIN_CONDITIONS.items():
        st.session_state[f"skin_{category}"] = {item for item in items if item in saved_conditions}
        

def save_today_record(all_records, date_key, record):
    """특정 날짜의 기록 저장"""
    all_records[date_key] = record
    save_records(all_records)


def get_last_7_days_data(all_records):
    """최근 7일 데이터"""
    today = datetime.now().date()
    last_7_days = {}
    for i in range(7):
        date = today - timedelta(days=i)
        date_key = get_date_key(date)
        if date_key in all_records:
            last_7_days[date_key] = all_records[date_key]
    return last_7_days 


# ═══════════════════════════════════════════════════════════════
# 통계 및 분석 함수
# ═══════════════════════════════════════════════════════════════
def analyze_last_7_days(all_records):
    """지난 7일 분석 및 요약 리포트"""
    last_7_days = get_last_7_days_data(all_records)
    
    if not last_7_days:
        return None, None, None
    
    # 음식 카테고리 빈도
    food_categories = {}
    snack_categories = {}
    
    for date_key, record in last_7_days.items():
        for meal_key in ['breakfast', 'lunch', 'dinner']:
            if record.get(meal_key, {}).get('category'):
                cat = record[meal_key]['category']
                food_categories[cat] = food_categories.get(cat, 0) + 1
        
        for snack in record.get('snacks', {}).values():
            if snack and snack.get('category'):
                cat = snack['category']
                snack_categories[cat] = snack_categories.get(cat, 0) + 1
    
    # 피부 증상 빈도
    skin_symptoms = {}
    for date_key, record in last_7_days.items():

        if record is None:
            record = {}

    
        for symptom in record.get('skin_conditions', []):
            skin_symptoms[symptom] = skin_symptoms.get(symptom, 0) + 1
    
    # 리포트 생성
    report = generate_summary_report(food_categories, snack_categories, skin_symptoms)
    
    return (food_categories, snack_categories), skin_symptoms, report

def generate_summary_report(food_cat, snack_cat, skin_symp):
    """AI 스타일 요약 리포트"""
    report_parts = []
    
    # 음식 분석
    if food_cat or snack_cat:
        combined_food = {**food_cat}
        combined_food.update({f"{k} (간식)": v for k, v in snack_cat.items()})
        top_food = sorted(combined_food.items(), key=lambda x: x[1], reverse=True)[:2]
        
        if top_food:
            top_food_str = ", ".join([f"{k}({v}회)" for k, v in top_food])
            report_parts.append(f"이번 주는 {top_food_str}를 주로 섭취했고")
    
    # 피부 증상 분석
    if skin_symp:
        top_symp = sorted(skin_symp.items(), key=lambda x: x[1], reverse=True)[:2]
        symp_str = ", ".join([k for k, v in top_symp])
        report_parts.append(f"{symp_str}가 많이 발생했습니다.")
    
    return " ".join(report_parts) if report_parts else "이번 주 데이터가 충분하지 않습니다."

def get_skincare_recommendation(skin_conditions, weather=None):
    """피부 상태와 날씨를 결합한 화장품 추천"""
    recommendations = []
    weather_note = ''
    if weather and not weather.get('error'):
        temp = weather.get('temperature')
        code = weather.get('weathercode')
        if temp is not None:
            if temp >= 28:
                weather_note = '오늘은 고온다습하니 유수분 밸런스와 자외선 차단에 집중하세요.'
            elif temp <= 10:
                weather_note = '오늘은 저온 건조하니 고보습과 장벽 강화가 중요합니다.'
            else:
                weather_note = '오늘은 일반적인 보습과 저자극 관리를 유지하세요.'
        if code is not None:
            if code in [80, 81, 82]:
                weather_note += ' 비가 오면 피부가 예민해질 수 있으니 진정 케어를 추가하세요.'
            elif code == 0:
                weather_note += ' 맑은 날에는 자외선 차단제를 꼭 사용하세요.'

    # 수분 부족
    dry_keywords = ['속당김', '전체적인 극건조', '각질 들뜸']
    if any(cond in skin_conditions for cond in dry_keywords):
        ingredients = ['히알루론산', '세라마이드']
        recommendations.append({
            'type': '고보습 케어',
            'ingredients': ingredients,
            'routine': '히알루론산, 세라마이드 성분의 고보습 크림과 세럼을 아침/저녁으로 레이어링하세요.',
            'products': get_product_examples(ingredients)
        })
    
    # 민감/자극
    sensitive_keywords = ['홍조/붉어짐', '따가움/가려움', '화끈거리는 열감']
    if any(cond in skin_conditions for cond in sensitive_keywords):
        ingredients = ['시카(병풀)', '어성초', '판테놀']
        recommendations.append({
            'type': '진정 케어',
            'ingredients': ingredients,
            'routine': '시카, 어성초, 판테놀 성분의 진정 앰플과 크림으로 피부 장벽을 보호하세요.',
            'products': get_product_examples(ingredients)
        })
    
    # 트러블/염증
    trouble_keywords = ['좁쌀 여드름', '화농성 여드름', '결절성(단단한 아픈 여드름)']
    if any(cond in skin_conditions for cond in trouble_keywords):
        ingredients = ['살리실산(BHA)', '티트리', '아하(AHA)']
        recommendations.append({
            'type': '트러블 케어',
            'ingredients': ingredients,
            'routine': 'BHA, 티트리, AHA 성분의 스팟 세럼과 저자극 수분크림을 사용하세요.',
            'products': get_product_examples(ingredients)
        })
    
    # 좋은 상태면 유지 추천
    if '피부 상태 아주 좋음' in skin_conditions and not recommendations:
        ingredients = ['토너', '에센스', '크림']
        recommendations.append({
            'type': '유지 케어',
            'ingredients': ingredients,
            'routine': '현재 상태를 유지하기 위해 가벼운 보습과 자외선 차단 위주로 관리하세요.',
            'products': get_product_examples(ingredients)
        })
    
    if not recommendations:
        ingredients = ['클렌징', '토닝', '모이스처']
        recommendations.append({
            'type': '기본 케어',
            'ingredients': ingredients,
            'routine': '저자극 클렌저, 수분 토너, 보습 크림 위주의 기본 루틴을 유지하세요.',
            'products': get_product_examples(ingredients)
        })

    if weather_note:
        for rec in recommendations:
            rec['weather_note'] = weather_note

    return recommendations


def get_basic_agent_analysis(today_skin_conditions, summary_report, combined_food_stats, skin_stats):
    """간단한 에이전트 분석 결과 생성"""
    if not today_skin_conditions:
        return {
            'summary': summary_report or '최근 데이터가 부족하여 피부 상태 분석을 제공할 수 없습니다.',
            'patterns': [],
            'advice_context': '피부 상태가 없어 기본 유지 관리에 집중해야 합니다.'
        }

    diagnosis = []
    if '피부 상태 아주 좋음' in today_skin_conditions:
        other_symptoms = [s for s in today_skin_conditions if s != '피부 상태 아주 좋음']
        if other_symptoms:
            diagnosis.append(
                f"현재 전체적으로 피부가 좋지만 {', '.join(other_symptoms)} 징후가 함께 나타나 유지와 진정 관리가 필요합니다."
            )
        else:
            diagnosis.append('현재 피부 상태가 매우 좋습니다. 과도한 제품 사용을 피하고 기본 보습을 유지하세요.')
    else:
        if any(symptom in today_skin_conditions for symptom in ['속당김', '전체적인 극건조', '각질 들뜸']):
            diagnosis.append('수분 부족과 장벽 약화 징후가 있어 고보습 케어가 필요합니다.')
        if any(symptom in today_skin_conditions for symptom in ['홍조/붉어짐', '따가움/가려움', '화끈거리는 열감']):
            diagnosis.append('민감/자극 증상이 있어 진정 중심 케어가 필요합니다.')
        if any(symptom in today_skin_conditions for symptom in ['좁쌀 여드름', '화농성 여드름', '결절성(단단한 아픈 여드름)']):
            diagnosis.append('트러블 징후가 있어 항염 및 유분 조절 케어가 필요합니다.')

    if not diagnosis:
        diagnosis.append('기본적인 피부 관리가 필요합니다. 더 많은 증상을 기록하면 정밀한 진단을 제시합니다.')

    return {
        'summary': ' '.join(diagnosis),
        'patterns': diagnosis,
        'advice_context': '오늘 피부 증상을 바탕으로 케어 우선순위를 정했습니다.'
    }


def get_product_examples(ingredients):
    examples = []
    for ingredient in ingredients:
        examples.extend(PRODUCT_EXAMPLES.get(ingredient, []))
    return examples


def fetch_oliveyoung_products(query, limit=5):
    """올리브영 API가 있는 경우 제품 검색 결과를 가져오는 자리표시 함수입니다."""
    # 실제로는 올리브영이 제공하는 공식 파트너 API 문서를 확인하고,
    # 해당 엔드포인트와 인증 정보를 사용해 아래처럼 호출해야 합니다.
    # 예시:
    # import httpx
    # url = 'https://api.oliveyoung.co.kr/v1/products/search'
    # headers = {'Authorization': f'Bearer {YOUR_API_KEY}'}
    # params = {'q': query, 'limit': limit}
    # response = httpx.get(url, headers=headers, params=params, timeout=10)
    # data = response.json()
    # return [item['name'] for item in data.get('products', [])]
    return []


def get_combined_action_recommendations(record, skin_conditions):
    actions = []
    if not record:
        return actions

    food_categories = [record.get('breakfast', {}).get('category', ''),
                       record.get('lunch', {}).get('category', ''),
                       record.get('dinner', {}).get('category', '')]
    snack_categories = [k for k, v in record.get('snacks', {}).items() if v]

    if any(item in ['패스트푸드/분식', '면류 (밀가루)', '음료 (가당)', '초콜릿/사탕/젤리'] for item in food_categories + snack_categories):
        actions.append('기름진 음식과 단 음료는 유분 과다 및 트러블을 악화시킬 수 있습니다. 물과 채소를 함께 드세요.')
    if '유분 과다(개기름)' in skin_conditions or '화이트헤드/블랙헤드' in skin_conditions:
        actions.append('피부 유분 조절이 필요해 보입니다. 기름진 간식은 줄이고, 저자극 클렌징을 도입하세요.')
    if '홍조/붉어짐' in skin_conditions or '따가움/가려움' in skin_conditions:
        actions.append('민감 피부가 감지되었습니다. 자극적인 음식과 과도한 양념을 피하고, 진정 케어 제품을 사용하세요.')
    if '좁쌀 여드름' in skin_conditions or '화농성 여드름' in skin_conditions or '결절성(단단한 아픈 여드름)' in skin_conditions:
        actions.append('트러블 징후가 있으므로 스팟 케어와 함께 당분/유지를 줄이는 식습관이 도움이 됩니다.')
    if '속당김' in skin_conditions or '전체적인 극건조' in skin_conditions or '각질 들뜸' in skin_conditions:
        actions.append('수분 부족 징후가 있습니다. 하루 동안 충분한 수분 섭취와 히알루론산/세라마이드 제품을 권장합니다.')

    if not actions:
        actions.append('식습관과 피부 변화를 함께 기록하면 문제 원인을 빠르게 파악하고 관리 루틴을 개선할 수 있습니다.')

    actions.append('꾸준한 기록은 피부 상태와 음식 패턴의 상관관계를 분석하는 데 가장 큰 도움이 됩니다.')
    return actions


def get_weather_info(city=WEATHER_CITY):
    try:
        from chapter7_code.weather_tool import get_weather

        weather = get_weather(city)
        if weather.get('error'):
            return {'error': weather['error']}
        return weather
    except Exception:
        return {'error': '날씨 정보를 가져오는 중 문제가 발생했습니다.'}


def get_weather_recommendation(weather):
    if weather.get('error'):
        return weather['error']

    temp = weather.get('temperature')
    code = weather.get('weathercode')
    advice = []
    if temp is not None:
        if temp >= 28:
            advice.append('고온다습한 날씨에는 유수분 조절과 자외선 차단에 집중하세요.')
        elif temp <= 10:
            advice.append('저온 건조한 날씨에는 고보습 크림과 장벽 케어가 필요합니다.')
        else:
            advice.append('오늘은 기본 보습과 자극 없는 관리가 가장 안전합니다.')
    if code is not None:
        if code in [80, 81, 82]:
            advice.append('비가 오는 날에는 피부가 예민해질 수 있으니 진정 케어를 추가하세요.')
        elif code == 0:
            advice.append('맑은 날씨에는 자외선 차단제를 잊지 마세요.')
    return ' '.join(advice) if advice else '오늘 날씨에 맞춘 기본 피부 관리가 필요합니다.'


def render_saved_dates_history(all_records):
    saved_dates = sorted(all_records.keys(), reverse=True)
    if not saved_dates:
        st.info('저장된 날짜가 없습니다. 기록 후 자동으로 추가됩니다.')
        return

    st.markdown('### 📅 저장된 날짜에서 빠르게 열기')
    buttons = st.columns(4)
    for idx, date_key in enumerate(saved_dates[:12]):
        col = buttons[idx % 4]
        col.button(
            date_key,
            key=f'saved_date_{date_key}',
            on_click=_select_saved_date,
            args=(date_key,)
        )


def _select_saved_date(date_key):
    st.session_state['selected_date_widget'] = datetime.strptime(date_key, '%Y-%m-%d').date()
    st.session_state['page_selector'] = '📝 기록하기'
    st.session_state['active_date'] = date_key
    # 날짜 선택 상태 초기화
    reset_date_selection_state()
    all_records = load_all_records()
    today_record = get_today_record(all_records, date_key)
    load_record_into_session(today_record)


def _navigate_to_page(page_name):
    st.session_state['pending_page_selector'] = page_name


def _apply_pending_state():
    if 'pending_selected_date_widget' in st.session_state:
        st.session_state['selected_date_widget'] = st.session_state.pop('pending_selected_date_widget')
    if 'pending_page_selector' in st.session_state:
        st.session_state['page_selector'] = st.session_state.pop('pending_page_selector')

# ═══════════════════════════════════════════════════════════════════════
# UI 컴포넌트 함수
# ═══════════════════════════════════════════════════════════════════════
def render_toggle_button_group(label, all_items, session_key):
    """토글 버튼 그룹 렌더링"""
    st.subheader(label)
    
    if session_key not in st.session_state:
        st.session_state[session_key] = set()
    
    cols = st.columns(3)
    for idx, item in enumerate(all_items):
        col_idx = idx % 3
        with cols[col_idx]:
            is_selected = item in st.session_state[session_key]
            btn_class = "toggle-btn active" if is_selected else "toggle-btn"


# 584번 줄부터 시작하는 이 구역을 그대로 붙여넣으세요.
    if is_selected:
                        # 🎨 선택되었을 때: 원하는 진한 색상 코드를 여기에 넣으세요! 
                        # (#5DADE2는 처음에 말씀하셨던 그 예쁜 하늘색입니다. 핑크를 원하시면 #FF6B9D로 바꾸세요!)
                        button_text = f"<a>✓ {item}</a>"
                        st.markdown(
                            """
                            <style>
                            div.stButton button:has(a) {
                                background-color: #5DADE2 !important;  /* 🩵 선택 시 확실하게 바뀔 진한 색 */
                                color: #000000 !important;             /* 🖤 검은색 글자 */
                                border: 2px solid #000000 !important;  /* ✏️ 얇은 검은색 테두리 */
                                font-weight: 800 !important;           /* 🔤 글씨 두껍게 */
                            }
                            </style>
                            """, 
                            unsafe_allow_html=True
                        )
    else:
                        button_text = f"  {item}"
                    
                    # 🟢 아래 버튼과 조건문들의 맨 앞 시작 라인을 자석처럼 일렬로 맞췄습니다.
    if st.button(
                        button_text,
                        key=f"{session_key}_{item}",
                        use_container_width=True
                    ):
                        if is_selected:
                            st.session_state[session_key].discard(item)
                        else:
                            st.session_state[session_key].add(item)
                        st.rerun()


def render_skin_conditions_section():
    """피부 상태 선택 섹션"""
    st.markdown("## 🧴 오늘의 피부 상태 선택")
    
    # 각 카테고리별로 렌더링
    all_selected = set()
    
    for category, items in SKIN_CONDITIONS.items():
        with st.container():
            st.markdown(f"### {category}")
            session_key = f"skin_{category}"
            
            if session_key not in st.session_state:
                st.session_state[session_key] = set()
            
            all_selected.update(st.session_state[session_key])

            cols = st.columns(3)

            for idx, item in enumerate(items):
                col_idx = idx % 3

                with cols[col_idx]:
                    is_selected = item in st.session_state[session_key]
                    btn_class = "toggle-btn active" if is_selected else "toggle-btn"

                    # 선택된 상태를 버튼 텍스트에 표시 (✓ 이모지)
                    button_text = f"✓ {item}" if is_selected else f"  {item}"

                
                    if st.button(
                        button_text,
                        key=f"{session_key}_{item}",
                        use_container_width=True
                    ):

                        if is_selected:
                            st.session_state[session_key].discard(item)

                        else:
                            st.session_state[session_key].add(item)

                        st.rerun()

    return list(all_selected)

def render_meal_section(meal_name, categories):
    """식사 섹션 렌더링"""
    st.markdown(f"### {meal_name}")
    
    # 식사 안 함 토글
    did_not_eat = st.checkbox(
        "이 끼니를 먹지 않았습니다",
        key=f"did_not_eat_{meal_name}"
    )
    
    if did_not_eat:
        return {
            'category': '안 했음',
            'menu': ''
        }
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # 세션 상태에서 저장된 값 읽기
        default_cat = st.session_state.get(f"cat_{meal_name}")
        if default_cat and default_cat in categories:
            idx = categories.index(default_cat)
        else:
            idx = 0
        category = st.selectbox(
            f"{meal_name} 카테고리",
            categories,
            index=idx,
            key=f"cat_{meal_name}"
        )
    
    with col2:
        # 세션 상태에서 저장된 값 읽기
        default_menu = st.session_state.get(f"menu_{meal_name}", "")
        menu = st.text_input(
            f"{meal_name} 구체적 메뉴",
            value=default_menu,
            key=f"menu_{meal_name}",
            placeholder="예: 된장찌개, 계란말이, 밥"
        )
    
    return {
        'category': category if category else '',
        'menu': menu
    }

# ═══════════════════════════════════════════════════════════════
# 메인 앱
# ═══════════════════════════════════════════════════════════════
def main():
    st.markdown("# 🌟 S.E.E. v2")
    st.markdown("Skin & Eating Habits Experience - 피부와 식습관 추적 에이전트")
    
    # 날짜 선택
    st.markdown("---")
    _apply_pending_state()
    
    col_date, col_nav = st.columns([2, 1])
    with col_date:
        selected_date = st.date_input(
            "📅 기록할 날짜 선택",
            value=st.session_state.get('selected_date_widget', datetime.now().date()),
            key="selected_date_widget"
        )
    
    date_key = get_date_key(selected_date)
    
    # 페이지 선택 라디오
    section_options = ["📝 기록하기", "📊 통계 및 화장품 추천"]
    selected_section = st.radio(
        "페이지 선택",
        section_options,
        key='page_selector',
        horizontal=True
    )
    show_stats = selected_section == section_options[1]
    
    all_records = load_all_records()
    today_record = get_today_record(all_records, date_key)

    if st.session_state.get('active_date') != date_key:
        reset_date_selection_state()
        st.session_state['active_date'] = date_key 
        load_record_into_session(today_record)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 기록하기 화면
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if not show_stats:
        st.markdown("### 📍 오늘의 식단 기록")
        if date_key in all_records:
            st.success(f"✅ {date_key}에 저장된 기록을 불러왔습니다.")

        # 저장된 날짜 히스토리
        render_saved_dates_history(all_records)
        
        # 식사 기록 섹션
        st.markdown("### 🍳🍱🍲 식사 기록")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🍳 아침")
            today_record['breakfast'] = render_meal_section('아침', MEAL_CATEGORIES['아침'])
        
        with col2:
            st.markdown("#### 🍱 점심")
            today_record['lunch'] = render_meal_section('점심', MEAL_CATEGORIES['점심'])
        
        st.markdown("#### 🍲 저녁")
        today_record['dinner'] = render_meal_section('저녁', MEAL_CATEGORIES['저녁'])
        
        # 군것질 섹션
        st.markdown("---")
        st.markdown("### 🍭 간식/군것질 (특별 관찰)")
        st.info("💡 피부 상태에 미치는 영향이 큰 음식들입니다. 꼼꼼히 기록해주세요.")
        
        snack_cols = st.columns(6)
        snack_data = {}
        for idx, cat in enumerate(SNACK_CATEGORIES):
            with snack_cols[idx]:
                # 세션 상태에서 저장된 값 읽기
                default_snack = st.session_state.get(f"snack_{cat}", "")
                snack_input = st.text_input(
                    cat,
                    value=default_snack,
                    key=f"snack_{cat}",
                    placeholder="기입 또는 공백"
                )
                snack_data[cat] = {
                    'category': cat,
                    'menu': snack_input
                } if snack_input else {}
        
        today_record['snacks'] = snack_data
        
        # 피부 상태 선택
        st.markdown('---')
        st.markdown('### 🧴 오늘의 피부 상태')
        st.info("💡 여러 개를 선택할 수 있습니다. 해당 증상을 클릭하세요.")
        
        selected_conditions = render_skin_conditions_section()
        today_record['skin_conditions'] = selected_conditions
        
        # 저장 버튼
        st.markdown('---')
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("💾 오늘 데이터 저장", use_container_width=True, type="primary"):
                save_today_record(all_records, date_key, today_record)
                st.success(f"✅ {date_key} 데이터가 저장되었습니다!")
                st.session_state['page_selector'] = section_options[1]
                st.rerun()

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 통계 및 추천 화면
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    if show_stats:
        food_stats, skin_stats, summary_report = analyze_last_7_days(all_records)

        st.markdown('### 📰 이번 주 요약 리포트')
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("← 기록하기로 돌아가기", type="secondary"):
                _navigate_to_page('📝 기록하기')
        if summary_report:
            st.success(f"📌 {summary_report}")
        else:
            st.info('이번 주 데이터가 충분하지 않습니다. 먼저 기록을 추가해주세요.')

        st.markdown("---")
        if food_stats or skin_stats:
            st.markdown('### 📊 음식 & 피부 상태 통계')
            if food_stats:
                food_categories, snack_categories = food_stats
                left, right = st.columns(2)
                with left:
                    st.markdown("#### 🍽️ 일반 식사")
                    food_df = pd.DataFrame(
                        sorted(food_categories.items(), key=lambda x: x[1], reverse=True),
                        columns=['카테고리', '횟수']
                    )
                    st.table(food_df)
                    st.bar_chart(food_df.set_index('카테고리'))
                with right:
                    st.markdown("#### 🍭 간식/군것질")
                    snack_df = pd.DataFrame(
                        sorted(snack_categories.items(), key=lambda x: x[1], reverse=True),
                        columns=['카테고리', '횟수']
                    )
                    st.table(snack_df)
                    st.bar_chart(snack_df.set_index('카테고리'))

            if skin_stats:
                st.markdown("#### 🧴 주요 피부 증상 비교")
                skin_df = pd.DataFrame(
                    sorted(skin_stats.items(), key=lambda x: x[1], reverse=True),
                    columns=['증상', '발생 횟수']
                )
                st.table(skin_df)
                st.bar_chart(skin_df.set_index('증상'))
        else:
            st.info("기록된 음식이나 피부 통계가 없습니다. 먼저 기록을 추가해주세요.")

        st.markdown("---")
        st.markdown('### ☁️ 날씨 기반 추천')
        weather = get_weather_info()
        weather_for_recs = None
        if weather.get('error'):
            st.warning(weather['error'])
            st.info('현재 날씨 정보를 가져올 수 없어 기본 추천만 제공합니다.')
            weather_advice = '오늘은 피부에 자극 없는 기본 보습과 진정 케어를 권장합니다.'
        else:
            st.info(f"📍 {weather.get('city')} 현재 온도 {weather.get('temperature')}℃")
            weather_advice = get_weather_recommendation(weather)
            weather_for_recs = weather
        st.markdown(f"**💡 추천**: {weather_advice}")

        st.markdown("---")
        st.markdown('### 💄 맞춤 추천')

        today_skin_conditions = today_record.get('skin_conditions', [])
        combined_advice = get_combined_action_recommendations(today_record, today_skin_conditions)
        if combined_advice:
            st.markdown("#### 🧠 식습관+피부 연계 추천")
            for item in combined_advice:
                st.write(f"✓ {item}")

        if today_skin_conditions:
            # 세션 단위 토글: LLM 추천 사용 여부
            use_llm_default = USE_LLM_RECS
            use_llm = st.checkbox("AI 에이전트 기반 처방 사용 (정밀 분석)", value=use_llm_default, help="LLM을 사용한 더 정확하고 맞춤화된 처방 제공")

            # 최근 7일 분석 결과 준비
            food_stats, skin_stats, summary_report = analyze_last_7_days(all_records)
            combined_food_stats = {}
            if food_stats:
                food_categories, snack_categories = food_stats
                combined_food_stats = {
                    **food_categories,
                    **{f"{k} (간식)": v for k, v in snack_categories.items()}
                }

            context = {
                'today': {
                    'skin_conditions': today_skin_conditions
                },
                'last7': {
                    'report': summary_report or '',
                    'food_stats': combined_food_stats,
                    'skin_stats': skin_stats or {}
                }
            }

            if use_llm:
                st.markdown('### 🧠 AI 분석 결과')
                llm_analysis = analyze_with_llm(context)
                context['analysis'] = llm_analysis

                st.info(llm_analysis.get('summary', '분석 결과가 없습니다.'))
                if llm_analysis.get('patterns'):
                    st.markdown(f"**🔍 발견 패턴**: {', '.join(llm_analysis.get('patterns', []))}")
                if llm_analysis.get('advice_context'):
                    st.markdown(f"**💡 추천 맥락**: {llm_analysis.get('advice_context')}")

                recommendations = None
                llm_result = recommend_with_llm(context)
                recommendations = llm_result.get('recommendations') if isinstance(llm_result, dict) else None
                if not recommendations:
                    recommendations = get_skincare_recommendation(today_skin_conditions, weather_for_recs)

                review_data = review_recommendation(context, recommendations)
                guide_text = write_user_guide(context, recommendations)

                st.markdown('### ✅ AI 추천 검토 결과')
                if review_data.get('valid'):
                    st.success(f"✓ 검토 통과: {review_data.get('notes', '추천이 입력 정보와 일치합니다.')}")
                else:
                    st.warning(f"⚠️ 검토 경고: {review_data.get('notes', '추가 검토가 필요합니다.')}")

                if guide_text:
                    st.markdown('### 📝 AI 맞춤 안내문')
                    st.info(guide_text)
                analysis_data = llm_analysis
            else:
                st.markdown('### 🧠 규칙 기반 분석 결과')
                basic_analysis = get_basic_agent_analysis(today_skin_conditions, summary_report, combined_food_stats, skin_stats or {})
                st.info(basic_analysis.get('summary', '분석 결과가 없습니다.'))
                if basic_analysis.get('patterns'):
                    st.markdown(f"**🔍 발견 패턴**: {', '.join(basic_analysis.get('patterns', []))}")
                if basic_analysis.get('advice_context'):
                    st.markdown(f"**💡 추천 맥락**: {basic_analysis.get('advice_context')}")

                recommendations = get_skincare_recommendation(today_skin_conditions, weather_for_recs)
                review_data = review_recommendation(context, recommendations)
                guide_text = write_user_guide(context, recommendations)
                analysis_data = basic_analysis

            st.markdown('### 💅 화장품 추천 결과')
            for idx, rec in enumerate(recommendations, 1):
                with st.container():
                    st.markdown(f'#### #{idx} {rec.get("type", "추천")}')
                    
                    ing = rec.get('ingredients', [])
                    st.markdown(f'**🧪 성분**: {", ".join(ing) if ing else "제공 안됨"}')
                    
                    products = rec.get('products') or get_product_examples(ing)
                    if products:
                        st.markdown(f'**✨ 추천 제품**: {", ".join(products[:3])}')
                    
                    if rec.get('weather_note'):
                        st.markdown(f'**☀️ 날씨 기반 추천**: {rec.get("weather_note")}')

                    routine = rec.get('routine', '')
                    reason = rec.get('reason', '')
                    food_advice = rec.get('food_advice', '')
                    warning = rec.get('warning', '')
                    confidence = rec.get('confidence')

                    if routine:
                        st.markdown(f'**📋 스킨케어 루틴**\n{routine}')
                    if reason:
                        st.markdown(f'**💡 근거**: {reason}')
                    if food_advice:
                        st.markdown(f'**🍽️ 식습관 조언**\n{food_advice}')
                    if warning:
                        st.warning(f"⚠️ 주의: {warning}")
                    if confidence is not None:
                        st.caption(f"📊 신뢰도: {int(confidence*100)}%")
                    st.markdown("---")
        else:
            st.info("🤔 피부 상태를 선택하면 맞춤 화장품 추천을 받을 수 있습니다.")

if __name__ == "__main__":
    main()
