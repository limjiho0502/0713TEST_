import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="서울·양평 기온 및 전력수요 분석", layout="wide")
st.title("🌡️ 서울·양평 기온과 전력수요 분석 웹앱")

# 2. 데이터 로드 및 전처리 (캐싱으로 성능 최적화)
@st.cache_data
def load_data():
    # 데이터 불러오기 (CP949 인코딩 반영)
    seoul_df = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong_df = pd.read_csv("양평_기온.csv", encoding="cp949")
    power_df = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    seoul_df['일시'] = pd.to_datetime(seoul_df['일시'])
    yangpyeong_df['일시'] = pd.to_datetime(yangpyeong_df['일시'])
    power_df['일시'] = pd.to_datetime(power_df['일시'])
    
    # 필요한 열 선택 및 이름 변경
    seoul_df = seoul_df[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울_기온'})
    yangpyeong_df = yangpyeong_df[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평_기온'})
    
    # [탭1 데이터] 서울과 양평 기온 병합
    df_temp = pd.merge(seoul_df, yangpyeong_df, on='일시', how='inner')
    df_temp['기온차(서울-양평)'] = df_temp['서울_기온'] - df_temp['양평_기온']
    df_temp['월'] = df_temp['일시'].dt.month
    df_temp['시각'] = df_temp['일시'].dt.hour
    
    # [탭2 데이터] 서울 기온과 전력수요 병합
    df_power = pd.merge(seoul_df, power_df, on='일시', how='inner')
    df_power['월'] = df_power['일시'].dt.month
    
    # 기온 구간 생성 (예: 5도 단위 구간)
    bins = list(range(-20, 45, 5))
    labels = [f"{i} ~ {i+5}°C" for i in bins[:-1]]
    df_power['기온구간'] = pd.cut(df_power['서울_기온'], bins=bins, labels=labels, right=False)
    
    return df_temp, df_power

# 데이터 로드 예외 처리
try:
    df_temp, df_power = load_data()
except Exception as e:
    st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다. 파일명과 위치를 확인해주세요.\n오류내용: {e}")
    st.stop()

# 3. 탭 구성
tab1, tab2 = st.tabs(["🔥 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])

# --- [탭1: 열섬 분석] ---
with tab1:
    st.header("서울과 양평의 기온 비교 (도시 열섬현상)")
    
    # ① 1년간 두 지역 기온 변화 (선그래프)
    st.subheader("① 1년간 두 지역 기온 변화")
    df_line = df_temp.sort_values('일시').set_index('일시')[['서울_기온', '양평_기온']]
    st.line_chart(df_line)
    
    # 가로로 배치하기 위해 컬럼 분할
    col1, col2 = st.columns(2)
    
    with col1:
        # ② 시각(0~23시)별 평균 기온차
        st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
        df_hour = df_temp.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
        st.bar_chart(df_hour.set_index('시각'))
        
    with col2:
        # ③ 월(1~12월)별 평균 기온차
        st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
        df_month = df_temp.groupby('월')['기온차(서울-양평)'].mean().reset_index()
        st.bar_chart(df_month.set_index('월'))


# --- [탭2: 전력 연결] ---
with tab2:
    st.header("서울 기온과 전력수요의 상관관계")
    
    # ① 기온(가로)과 전력수요(세로)의 산점도
    st.subheader("① 기온과 전력수요 산점도")
    st.scatter_chart(data=df_power, x='서울_기온', y='전력수요(MWh)')
    
    # 가로로 배치하기 위해 컬럼 분할
    col3, col4 = st.columns(2)
    
    with col3:
        # ② 기온 구간별 평균 전력수요
        st.subheader("② 기온 구간별 평균 전력수요")
        # observed=False는 빈 구간도 포함하여 연산하되 경고를 방지하기 위함입니다.
        df_bin = df_power.groupby('기온구간', observed=False)['전력수요(MWh)'].mean().reset_index()
        st.bar_chart(df_bin.set_index('기온구간'))
        
    with col4:
        # ③ 월(1~12월)별 평균 전력수요
        st.subheader("③ 월별 평균 전력수요")
        df_month_p = df_power.groupby('월')['전력수요(MWh)'].mean().reset_index()
        st.bar_chart(df_month_p.set_index('월'))
    st.bar_chart(df_month.set_index('월'))
    st.caption("계절별로 도시와 외곽 지역 간의 복사 냉각 및 인공열 발생 차이에 따른 변화를 볼 수 있습니다.")
