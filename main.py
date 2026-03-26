# -*- coding: utf-8 -*-
"""
Streamlit MBTI 검사 & 시각화 앱
- 4가지 차원(외향/내향, 감각/직관, 사고/감정, 판단/인식) 중 각각 2개의 질문을 제시
- 5‑point Likert(1~5) 로 점수 집계 → 차원별 최고점 → MBTI 코드 도출
- 결과 페이지에 유형 설명, 직업·팀 역할 추천, 시각화 포함
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# ------------------- 1. 페이지 설정 -------------------
st.set_page_config(
    page_title="MBTI Explorer",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🧠 MBTI 성격 유형 탐색기")
st.markdown(
    """
    MBTI는 **Myers‑Briggs Type Indicator** 로,
    4가지 차원(외향/내향, 감각/직관, 사고/감정, 판단/인식) 의 조합으로 16가지 유형을 나타냅니다.
    아래 설문에 답하면 당신과 가장 가까운 MBTI 유형을 추정해 드립니다!
    """
)

# ------------------- 2. 설문 데이터 -------------------
# 차원별 질문 리스트 (각 차원 2개)
survey_data = {
    "외향/내향": {
        "question": [
            "새로운 사람을 만나는 것이 즐거운가요?",
            "혼자 있는 시간이 필요하다고 생각하나요?"
        ],
        "points": [1, 2],          # 낮은 점수 = 내향, 높은 점수 = 외향
    },
    "감각/직관": {
        "question": [
            "세부적인 사실·정보를 중시하나요?",
            "큰 그림·가능성을 추구하는 편인가요?"
        ],
        "points": [1, 2],
    },
    "사고/감정": {
        "question": [
            "논리와 객관적 사실을 우선시하나요?",
            "사람들의 감정과 가치를 고려하나요?"
        ],
        "points": [1, 2],
    },
    "판단/인식": {
        "question": [
            "계획을 세우고 지키려는 편인가요?",
            "유연하고 즉흥적인 상황에서 더 편안하게 느끼나요?"
        ],
        "points": [1, 2],
    },
}

# ------------------- 3. 설문 진행 -------------------
st.sidebar.header("▶ MBTI 설문")
user_answers = []

for dim, d in survey_data.items():
    st.sidebar.subheader(f"🟢 차원: {dim}")
    for i, q in enumerate(d["question"], 1):
        points = st.sidebar.slider(q, 1, 5, 3, step=1)
        user_answers.append({"dimension": dim, "question_idx": i, "score": points})

# ------------------- 4. 점수 집계 & 유형 추정 -------------------
answers_df = pd.DataFrame(user_answers)

# 차원별 점수 합계
dim_scored = answers_df.groupby("dimension")["score"].sum().reset_index()

# 가장 높은 점수를 받은 차원을 선택
max_dim = dim_scored.loc[dim_scored["score"].idxmax(), "dimension"]
# 해당 차원의 최고 점수 (1~5)
max_score = dim_scored.loc[dim_scored["score"].idxmax(), "score"]

# 차원별 점수 순위 (내림차순) → MBTI 코드 순서 (E/I, S/N, T/F, J/P)
# 여기서는 가장 높은 차원을 기준으로 코드를 만든다.
# 실제 MBTI 검사는 20문항 이상이지만, 학습용 간단 버전이다.
def get_mbti_code(dimension, score):
    """dimension에 따라 1~5점 중 어느쪽에 가까운지 판단해서 코드 반환"""
    if dimension in ["외향/내향"]:
        return "E" if score >= 4 else "I"
    elif dimension in ["감각/직관"]:
        return "S" if score >= 4 else "N"
    elif dimension in ["사고/감정"]:
        return "T" if score >= 4 else "F"
    elif dimension in ["판단/인식"]:
        return "J" if score >= 4 else "P"

# 4차원 모두 같은 방식으로 점수 사용 (간단히)
e_i = get_mbti_code("외향/내향", dim_scored.loc[dim_scored["dimension"]=="외향/내향", "score"].max())
s_n = get_mbti_code("감각/직관", dim_scored.loc[dim_scored["dimension"]=="감각/직관", "score"].max())
t_f = get_mbti_code("사고/감정", dim_scored.loc[dim_scored["dimension"]=="사고/감정", "score"].max())
j_p = get_mbti_code("판단/인식", dim_scored.loc[dim_scored["dimension"]=="판단/인식", "score"].max())

mbti_code = f"{e_i}{s_n}{t_f}{j_p}"

# ------------------- 5. 결과 페이지 -------------------
st.header("📊 검사 결과")
st.write(f"**추정 MBTI 유형:** {mbti_code.upper()}")

# 차원별 점수 표
st.subheader("📈 차원별 점수")
chart_df = pd.DataFrame(
    {
        "Dimension": ["외향/내향", "감각/직관", "사고/감정", "판단/인식"],
        "Score": dim_scored["score"].tolist()
    }
)
st.dataframe(chart_df.style.highlight_max(color="lightgreen"))

# 유형 설명 (간략)
def show_mbti_info(code):
    info = {
        "ESFP": "활동적이고 자유로운 영혼, 사람들과의 교류를 즐기며 언제든지 새로운 경험을 찾는다.",
        "ENFP": "열정적인 아이디어 제공자, 가능성을 탐구하고 사람들을 고무한다.",
        "ENTJ": "전략가, 목표와 비전을 가지고 조직을 이끈다.",
        "INTJ": "전략적인 비전가, 복잡한 문제를 구조적으로 해결한다.",
        "INFP": "이상주의자, 가치와 신념에 따라 살아간다.",
        "INFJ": "예언가, 깊은 통찰력으로 타인의 마음을 이해한다.",
        "ISTJ": "책임감 강한 관리자, 규칙과 전통을 중시한다.",
        "ISFJ": "보호자, 타인을 돌보는 현실적인 성향.",
        "ISTP": "실용적인 문제 해결사, 직접 체험을 선호한다.",
        "ISFP": "예술가, 조용하고 감각적인 생활 방식을 좋아한다.",
        "ESTP": "행동가, 즉각적인 반응을 보이며 모험을 즐긴다.",
        "ESFJ": "배려형 사회인, 조화를 중시하고 타인을 돕는다.",
        "ESTJ": "리더형 관리자, 조직적이고 실용적인 결정을 내린다.",
        "ENTP": "논쟁가, 새로운 아이디어와 도전을 즐긴다.",
        "ENFJ": "영감을 주는 리더, 사람들의 잠재력을 끌어낸다.",
        "ENFJ": "조화로운 인간관계 전문가, 타인을 격려하고 연결한다."
    }
    return info.get(code, "해당 유형에 대한 정보가 없습니다.")

info = show_mbti_info(mbti_code.upper())
st.write(info)

# 추천 직업·팀 역할 (간단 리스트)
occupation_map = {
    "ESFP": ["연예인, 예술가, 마케터, 이벤트 플래너"],
    "ENFP": ["교육자, 작가, 기업가, 상담사"],
    "ENTJ": ["전략 컨설턴트, 프로젝트 매니저, 경영진"],
    "INTJ": ["소프트웨어 엔지니어, 연구원, 데이터 과학자"],
    "INFP": ["사회복지사, 작가, 심리 상담사"],
    "INFJ": ["코치, HR, 비영리단체 리더"],
    "ISTJ": ["회계사, 품질관리, 행정직"],
    "ISFJ": ["간호사, 교사, 행정지원"],
    "ISTP": ["기술 엔지니어, 메카닉, 프리랜서 개발자"],
    "ISFP": ["디자이너, 요리사, 프리랜서 작가"],
    "ESTP": ["영업, 트레이너, 이벤트 코디네이터"],
    "ESFJ": ["고객 서비스, 행사 기획, HR"],
    "ESTJ": ["프로젝트 매니저, 군인, 행정관"],
    "ENTP": ["발명가, 컨설턴트, 언론인"],
    "ENFJ": ["교육자, 팀 리더, HR"]
}

rec_jobs = occupation_map.get(mbti_code.upper(), "추천 직업 정보가 없습니다.")
st.subheader("💼 추천 직업")
st.write(rec_jobs)

# 팀 역할 (리더십·팔로워 역할) 간단히 매핑
role_map = {
    "ISTJ": ["데이터 분석가", "품질 관리"],
    "ISFJ": ["팀 서포터", "문서 담당자"],
    "ESFJ": ["팀 서포터", "커뮤니케이션 담당"],
    "ESTJ": ["팀 리더", "프로젝트 매니저"],
    "INFJ": ["전략가", "멘토링 담당자"],
    "INFP": ["크리에이티브", "감성 코치"],
    "INTJ": ["전략가", "아키텍트"],
    "ISTP": ["기술 전문가", "문제 해결사"],
    "ISFP": ["디자이너", "크리에이티브"],
    "ESTP": ["프로모터", "현장 실행자"],
    "ENFP": ["아이디어 제너레이터", "팀 분위기 메이커"],
    "ENFJ": ["팀 리더", "동기부여자"],
    "ENTJ": ["전략가", "결정권자"],
    "ENTP": ["혁신가", "디베이트 챔피언"],
}

roles = role_map.get(mbti_code.upper())
if roles:
    st.subheader("🧩 팀 내 역할")
    st.write(f"- **리더십 역할:** {roles[0]}")
    st.write(f"- **팔로워 역할:** {roles[1]}")
else:
    st.write("역할 매핑 정보가 없습니다.")

# 차원별 점수 막대 차트
st.subheader("📊 차원별 점수 (1~5)")
chart_df["Score"] = pd.to_numeric(chart_df["Score"])
st.bar_chart(chart_df.set_index("Dimension")["Score"], use_container_width=True)

# ------------------- 6. 참고·링크 -------------------
st.sidebar.markdown("---")
st.sidebar.info(
    """
    📌 **MBTI 검사 참고**  
    - 실제 MBTI는 20문항, 4차원 각각 5문항씩 사용합니다.  
    - 여기서는 교육·데모용으로 간단히 구현했으며, 정확한 유형을 원하시면 정식 검사를 권장합니다.
    """
)

st.sidebar.markdown("[🔎 MBTI 공식 정보 (공식 MBTI 연구소)](https://www.myersbriggs.org/)")
