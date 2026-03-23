import streamlit as st
import google.generativeai as genai
import json
from PIL import Image

# ------------------------------------------------
# 1. 닉네임 사전 및 우마 계산 함수 설정
# ------------------------------------------------
NAME_DICTIONARY = {
    "keichi": "정훈",
    "sleeeeeeeep": "도균",
    "이쁜괜티": "규빈",
    "김근머": "근영",
    "테라짐": "도헌",
    "koyume": "동욱",
    "하루를영원히": "민철",
    "넘버걸": "범진",
    "babysunfish": "선일",
    "새벽녕": "재현",
    "jeezjz": "지성",
    "MANKURU": "태욱",
    "제라툴": "재훈",
    "うああつあ": "우혁",
    "lecon": "동희",
    "平澤文": "기형",
    "시나몬샐러드": "나경",
    "tminid": "박정우",
    "쉿자는중": "지완",
    "Maeil": "근협",
    "오천리더": "재윤",
    "닷시마": "혜림",
    "wakhang": "정완",
    "あやフブミオ": "재욱",
    "스도리": "태민",
    "찐빵vs호빵": "두찬",
    "밤하늘먹구름": "승훈",
    "joyhome": "이정우",
    "gtrhdea": "정학",
    "Reippah": "종현",
    "hoshizoraaaa": "창민",
    "소외감": "우영",
    "zxxzxx": "승현",
    "lJpuddingl": "재형",
    "가우르구라원툴": "상현",
    "실루엣": "우재",
    "한국의기술": "유준",
    "Kyorang": "교창"
}

def calculate_uma(score):
    uma = (score - 25000) / 1000.0
    if uma > 0:
        return f"+{uma:.1f}"
    else:
        return f"{uma:.1f}"

# ------------------------------------------------
# 2. 웹 앱 화면 구성 (UI)
# ------------------------------------------------
st.set_page_config(page_title="작혼 전적 정리기", page_icon="🀄", layout="centered")

st.title("🀄 작혼 전적 자동 정리 도구")
st.markdown("이미지를 업로드하고 정보를 입력하면 텍스트로 자동 변환해 줍니다.")

# 사이드바 (API 키 입력란)
with st.sidebar:
    st.header("⚙️ 기본 설정")
    api_key = st.text_input("Gemini API Key를 입력하세요", type="password")
    st.markdown("[👉 API 키 무료 발급받기](https://aistudio.google.com/app/apikey)")

# 메인 화면 레이아웃 분할
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("결과 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])
    game_number = st.text_input("게임 번호를 입력하세요", placeholder="예: 228")
    start_time = st.text_input("시작 시간을 입력하세요", placeholder="예: 2322")

with col2:
    if uploaded_file is not None:
        st.image(uploaded_file, caption="업로드된 이미지 미리보기", use_column_width=True)

# ------------------------------------------------
# 3. 데이터 추출 및 출력 로직
# ------------------------------------------------
st.divider()

if st.button("🚀 결과 텍스트 추출하기", use_container_width=True):
    # 필수 입력값 확인
    if not api_key:
        st.error("왼쪽 사이드바에 API 키를 먼저 입력해 주세요!")
    elif not uploaded_file:
        st.error("이미지를 업로드해 주세요!")
    elif not game_number:
        st.error("게임 번호를 입력해 주세요!")
    elif not start_time:
        st.error("시작 시간을 입력해 주세요!")
    else:
        with st.spinner("AI가 이미지를 분석 중입니다... (약 2~3초 소요)"):
            try:
                # API 설정 및 이미지 로드 (최신 2.5 모델 적용)
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                img = Image.open(uploaded_file)
                # 전송 속도를 높이기 위해 이미지 크기 압축
                img.thumbnail((1024, 1024)) 

                # AI 프롬프트
                prompt = """
                이 이미지는 마작 게임 작혼의 결과 화면이야. 
                1위부터 4위까지의 '순위(rank)', '닉네임(nickname)', '점수(score)'와 화면 우측 하단에 있는 '종료시간(end_time, HH:MM 형식)'을 추출해줘.
                결과는 반드시 아래 JSON 형식으로만 대답해. 마크다운 기호 없이 순수 JSON 텍스트만 출력해.
                {
                  "end_time": "22:21",
                  "players": [
                    {"rank": 1, "nickname": "gtrhdea", "score": 33900},
                    {"rank": 2, "nickname": "하루를영원히", "score": 33300},
                    {"rank": 3, "nickname": "joyhome", "score": 29000},
                    {"rank": 4, "nickname": "닷시마", "score": 3800}
                  ]
                }
                """
                
                response = model.generate_content([prompt, img])
                
                # 결과 텍스트 파싱
                result_text = response.text.strip()
                if result_text.startswith("```json"):
                    result_text = result_text[7:]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]
                
                data = json.loads(result_text.strip())

                # 시간 포맷팅
                end_time_raw = data.get("end_time", "00:00")
                end_time_str = end_time_raw.replace(":", "")

                # 🌟 최종 텍스트 조립 (게임 번호 먼저 출력)
                final_text = f"{game_number}\n"
                final_text += f"{start_time}~{end_time_str}\n"
                
                players = sorted(data["players"], key=lambda x: x["rank"])
                for player in players:
                    rank = player["rank"]
                    nickname = player["nickname"]
                    score = player["score"]
                    
                    # 닉네임 앞뒤 공백을 제거(.strip())하여 사전에서 더 정확하게 찾도록 개선
                    real_name = NAME_DICTIONARY.get(nickname.strip(), nickname)
                    uma_str = calculate_uma(score)
                    
                    final_text += f"{rank}. {real_name} {score} {uma_str}\n"

                st.success("✨ 추출이 완료되었습니다!")
                st.text_area("결과 (클릭해서 `Ctrl+C` 로 복사하세요)", final_text, height=180)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다. 다시 시도해 주세요.\n(상세 내용: {e})")