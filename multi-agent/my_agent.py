#!/usr/bin/env python3
"""
my_agent.py

에이전트 v0 스캐폴드: extract_facts, classify_items, write_output
초보자도 읽기 쉽도록 단순한 규칙 기반 구현입니다.

실행: python my_agent.py
"""

import re
from collections import defaultdict, Counter

SAMPLE_INPUT = """
오늘 아침에 B사 수분 크림 발랐는데, 오후 되니까 볼 쪽이 좀 당기고 간지러워.
어제 술을 마셔서 그런가? 턱 주변에 좁쌀 여드름이 두 개 올라왔어. 진정 앰플 듬뿍 바르고 자야지.
오늘부터 C 브랜드 비타민 C 세럼 시작. 첫 느낌은 약간 따끔함. 날씨가 건조해서 그런지 평소보다 흡수가 더딘 것 같아.
미세먼지 때문인지 세안 후에 피부가 너무 붉어. 오늘은 평소 쓰던 클렌징 폼 말고 오일 타입으로 세안함.
주말 내내 캠핑 다녀와서 자외선 노출이 많았음. 전체적으로 피부 열감이 심하고 푸석푸석해.
요즘 마감 기한이라 잠을 4시간밖에 못 잤더니 다크서클이 심해지고 안색이 칙칙함.
"""


def extract_facts(raw_text):
    """간단한 규칙 기반 추출기.

    반환 형식: dict {
        'text': str,
        'products': [str],
        'symptoms': [str],
        'subjective_score': int (1-5),
        'sleep_hours': int or None,
    }
    """
    text = raw_text.strip()

    # 제품 추출(간단 키워드 매칭)
    product_keywords = ['크림', '세럼', '앰플', '클렌징', '클렌징 폼', '오일', '토너']
    products = []
    for kw in product_keywords:
        if kw in text:
            # 주변 단어(브랜드 표기 포함)를 단순 추출
            m = re.search(r'(\S{0,10}' + re.escape(kw) + r'\S{0,10})', text)
            if m:
                prod = m.group(0).strip(' ,.')
                products.append(prod)

    # 브랜드 표기(B사, C 브랜드) 추출
    brands = re.findall(r'([A-Z가-힣0-9]{1,5}사|[A-Z가-힣0-9]{1,10} 브랜드)', text)
    for b in brands:
        products.append(b)

    products = list(dict.fromkeys(products))  # 순서 유지 중복 제거

    # 증상(증상 단어 사전)
    symptom_dict = {
        '당김': ['당기', '땡김'],
        '간지러움': ['간지럽', '간지러워'],
        '따가움': ['따가', '따끔'],
        '홍조': ['붉', '붉어', '붉음'],
        '좁쌀': ['좁쌀'],
        '트러블': ['여드름', '트러블'],
        '열감': ['열감', '열이'],
        '푸석': ['푸석'],
        '다크서클': ['다크서클'],
        '칙칙': ['칙칙']
    }
    symptoms = []
    for label, toks in symptom_dict.items():
        for t in toks:
            if t in text:
                symptoms.append(label)
                break

    # 주관적 스코어(간단 휴리스틱)
    score = 3
    neg_words = ['따가', '간지', '붉', '좁쌀', '트러블', '열감', '푸석', '칙칙']
    pos_words = ['진정', '편안', '흡수 잘']
    for w in neg_words:
        if w in text:
            score -= 1
    for w in pos_words:
        if w in text:
            score += 1
    score = max(1, min(5, score))

    # 수면 시간 추출
    sleep_hours = None
    m = re.search(r'(\d{1,2})시간', text)
    if m:
        try:
            sleep_hours = int(m.group(1))
        except ValueError:
            sleep_hours = None

    return {
        'text': text,
        'products': products,
        'symptoms': symptoms,
        'subjective_score': score,
        'sleep_hours': sleep_hours,
    }


