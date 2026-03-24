import streamlit as st
import google.generativeai as genai
import json
import difflib 
from PIL import Image
from streamlit_paste_button import paste_image_button

# ------------------------------------------------
# 1. 닉네임 사전 (순수 명단만 유지)
# ------------------------------------------------
NAME_DICTIONARY = {
    "keichi": "정훈", "sleeeeeeeep": "도균", "이쁜괜티": "규빈", "김근머": "근영",
    "테라짐": "도헌", "koyume": "동욱", "하루를영원히": "민철", "넘버걸": "범진",
    "babysunfish": "선일", "새벽녕": "재현", "jeezjz": "지성", "MANKURU": "태욱",
    "제라툴": "재훈", "うああつあ": "우혁", "lecon": "동희", "平澤文": "기형",
    "시나몬샐러드": "나경", "tminid": "박정우", "쉿자는중": "지완", "Maeil": "근협",
    "오천리더": "재윤", "닷시마": "혜림", "wakhang": "정완", "あやフブミオ": "재욱",
    "스도리": "태민", "찐빵vs호빵": "두찬", "밤하늘먹구름": "승훈", "joyhome": "이정우",
    "gtrhdea": "정학", "Reippah": "종현", "hoshizoraaaa": "창민", "소외감": "우영",
    "zxxzxx": "승현", "lJpuddingl": "재형", "가우르구라원툴": "상현", "실루엣": "우재",
    "한국의기술": "유준", "Kyorang": "교창"
}

# AI가 참고할 수 있게 닉네임 원본 명단만 따로 뽑아둠
VALID_NICKNAMES = list(NAME_DICTIONARY.keys())

def calculate_uma(score):
    uma = (score - 25000) / 1000.0
    return f"+{uma:.1f}" if uma > 0 else f"{uma:.1f}"

# ------------------------------------------------
# 2. 웹 앱 화면 구성
# ------------------------------------------------
st.set_page_config(page_title="작혼 전적 정리기", page_icon="🀄", layout="centered")
st.title("🀄 작혼 전적 자동 정리 도구")

col1, col2 = st.columns(2)
with col1:
    st.write("이미지 입력 방식 (둘 중 하나 선택)")
    paste_result = paste_image_button("📋 캡처 후 클릭해 붙여넣기!", background_color="#e63946")
    uploaded_file = st.file_uploader("또는 파일로 찾아보기", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    st.divider()
    game_number = st.text_input("게임 번호를 입력하세요", placeholder="예: 228")
    start_time = st.text_input("시작 시간을 입력하세요", placeholder="예: 2322")
    end_time_input = st.text_input("종료 시간 (사진에 없으면 입력하세요)", placeholder="예: 0028")

final_image = None
if paste_result.image_data is not None:
    final_image = paste_result.image_data
elif uploaded_file is not None:
    final_image = Image.open(uploaded_file)

with col2:
    if final_image is not None:
        st.image(final