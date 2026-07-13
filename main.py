import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울·양평 기온 및 전력수요 분석", layout="wide")
st.title("🌡️ 서울·양평 기온과 전력수요 데이터 분석")
st.markdown("2025년 시간별 데이터를 바탕으로 도시 열섬현상과 기온-전력수요의 상관관계를 분석합니다.")

# -----------------------------------------------------------------------------
# 1. 데이터 로드 및 전처리 (캐싱 적용으로 속도 향상)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # 데이터 읽기 (CP949 인코딩 적용)
    seoul_temp = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong_temp = pd.read_csv("양평_기온.csv", encoding="cp949")
    power_demand = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    seoul_temp['일시'] = pd.to_datetime(seoul_temp['일시'])
    yangpyeong_temp['일시'] = pd.to_datetime(yangpyeong_temp['일시'])
    power_demand['일시'] = pd.to_datetime(power_demand['일시'])
    
    # 필요한 열만 추출 및 이름 변경
    seoul_temp = seoul_temp[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울_기온'})
    yangpyeong_temp = yangpyeong_temp[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평_기온'})
    
    # [탭1용] 서울 & 양평 기온 병합
    df_temp = pd.merge(seoul_temp, yangpyeong_temp, on='일시', how='inner')
    df_temp['기온차(서울-양평)'] = df_temp['서울_기온'] - df_temp['양평_기온']
    df_temp['월'] = df_temp['일시'].dt.month
    df_temp['시각'] = df_temp['일시'].dt.hour
    
    # [탭2용] 서울 기온 & 전력수요 병합
    df_power = pd.merge(seoul_temp, power_demand, on='일시', how='inner')
    df_power['월'] = df_power['일시'].dt.month
    
    # 기온 구간 설정 (예: -20도부터 40도까지 5도 간격)
    bins = list(range(-20, 45, 5))
    labels = [f"{i} ~ {i+5}°C" for i in bins[:-1]]
    df_power['기온구간'] = pd.cut(df_power['서울_기온'], bins=bins, labels=labels, right=False)
    
    return df_temp, df_power

# 데이터 가져오기
try:
    df_temp, df_power = load_data()
except Exception as e:
    st.error(f"데이터 파일을 읽는 중 오류가 발생했습니다. 파일명과 위치를 확인해주세요.\n오류 내용: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 2. 탭 구성
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🔥 탭 1: 열섬 분석", "⚡ 탭 2: 전력 연결"])

# --- 탭 1: 열섬 분석 ---
with tab1:
    st.header("서울과 양평의 기온 비교를 통한 열섬현상 분석")
    
    # ① 1년간 두 지역 기온 변화 (선그래프)
    st.subheader("① 1년간 두 지역 기온 변화")
    # 차트용 데이터 정렬 및 인덱스 설정
    df_line = df_temp.sort_values('일시').set_index('일시')[['서울_기온', '양평_기온']]
    st.line_chart(df_line)
    
    col1, col2 = st.columns(2)
    
    # ② 시각(0~23시)별 평균 기온차 (막대그래프)
    with col1:
        st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
        df_hour_diff = df_temp.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
        st.bar_chart(df_hour_diff.set_index('시각'))
        st.caption("새벽~야간 시간대에 서울(도시)의 열섬현상이 뚜렷하게 나타나는지 확인할 수 있습니다.")
        
    # ③ 월(1~12월)별 평균 기온차 (막대그래프)
    with col2:
        st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
        df_month_diff = df_temp.groupby('월')['기온차(서울-양평)'].mean().reset_index()
        st.bar_chart(df_month_diff.set_index('월'))
        st.caption("계절별로 도시와 외곽 지역 간의 기온 차이가 어떻게 변하는지 확인 수 있습니다.")

# --- 탭 2: 전력 연결 ---
with tab2:
    st.header("서울 기온 변화에 따른 전력수요 분석")
    
    # ① 기온(가로)과 전력수요(세로)의 산점도
    st.subheader("① 기온과 전력수요 산점도")
    # st.scatter_chart는 x와 y 인자를 지정하여 쉽게 그릴 수 있습니다.
    st.scatter_chart(data=df_power, x='서울_기온', y='전력수요(MWh)')
    st.caption("기온이 매우 낮거나(난방) 매우 높을 때(냉방) 전력수요가 급증하는 U자형 패턴을 확인할 수 있습니다.")
    
    col3, col4 = st.columns(2)
    
    # ② 기온 구간별 평균 전력수요 (막대그래프)
    with col3:
        st.subheader("② 기온 구간별 평균 전력수요")
        df_bin_power = df_power.groupby('기온구간', observed=False)['전력수요(MWh)'].mean().reset_index()
        st.bar_chart(df_bin_power.set_index('기온구간'))
        
    # ③ 월(1~12월)별 평균 전력수요 (막대그래프)
    with col4:
        st.subheader("③ 월별 평균 전력수요")
        df_month_power = df_power.groupby('월')['전력수요(MWh)'].mean().reset_index()
        st.bar_chart(df_month_power.set_index('월'))
        st.caption("전력 소모가 많은 여름철(7-8월)과 겨울철(12-1월)의 피크 수요를 비교할 수 있습니다.")