def classify_items(records):
    """간단 분류 및 인과 후보 도출.

    - env_cluster: 텍스트 기반 추정(실제 환경 API 미사용)
    - reaction_group: '안정'/'좁쌀'/'홍조'/'각질' 등
    - rules: (env_cluster, product, reaction) 카운트
    """
    env_clusters = []
    reaction_groups = []
    rules = Counter()

    for r in records:
        text = r['text']

        # 환경 클러스터 추정(간단 규칙)
        env = 'unknown'
        if '건조' in text or '흡수' in text:
            env = '저온건조'
        if '미세먼지' in text:
            env = '고미세먼지'
        if '자외선' in text or '캠핑' in text:
            env = '고자외선'
        if '습' in text or '땀' in text:
            env = '고온다습'

        env_clusters.append(env)

        # 반응군 분류
        if '홍조' in r['symptoms'] or any(s in text for s in ['붉','붉어']):
            reaction = '홍조'
        elif '좁쌀' in r['symptoms']:
            reaction = '좁쌀'
        elif '푸석' in r['symptoms'] or '각질' in text:
            reaction = '각질'
        else:
            reaction = '안정'

        reaction_groups.append(reaction)

        # 규칙 후보 추가
        for prod in r['products']:
            rules[(env, prod, reaction)] += 1

    analysis = {
        'env_clusters': env_clusters,
        'reaction_groups': reaction_groups,
        'rules': rules,
    }
    return analysis


def write_output(records, analysis):
    """간단한 리포트 생성 및 예측 알림.

    반환: dict {'daily_reports': [...], 'insights': {...}, 'alerts': [...]}
    """
    daily = []
    for i, r in enumerate(records, 1):
        summary = {
            'id': i,
            'text': r['text'],
            'products': r['products'],
            'symptoms': r['symptoms'],
            'subjective_score': r['subjective_score'],
        }
        daily.append(summary)

    # 인사이트: 제품별 반응 요약
    prod_counter = defaultdict(lambda: {'total': 0, 'bad': 0})
    for r, react in zip(records, analysis['reaction_groups']):
        for p in r['products']:
            prod_counter[p]['total'] += 1
            if react != '안정':
                prod_counter[p]['bad'] += 1

    insights = {'product_summary': prod_counter}

    # 간단한 '독 vs 득' 판단
    toxic = []
    beneficial = []
    for p, v in prod_counter.items():
        if v['total'] >= 1:
            ratio = v['bad'] / v['total']
            if ratio >= 0.5:
                toxic.append(p)
            else:
                beneficial.append(p)

    # 알림(예측): 간단 규칙
    alerts = []
    # 미세먼지 관련 텍스트가 하나라도 있으면 알림 생성
    if any('미세먼지' in r['text'] for r in records):
        alerts.append('내일 미세먼지 주의: 외출 시 보호 조치 권장')
    if any('자외선' in r['text'] or '캠핑' in r['text'] for r in records):
        alerts.append('자외선 노출 주의: 자외선 차단 권장')
    # 수면 부족 경고
    if any(r.get('sleep_hours') is not None and r.get('sleep_hours') <= 4 for r in records):
        alerts.append('수면 부족 관찰: 회복 및 보습 루틴 권장')

    report = {
        'daily_reports': daily,
        'insights': {
            'toxic_products': toxic,
            'beneficial_products': beneficial,
        },
        'alerts': alerts,
    }
    return report


def main():
    lines = [ln.strip() for ln in SAMPLE_INPUT.strip().splitlines() if ln.strip()]

    print('=== 입력 예시 수집 ===')
    for i, ln in enumerate(lines, 1):
        print(f'{i}.', ln)

    # 1) 추출
    records = []
    print('\n=== 1) extract_facts 결과 ===')
    for ln in lines:
        rec = extract_facts(ln)
        records.append(rec)
        print(rec)

    # 2) 분류/분석
    print('\n=== 2) classify_items 결과 ===')
    analysis = classify_items(records)
    print('env_clusters:', analysis['env_clusters'])
    print('reaction_groups:', analysis['reaction_groups'])
    print('rules (sample up to 10):')
    for k, v in list(analysis['rules'].items())[:10]:
        print(k, '->', v)

    # 3) 리포트 생성
    print('\n=== 3) write_output 결과 ===')
    report = write_output(records, analysis)
    print('Daily reports count:', len(report['daily_reports']))
    print('Toxic products:', report['insights']['toxic_products'])
    print('Beneficial products:', report['insights']['beneficial_products'])
    print('Alerts:', report['alerts'])


if __name__ == '__main__':
    main()
