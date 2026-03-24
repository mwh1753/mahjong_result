import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
from streamlit_paste_button import paste_image_button # 🌟 새로운 부품 가져오기

# 1. 닉네임 사전 및 우마 계산 함수
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

def calculate_uma(score):
    uma = (score - 25000) / 1000.0
    return f"+{uma:.1f}" if uma > 0 else f"{uma:.1f}"

# 2. 웹 앱 화면 구성
st.set_page_config(page_title="작혼 전적 정리기", page_icon="🀄", layout="centered")
st.title("🀄 작혼 전적 자동 정리 도구")

col1, col2 = st.columns(2)
with col1:
    # 🌟 파일 업로더 대신 캡처본 바로 붙여넣기 버튼 생성
    st.write("이미지 입력 방식 (둘 중 하나 선택)")
    paste_result = paste_image_button("📋 캡처 후 여기를 클릭해 붙여넣기!", background_color="#e63946")
    uploaded_file = st.file_uploader("또는 파일로 찾아보기", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    
    st.divider()
    game_number = st.text_input("게임 번호를 입력하세요", placeholder="예: 228")
    start_time = st.text_input("시작 시간을 입력하세요", placeholder="예: 2322")
    end_time = st.text_input("종료 시간을 입력하세요", placeholder="예: 0028")

# 붙여넣기한 이미지 또는 업로드한 이미지 중 하나를 선택
final_image = None
if paste_result.image_data is not None:
    final_image = paste_result.image_data
elif uploaded_file is not None:
    final_image = Image.open(uploaded_file)

with col2:
    if final_image is not None:
        st.image(final_image, caption="입력된 이미지", use_column_width=True)

st.divider()

# 3. 데이터 추출 로직
if st.button("🚀 결과 텍스트 추출하기", use_container_width=True):
    if final_image is None or not game_number or not start_time or not end_time:
        st.error("이미지, 게임 번호, 시작 시간, 종료 시간을 모두 입력해 주세요!")
    else:
        with st.spinner("AI가 이미지를 분석 중입니다..."):
            try:
                # 비밀 금고에서 API 키 가져오기
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                
                model = genai.GenerativeModel('gemini-2.5-flash')
                final_image.thumbnail((1024, 1024)) 

                prompt = """
                이 이미지는 마작 게임 작혼의 결과 화면이야. 1위부터 4위까지의 '순위(rank)', '닉네임(nickname)', '점수(score)'만 추출해줘. 반드시 아래 JSON 형식으로만 대답해. 마크다운 기호 없이 순수 JSON 텍스트만 출력해.
                {"players": [{"rank": 1, "nickname": "gtrhdea", "score": 33900}]}
                """
                
                response = model.generate_content([prompt, final_image])
                result_text = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(result_text)

                final_text = f"{game_number}\n{start_time}~{end_time}\n"
                
                players = sorted(data["players"], key=lambda x: x["rank"])
                for player in players:
                    rank = player["rank"]
                    nickname = player["nickname"]
                    score = player["score"]
                    
                    real_name = NAME_DICTIONARY.get(nickname.strip(), nickname)
                    uma_str = calculate_uma(score)
                    final_text += f"{rank}. {real_name} {score} {uma_str}\n"

                st.success("✨ 추출이 완료되었습니다!")
                st.text_area("결과 (클릭해서 `Ctrl+C` 로 복사하세요)", final_text, height=180)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")