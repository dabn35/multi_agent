import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path
import os

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

# CSS for toggle buttons
TOGGLE_BUTTON_CSS = """
<style>
.toggle-btn {
    display: inline-block;
    padding: 8px 12px;
    margin: 4px;
    border: 2px solid #d0d0d0;
    border-radius: 6px;
    background-color: #f0f0f0;
    color: #333;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    user-select: none;
}
.toggle-btn:hover {
    border-color: #888;
    background-color: #e0e0e0;
}
.toggle-btn.active {
    background-color: #FF6B9D;
    color: white;
    border-color: #FF6B9D;
    font-weight: 600;
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

def get_skincare_recommendation(skin_conditions):
    """피부 상태에 따른 화장품 추천"""
    recommendations = []
    
    # 수분 부족
    dry_keywords = ['속당김', '전체적인 극건조', '각질 들뜸']
    if any(cond in skin_conditions for cond in dry_keywords):
        recommendations.append({
            'type': '고보습 케어',
            'ingredients': ['히알루론산', '세라마이드'],
            'routine': '히알루론산, 세라마이드 성분의 고보습 크림 레이어링 추천'
        })
    
    # 민감/자극
    sensitive_keywords = ['홍조/붉어짐', '따가움/가려움', '화끈거리는 열감']
    if any(cond in skin_conditions for cond in sensitive_keywords):
        recommendations.append({
            'type': '진정 케어',
            'ingredients': ['시카(병풀)', '어성초', '판테놀'],
            'routine': '시카(병풀), 어성초, 판테놀 성분의 진정 앰플 및 쿨링 케어 추천'
        })
    
    # 트러블/염증
    trouble_keywords = ['좁쌀 여드름', '화농성 여드름', '결절성(단단한 아픈 여드름)']
    if any(cond in skin_conditions for cond in trouble_keywords):
        recommendations.append({
            'type': '트러블 케어',
            'ingredients': ['살리실산(BHA)', '티트리', '아하(AHA)'],
            'routine': '살리실산(BHA), 티트리, 아하(AHA) 성분의 스팟 케어 및 유분 없는 젤 수분크림 추천'
        })
    
    # 좋은 상태면 유지 추천
    if '피부 상태 아주 좋음' in skin_conditions and not recommendations:
        recommendations.append({
            'type': '유지 케어',
            'ingredients': ['토너', '에센스', '크림'],
            'routine': '현재의 좋은 상태를 유지하기 위해 기본 3스텝(토너-에센스-크림) 루틴을 꾸준히 진행하세요.'
        })
    
    if not recommendations:
        recommendations.append({
            'type': '기본 케어',
            'ingredients': ['클렌징', '토닝', '모이스처'],
            'routine': '기본 클렌징-토닝-모이스처 루틴을 꾸준히 진행하세요.'
        })
    
    return recommendations

# ═══════════════════════════════════════════════════════════════
# UI 컴포넌트 함수
# ═══════════════════════════════════════════════════════════════
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
            
            if st.button(
                item,
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
                
                if is_selected:
                    all_selected.add(item)
    
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
        category = st.selectbox(
            f"{meal_name} 카테고리",
            categories,
            key=f"cat_{meal_name}"
        )
    
    with col2:
        menu = st.text_input(
            f"{meal_name} 구체적 메뉴",
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
    st.title("🌟 S.E.E. v2")
    st.markdown("**Skin & Eating Habits Experience** - 피부와 식습관 추적 에이전트")
    
    # 날짜 선택
    st.markdown("---")
    selected_date = st.date_input(
        "📅 기록할 날짜 선택",
        value=datetime.now().date(),
        key="date_picker"
    )
    date_key = get_date_key(selected_date)
    
    # 탭 구성
    tab1, tab2 = st.tabs(["📝 기록하기", "📊 통계 및 화장품 추천"])
    
    all_records = load_all_records()
    today_record = get_today_record(all_records, date_key)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 탭 1: 기록하기
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab1:
        st.markdown("### 📍 오늘의 식단 기록")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🍳 아침")
            today_record['breakfast'] = render_meal_section('아침', MEAL_CATEGORIES['아침'])
        
        with col2:
            st.markdown("#### 🍱 점심")
            today_record['lunch'] = render_meal_section('점심', MEAL_CATEGORIES['점심'])
        
        st.markdown("#### 🍲 저녁")
        today_record['dinner'] = render_meal_section('저녁', MEAL_CATEGORIES['저녁'])
        
        # 군것질 섹션 (눈에 띄게)
        st.markdown("---")
        with st.container():
            st.markdown("### 🍭 간식/군것질 (특별 관찰)")
            st.info("💡 피부 상태에 미치는 영향이 큰 음식들입니다. 꼼꼼히 기록해주세요.")
            
            snack_cols = st.columns(6)
            snack_data = {}
            for idx, cat in enumerate(SNACK_CATEGORIES):
                with snack_cols[idx]:
                    snack_input = st.text_input(
                        cat,
                        key=f"snack_{cat}",
                        placeholder="기입 또는 공백"
                    )
                    snack_data[cat] = {
                        'category': cat,
                        'menu': snack_input
                    } if snack_input else {}
            
            today_record['snacks'] = snack_data
        
        # 피부 상태 선택
        st.markdown("---")
        st.markdown("### 🧴 오늘의 피부 상태")
        st.info("💡 여러 개를 선택할 수 있습니다. 해당 증상을 클릭하세요.")
        
        selected_conditions = render_skin_conditions_section()
        today_record['skin_conditions'] = selected_conditions
        
        # 저장 버튼
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("💾 오늘 데이터 저장", use_container_width=True, type="primary"):
                save_today_record(all_records, date_key, today_record)
                st.success(f"✅ {date_key} 데이터가 저장되었습니다!")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 탭 2: 통계 및 추천
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    with tab2:
        food_stats, skin_stats, summary_report = analyze_last_7_days(all_records)
        
        # 요약 리포트 (최상단에 눈에 띄게)
        if summary_report:
            st.markdown("---")
            with st.container():
                st.markdown("### 📰 이번 주 요약 리포트")
                st.success(f"📌 {summary_report}")
        
        st.markdown("---")
        
        # 음식 통계
        if food_stats:
            st.markdown("### 🍽️ 최근 7일간 주요 음식 카테고리")
            
            food_categories, snack_categories = food_stats
            
            if food_categories:
                st.markdown("#### 일반 식사")
                food_df = pd.DataFrame(
                    sorted(food_categories.items(), key=lambda x: x[1], reverse=True),
                    columns=['카테고리', '횟수']
                )
                st.bar_chart(food_df.set_index('카테고리'))
            
            if snack_categories:
                st.markdown("#### 간식/군것질")
                snack_df = pd.DataFrame(
                    sorted(snack_categories.items(), key=lambda x: x[1], reverse=True),
                    columns=['카테고리', '횟수']
                )
                st.bar_chart(snack_df.set_index('카테고리'))
        else:
            st.info("📊 아직 기록된 데이터가 없습니다.")
        
        st.markdown("---")
        
        # 피부 상태 통계
        if skin_stats:
            st.markdown("### 🧴 최근 7일간 주요 피부 증상")
            skin_df = pd.DataFrame(
                sorted(skin_stats.items(), key=lambda x: x[1], reverse=True),
                columns=['증상', '발생 횟수']
            )
            st.bar_chart(skin_df.set_index('증상'))
        else:
            st.info("📊 아직 피부 기록이 없습니다.")
        
        st.markdown("---")
        
        # 오늘 피부 상태 기반 화장품 추천
        st.markdown("### 💄 오늘의 피부 상태에 맞는 화장품 추천")
        
        today_skin_conditions = today_record.get('skin_conditions', [])
        
        if today_skin_conditions:
            recommendations = get_skincare_recommendation(today_skin_conditions)
            
            for idx, rec in enumerate(recommendations, 1):
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"**{rec['type']}**")
                    with col2:
                        st.markdown(f"🧪 성분: {', '.join(rec['ingredients'])}")
                    
                    st.markdown(f"💡 {rec['routine']}")
                    st.markdown("---")
        else:
            st.info("🤔 피부 상태를 선택하면 맞춤 화장품 추천을 받을 수 있습니다.")

if __name__ == "__main__":
    main()
