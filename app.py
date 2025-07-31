import streamlit as st
import pandas as pd
from datetime import datetime

# --- Google Sheet에서 CSV로 데이터 로드 함수 ---
@st.cache_data(ttl=300) # 300초(5분)마다 캐시 갱신
def load_news_data_from_csv(csv_url):
    try:
        # 웹에 게시된 CSV 파일에서 직접 데이터 읽기
        df = pd.read_csv(csv_url) # pandas를 사용하여 CSV URL에서 데이터 읽기

        # 데이터 전처리 (이전과 동일: 발행일, 총점 변환 등)
        if '발행일' in df.columns:
            def parse_date(date_str):
                if pd.isna(date_str): return pd.NaT
                date_str = str(date_str).strip()
                try: 
                    if ' +' in date_str: date_str = date_str.split(' +')[0]
                    return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S')
                except ValueError:
                    try: 
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except ValueError:
                        return pd.NaT
            df['발행일'] = df['발행일'].apply(parse_date)

        if '총점' in df.columns:
            df['총점'] = pd.to_numeric(df['총점'], errors='coerce').fillna(0)

        df = df.dropna(how='all')

        return df.to_dict('records')
    except Exception as e:
        st.error(f"CSV 데이터를 로드하는 중 오류 발생: {e}")
        st.info("Google Sheet가 CSV로 제대로 게시되었는지, URL이 올바른지 확인해주세요.")
        return []

st.set_page_config(layout="wide")
st.title("📰 오늘의 SK 뉴스 클리핑 (Gemini 중요도 평가)")

st.sidebar.header("설정")
num_articles_to_show = st.sidebar.slider("표시할 기사 수", 1, 50, 5)

# ★ 여기에 웹에 게시된 CSV URL을 붙여넣으세요! (반드시 쌍따옴표 안에!)
csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vStTkfygze7Y_6ZCiUiJNTCHDmaniooxZWdKmvZLOOjK25NPfc-6i7Or6d4MQRgRS-S3po6pUychIMD/pub?output=csv" 

news_articles = load_news_data_from_csv(csv_url)

if news_articles:
    # 총점과 발행일(datetime 객체) 기준으로 내림차순 정렬
    news_articles.sort(key=lambda x: (x.get('총점', 0), x.get('발행일', datetime.min)), reverse=True)

    display_articles = news_articles[:num_articles_to_show]

    st.header(f"중요도별 최신 {len(display_articles)}개 기사 목록")

    for article in display_articles:
        st.subheader(f"[{article.get('중요도 등급', '미정')}] {article.get('제목', '제목 없음')}")

        published_date_str = article.get('발행일', '날짜 없음')
        if isinstance(published_date_str, datetime):
            published_date_str = published_date_str.strftime('%Y-%m-%d %H:%M')

        st.markdown(f"**총점:** {article.get('총점', 0)}점 | **발행일:** {published_date_str} | **언론사:** {article.get('언론사', '정보 없음')}")
        st.write(f"**요약:** {article.get('요약', '요약 없음')}")
        st.write(f"**LLM 평가:** {article.get('LLM 평가 요약', 'LLM 평가 요약 없음')}")
        st.markdown(f"[기사 원문 보기]({article.get('링크', '#')})")
        st.markdown("---")
else:
    st.info(f"뉴스 데이터를 찾을 수 없습니다. Google Sheet가 CSV로 제대로 게시되었는지, URL이 올바른지 확인해주세요.")

st.sidebar.markdown("Made with ❤️ by Gemini")

if st.button("데이터 새로고침"):
    st.cache_data.clear()
    st.experimental_rerun()
