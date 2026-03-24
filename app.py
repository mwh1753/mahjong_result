import streamlit as st
import google.generativeai as genai
import json
from PIL import Image
from streamlit_paste_button import paste_image_button

# ------------------------------------------------
# 1. 닉네임 사전 및 우마 계산 함수 (초대규모 오타 방어망 적용)
NAME_DICTIONARY = {
    # ---------------------------------------------
    # 🔠 알파벳/숫자 혼동 완벽 방어 (l, I, 1, e, c, n, m, 0, o)
    # ---------------------------------------------
    "keichi": "정훈", "kelchi": "정훈", "ketchi": "정훈", "keichl": "정훈", "keich1": "정훈", "k0ichi": "정훈",
    "sleeeeeeeep": "도균", "sleeeeeeep": "도균", "sleeeeeeeeep": "도균", "s1eeeeeeeep": "도균", "sIeeeeeeeep": "도균", "sleeeeeeeep": "도균",
    "koyume": "동욱", "koynme": "동욱", "kcyume": "동욱", "k0yume": "동욱", "keyume": "동욱",
    "babysunfish": "선일", "babysunf1sh": "선일", "hahysunfish": "선일", "babysuntish": "선일",
    "jeezjz": "지성", "jeezj2": "지성", "jee2jz": "지성", "jeczjz": "지성", "jeczj2": "지성",
    "MANKURU": "태욱", "MANKURV": "태욱", "MANKUKU": "태욱", "MANKUPU": "태욱",
    "lecon": "동희", "Iecon": "동희", "1econ": "동희", "lacon": "동희", "lceon": "동희",
    "tminid": "박정우", "tminld": "박정우", "tmInid": "박정우", "tmin1d": "박정우", "tminjd": "박정우",
    "Maeil": "근협", "MaeiI": "근협", "Maei1": "근협", "Meeil": "근협", "MaelI": "근협",
    "wakhang": "정완", "wakhong": "정완", "wekhang": "정완", "wakheng": "정완",
    "joyhome": "이정우", "jcyhome": "이정우", "joyhoma": "이정우", "j0yhome": "이정우", "juyhome": "이정우",
    "gtrhdea": "정학", "gtrhdee": "정학", "ytrhdea": "정학", "gtrhdoa": "정학",
    "Reippah": "종현", "Reippeh": "종현", "Relppah": "종현", "ReIppah": "종현", "Re1ppah": "종현",
    "hoshizoraaaa": "창민", "hoshizoraaa": "창민", "hoshlzoraaaa": "창민", "hoshizoreaaa": "창민",
    "zxxzxx": "승현", "2xx2xx": "승현", "zxx2xx": "승현", "zxxzXx": "승현",
    "lJpuddingl": "재형", "1Jpudding1": "재형", "IJpuddingI": "재형", "lJpudding1": "재형", "lJpudd1ngl": "재형",
    "Kyorang": "교창", "Kyarang": "교창", "Kyoreng": "교창", "Ky0rang": "교창",

    # ---------------------------------------------
    # 🇰🇷 한글 자음/모음/받침 혼동 완벽 방어
    # ---------------------------------------------
    "이쁜괜티": "규빈", "이쁜괜히": "규빈", "이픈괜티": "규빈", "이쁜쾐티": "규빈", "아쁜괜티": "규빈", "이쁜관티": "규빈", "이쁜권티": "규빈", "이쁜괜다": "규빈",
    "김근머": "근영", "김근며": "근영", "길근머": "근영", "감근머": "근영", "킴근머": "근영", "김긴머": "근영", "김근미": "근영",
    "테라짐": "도헌", "데라짐": "도헌", "테라잠": "도헌", "톄라짐": "도헌", "터라짐": "도헌", "테리짐": "도헌",
    "하루를영원히": "민철", "하루룰영원히": "민철", "하루를영원히": "민철", "하루를영윈히": "민철", "히루를영원히": "민철", "하루를영원히": "민철", "하루를영원하": "민철",
    "넘버걸": "범진", "넙버걸": "범진", "넘버결": "범진", "님버걸": "범진", "넘버길": "범진", "넌버걸": "범진",
    "새벽녕": "재현", "새벽명": "재현", "세벽녕": "재현", "새벽령": "재현", "새벽넝": "재현", "새벽영": "재현",
    "제라툴": "재훈", "계라툴": "재훈", "재라툴": "재훈", "제리툴": "재훈", "제라틀": "재훈",
    "시나몬샐러드": "나경", "시나몬셀러드": "나경", "사나몬샐러드": "나경", "시나몬살러드": "나경", "시나문샐러드": "나경",
    "쉿자는중": "지완", "찻자는중": "지완", "숫자는중": "지완", "솟자는중": "지완", "찾자는중": "지완", "쉿자느중": "지완", "쉿지눈중": "지완", "쉿자는종": "지완",
    "오천리더": "재윤", "으천리더": "재윤", "오천라더": "재윤", "오친리더": "재윤", "어천리더": "재윤", "옴천리더": "재윤",
    "닷시마": "혜림", "딧시마": "혜림", "닫시마": "혜림", "맛시마": "혜림", "닺시마": "혜림", "댯시마": "혜림", "단시마": "혜림", "닽시마": "혜림",
    "스도리": "태민", "스도라": "태민", "츠도리": "태민", "스두리": "태민", "수도리": "태민",
    "찐빵vs호빵": "두찬", "찐빵vS호빵": "두찬", "찐빵VS호빵": "두찬", "짠빵vs호빵": "두찬", "찐빵vs후빵": "두찬", "찐방vs호빵": "두찬", "찐빵vs호방": "두찬",
    "밤하늘먹구름": "승훈", "밤하늘벅구름": "승훈", "밤하늘먹꾸름": "승훈", "빔하늘먹구름": "승훈", "밤하닐먹구름": "승훈", "밤하늘먹구림": "승훈",
    "소외감": "우영", "소의감": "우영", "스외감": "우영", "쇠외감": "우영", "초외감": "우영", "소외강": "우영", "수외감": "우영",
    "가우르구라원툴": "상현", "가오르구라원툴": "상현", "기우르구라원툴": "상현", "가우르구리원툴": "상현", "가우르구라원틀": "상현",
    "실루엣": "우재", "쉴루엣": "우재", "설루엣": "우재", "살루엣": "우재", "실루엇": "우재", "실루엔": "우재",
    "한국의기술": "유준", "한극의기술": "유준", "한국이기술": "유준", "힌국의기술": "유준", "한국의가술": "유준",

    # ---------------------------------------------
    # 🇯🇵 일본어/한자/특수기호 혼동 완벽 방어
    # ---------------------------------------------
    "うああつあ": "우혁", "うあぁつあ": "우혁", "ぅああつあ": "우혁", "5ああつあ": "우혁", "うおあつあ": "우혁",
    "平澤文": "기형", "平沢文": "기형", "乎澤文": "기형", "苹澤文": "기형", "平洋文": "기형",
    "あやフブミオ": "재욱", "あやフプミオ": "재욱", "あやフフミオ": "재욱", "おやフブミオ": "재욱"
}

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
        st.image(final_image, caption="입력된 이미지", use_column_width=True)

