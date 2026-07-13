import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="서울·양평 열섬현상 분석", layout="wide")
st.title("🌡️ 서울-양평 기온 비교를 통한 도시 열섬현상 분석")
st.markdown("2025년 시간별 기온 데이터를 바탕으로 도시(서울)와 외곽(양평)의 기온 차이를 분석합니다.")

# 2. 데이터 데이터 로드 및 전처리 (캐싱으로 성능 최적화)
@st.cache_data
def load_and_process_data():
    # 데이터 읽기 (CP949 인코딩 적용)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    
    # 필요한 컬럼만 추출하고 이름 변경
    seoul = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울 기온'})
    yangpyeong = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평 기온'})
    
    # 일시를 기준으로 두 데이터 병합 (같은 일시끼리 매칭)
    df = pd.merge(seoul, yangpyeong, on='일시', how='inner')
    
    # 기온차(서울 - 양평) 계산 및 월/시각 변수 생성
    df['기온차(서울-양평)'] = df['서울 기온'] - df['양평 기온']
    df['월'] = df['일시'].dt.month
    df['시각'] = df['일시'].dt.hour
    
    return df

# 데이터 불러오기 예외 처리
try:
    df = load_and_process_data()
except Exception as e:
    st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다. 파일명과 위치를 확인해주세요. (오류 내용: {e})")
    st.stop()

# -----------------------------------------------------------------------------
# 3. 그래프 시각화
# -----------------------------------------------------------------------------

# ① 1년간 두 지역의 기온 변화 (선그래프)
st.subheader("① 1년간 두 지역의 기온 변화")
# 차트 전용 데이터프레임 생성 (시계열 선그래프는 인덱스가 X축이 됩니다)
df_line = df.sort_values('일시').set_index('일시')[['서울 기온', '양평 기온']]
st.line_chart(df_line)

st.markdown("---")

# 레이아웃을 2개의 컬럼으로 분할하여 ②, ③ 그래프 배치
col1, col2 = st.columns(2)

# ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
with col1:
    st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
    df_hour = df.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
    # 시각을 인덱스로 설정하여 X축으로 지정
    st.bar_chart(df_hour.set_index('시각'))
    st.caption("주로 낮보다 대기가 안정되는 밤과 새벽 시간대에 도시 열섬현상(기온차 > 0)이 뚜렷하게 나타납니다.")

# ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
with col2:
    st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
    df_month = df.groupby('월')['기온차(서울-양평)'].mean().reset_index()
    # 월을 인덱스로 설정하여 X축으로 지정
    st.bar_chart(df_month.set_index('월'))
    st.caption("계절별로 도시와 외곽 지역 간의 복사 냉각 및 인공열 발생 차이에 따른 변화를 볼 수 있습니다.")
