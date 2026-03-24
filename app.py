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
st.set_page_config(page_title="작혼 전적 정리기", page_icon="icon.png", layout="centered")

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
        st.image(final_image, caption="입력된 이미지", use_column_width=True)

st.divider()

# ------------------------------------------------
# 3. 데이터 추출 및 유사도 교정 로직
# ------------------------------------------------
if st.button("🚀 결과 텍스트 추출하기", use_container_width=True):
    if final_image is None or not game_number or not start_time:
        st.error("이미지, 게임 번호, 시작 시간은 필수입니다!")
    else:
        with st.spinner("AI가 이미지를 분석 중입니다..."):
            try:
                # 1. AI API 호출 및 명단 기반 인식
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                final_image.thumbnail((1024, 1024)) 

                prompt = f"""
                이 이미지는 마작 게임 작혼의 결과 화면이야. 
                1. 1위부터 4위까지의 '순위(rank)', '닉네임(nickname)', '점수(score)'를 추출해줘.
                * 주의: 플레이어의 닉네임은 반드시 다음 명단 중에서 가장 비슷한 것을 골라서 적어! 글자가 뭉개졌어도 무조건 이 안에서 찾아야 해.
                [명단: {', '.join(VALID_NICKNAMES)}]
                
                2. 화면(주로 우측 하단)에 '종료시간(end_time, HH:MM 형식)'이 있다면 추출하고, 만약 화면에 시간이 아예 없다면 end_time 값으로 빈 문자열("")을 줘.
                반드시 아래 JSON 형식으로만 대답해. 마크다운 기호 없이 순수 JSON 텍스트만 출력해.
                {{"end_time": "22:21", "players": [{{"rank": 1, "nickname": "gtrhdea", "score": 33900}}]}}
                """
                response = model.generate_content([prompt, final_image])
                result_text = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(result_text)

                # 2. 종료 시간 처리 (수동 입력 최우선)
                ai_end_time = data.get("end_time", "").replace(":", "")
                final_end_time = end_time_input if end_time_input else ai_end_time
                
                if not final_end_time:
                    st.warning("⚠️ 사진에서 종료 시간을 찾지 못했습니다. 왼쪽 '종료 시간' 칸에 직접 입력해 주세요!")
                    st.stop()

                # 3. 텍스트 조립 및 difflib 유사도 기반 오타 자동 교정
                final_text = f"{game_number}\n{start_time}~{final_end_time}\n"
                players = sorted(data["players"], key=lambda x: x["rank"])
                
                for player in players:
                    rank = player["rank"]
                    ai_nickname = player["nickname"].strip()
                    score = player["score"]
                    
                    # AI가 읽어온 이름이 사전에 없다면, 가장 비슷한 이름을 찾아냄 (일치율 40% 이상)
                    if ai_nickname not in NAME_DICTIONARY:
                        closest_matches = difflib.get_close_matches(ai_nickname, NAME_DICTIONARY.keys(), n=1, cutoff=0.4)
                        if closest_matches:
                            ai_nickname = closest_matches[0] 

                    # 최종적으로 실제 이름(본명)으로 변환
                    real_name = NAME_DICTIONARY.get(ai_nickname, ai_nickname)
                    uma_str = calculate_uma(score)
                    final_text += f"{rank}. {real_name} {score} {uma_str}\n"

                # 4. 결과 출력
                st.success("✨ 추출이 완료되었습니다! 아래 상자 오른쪽 위의 📋 복사 아이콘을 누르세요.")
                st.code(final_text, language="plaintext")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")