st.divider()

# ------------------------------------------------
# 3. 데이터 추출 로직
# ------------------------------------------------
if st.button("🚀 결과 텍스트 추출하기", use_container_width=True):
    if final_image is None or not game_number or not start_time:
        st.error("이미지, 게임 번호, 시작 시간은 필수입니다!")
    else:
        with st.spinner("AI가 이미지를 분석 중입니다..."):
            try:
                # 비밀 금고에서 API 키 가져오기
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                
                model = genai.GenerativeModel('gemini-2.5-flash')
                final_image.thumbnail((1024, 1024)) 

                prompt = """
                이 이미지는 마작 게임 작혼의 결과 화면이야. 
                1. 1위부터 4위까지의 '순위(rank)', '닉네임(nickname)', '점수(score)'를 추출해줘.
                2. 화면(주로 우측 하단)에 '종료시간(end_time, HH:MM 형식)'이 있다면 추출하고, 만약 화면에 시간이 아예 없다면 end_time 값으로 빈 문자열("")을 줘.
                반드시 아래 JSON 형식으로만 대답해. 마크다운 기호 없이 순수 JSON 텍스트만 출력해.
                {"end_time": "22:21", "players": [{"rank": 1, "nickname": "gtrhdea", "score": 33900}]}
                """
                
                response = model.generate_content([prompt, final_image])
                result_text = response.text.strip().replace("```json", "").replace("```", "")
                data = json.loads(result_text)

                # 하이브리드 시간 로직: 내가 쓴 값 > AI가 찾은 값
                ai_end_time = data.get("end_time", "").replace(":", "")
                final_end_time = end_time_input if end_time_input else ai_end_time
                
                # 둘 다 없다면 에러 메시지
                if not final_end_time:
                    st.warning("⚠️ 사진에서 종료 시간을 찾지 못했습니다. 왼쪽 '종료 시간' 칸에 직접 입력해 주세요!")
                    st.stop()

                final_text = f"{game_number}\n{start_time}~{final_end_time}\n"
                
                players = sorted(data["players"], key=lambda x: x["rank"])
                for player in players:
                    rank = player["rank"]
                    nickname = player["nickname"]
                    score = player["score"]
                    
                    real_name = NAME_DICTIONARY.get(nickname.strip(), nickname)
                    uma_str = calculate_uma(score)
                    final_text += f"{rank}. {real_name} {score} {uma_str}\n"

                st.success("✨ 추출이 완료되었습니다! 아래 상자 오른쪽 위의 📋 복사 아이콘을 누르세요.")
                # 🌟 결과 텍스트를 복사 버튼이 있는 코드 블록으로 출력
                st.code(final_text, language="plaintext")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")