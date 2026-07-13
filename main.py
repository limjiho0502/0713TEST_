import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 1. 페이지 및 레이아웃 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="서울·양평 기온 및 전력수요 분석", layout="wide")
st.title("🌡️ 서울·양평 기온 변화와 전력수요 분석")
st.markdown("도심(서울)과 교외(양평)의 데이터를 활용해 **열섬현상**과 **전력수요**의 관계를 분석합니다.")

# -----------------------------------------------------------------------------
# 2. 데이터 데이터 로드 및 전처리 (캐싱 적용)
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_process_data():
    # 파일 읽기 (요청하신 cp949 인코딩 적용)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 통일
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    power['일시'] = pd.to_datetime(power['일시'])
    
    # 필요한 열만 추출 및 이름 변경
    seoul = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울_기온'})
    yangpyeong = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평_기온'})
    
    # [탭1용] 서울 및 양평 기온 데이터 결합 (일시 기준)
    df_temp = pd.merge(seoul, yangpyeong, on='일시', how='inner')
    df_temp['기온차(서울-양평)'] = df_temp['서울_기온'] - df_temp['양평_기온']
    df_temp['월'] = df_temp['일시'].dt.month
    df_temp['시각'] = df_temp['일시'].dt.hour
    
    # [탭2용] 서울 기온과 전력수요 데이터 결합 (일시 기준)
    df_power = pd.merge(seoul, power, on='일시', how='inner')
    df_power['월'] = df_power['일시'].dt.month
    
    # 5도 단위 기온 구간 생성
    bins = list(range(-20, 45, 5))
    labels = [f"{i} ~ {i+5}°C" for i in bins[:-1]]
    df_power['기온구간'] = pd.cut(df_power['서울_기온'], bins=bins, labels=labels, right=False)
    
    return df_temp, df_power

# 데이터 로딩 실행 및 예외 처리
try:
    df_temp, df_power = load_and_process_data()
except Exception as e:
    st.error("⚠️ 데이터 파일을 정상적으로 불러오지 못했습니다. 파일명과 위치를 확인해주세요.")
    st.info("💡 필요 파일 목록: `서울_기온.csv`, `양평_기온.csv`, `전력수요.csv` (모두 스크립트 파일과 같은 폴더에 위치해야 합니다.)")
    st.stop()

# -----------------------------------------------------------------------------
# 3. 탭 구성 (st.tabs)
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🔥 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])

# --- [탭1: 열섬 분석] ---
with tab1:
    st.header("1. 서울과 양평의 기온 비교 및 열섬현상")
    st.markdown("도심과 외곽 지역의 시간별 기온 편차와 계절별 변화 양상을 시각화합니다.")
    
    # ① 1년간 두 지역 기온 변화 (선그래프)
    st.subheader("① 1년간 두 지역 기온 변화")
    df_line = df_temp.sort_values('일시').set_index('일시')[['서울_기온', '양평_기온']]
    st.line_chart(df_line)
    
    # 좌우 컬럼 배치
    col1, col2 = st.columns(2)
    
    with col1:
        # ② 시각(0~23시)별 평균 기온차
        st.subheader("② 시각(0~23시)별 평균 기온차 (서울 - 양평)")
        df_hour = df_temp.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
        st.bar_chart(df_hour.set_index('시각'))
        
    with col2:
        # ③ 월(1~12월)별 평균 기온차
        st.subheader("③ 월(1~12월)별 평균 기온차 (서울 - 양평)")
        df_month = df_temp.groupby('월')['기온차(서울-양평)'].mean().reset_index()
        st.bar_chart(df_month.set_index('월'))


# --- [탭2: 전력 연결] ---
with tab2:
    st.header("2. 서울 기온 변화에 따른 전력수요 연동 분석")
    st.markdown("기온 환경 요소가 실제 전력 부하에 미치는 통계적 특성을 파악합니다.")
    
    # ① 기온(가로)과 전력수요(세로)의 산점도
    st.subheader("① 기온(가로)과 전력수요(세로)의 산점도")
    st.scatter_chart(data=df_power, x='서울_기온', y='전력수요(MWh)')
    
    # 좌우 컬럼 배치
    col3, col4 = st.columns(2)
    
    with col3:
        # ② 기온 구간별 평균 전력수요
        st.subheader("② 기온 구간별 평균 전력수요")
        df_bin = df_power.groupby('기온구간', observed=False)['전력수요(MWh)'].mean().reset_index()
        st.bar_chart(df_bin.set_index('기온구간'))
        
    with col4:
        # ③ 월(1~12월)별 평균 전력수요
        st.subheader("③ 월(1~12월)별 평균 전력수요")
        df_month_p = df_power.groupby('월')['전력수요(MWh)'].mean().reset_index()
        st.bar_chart(df_month_p.set_index('월'))
