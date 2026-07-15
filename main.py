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
    # 파일 읽기 (cp949 인코딩 적용)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # [수정] 일시 컬럼의 앞뒤 공백 제거 및 유연한 datetime 변환 (errors='coerce'로 강제 차단 방지)
    for df in [seoul, yangpyeong, power]:
        if '일시' in df.columns:
            df['일시'] = df['일시'].astype(str).str.strip()
            df['일시'] = pd.to_datetime(df['일시'], errors='coerce')
    
    # 결측치(NaT)가 발생한 행은 제거
    seoul = seoul.dropna(subset=['일시'])
    yangpyeong = yangpyeong.dropna(subset=['일시'])
    power = power.dropna(subset=['일시'])
    
    # 필요한 열만 추출 및 이름 변경 (기온 데이터 컬럼명 유연성 확보)
    seoul_temp_col = [c for c in seoul.columns if '기온' in c][0]
    yang_temp_col = [c for c in yangpyeong.columns if '기온' in c][0]
    
    seoul = seoul[['일시', seoul_temp_col]].rename(columns={seoul_temp_col: '서울_기온'})
    yangpyeong = yangpyeong[['일시', yang_temp_col]].rename(columns={yang_temp_col: '양평_기온'})
    
    # 전력수요 컬럼명이 다를 경우를 대비해 변환
    power_col = [c for c in power.columns if '전력' in c][0]
    power = power[['일시', power_col]].rename(columns={power_col: '전력수요(MWh)'})
    
    # [탭1용] 서울 및 양평 기온 데이터 결합 (일시 기준)
    df_temp = pd.merge(seoul, yangpyeong, on='일시', how='inner')
    
    # [체크] 데이터 조인 결과 검증
    if df_temp.empty:
        raise ValueError("서울 기온 데이터와 양평 기온 데이터 간에 일치하는 날짜/시간이 없습니다. 데이터의 기간을 확인해 주세요.")
        
    df_temp['기온차(서울-양평)'] = df_temp['서울_기온'] - df_temp['양평_기온']
    df_temp['월'] = df_temp['일시'].dt.month
    df_temp['시각'] = df_temp['일시'].dt.hour
    
    # [탭2용] 서울 기온과 전력수요 데이터 결합 (일시 기준)
    df_power = pd.merge(seoul, power, on='일시', how='inner')
    
    if df_power.empty:
        # 에러 추적을 위한 샘플 추출
        seoul_sample = str(seoul['일시'].dt.date.iloc[0]) if not seoul.empty else "없음"
        power_sample = str(power['일시'].dt.date.iloc[0]) if not power.empty else "없음"
        raise ValueError(f"기온 데이터와 전력수요 데이터의 연도/날짜 구간이 일치하지 않습니다.\n"
                         f"- 서울 기온 날짜 샘플: {seoul_sample}\n"
                         f"- 전력 수요 날짜 샘플: {power_sample}")
        
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
    st.error("⚠️ 데이터 처리 중 오류가 발생했습니다.")
    st.info(f"📋 **상세 내용:**\n{e}")
    st.stop()

# -----------------------------------------------------------------------------
# 3. 탭 구성 (st.tabs)
# -----------------------------------------------------------------------------
tab1, tab2 = st.tabs(["🔥 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])

# --- [탭1: 열섬 분석] ---
with tab1:
    st.header("1. 서울과 양평의 기온 비교 및 열섬현상")
    st.markdown("도심과 외곽 지역의 시간별 기온 편차와 계절별 변화 양상을 시각화합니다.")
    
    st.subheader("① 1년간 두 지역 기온 변화")
    df_line = df_temp.sort_values('일시').set_index('일시')[['서울_기온', '양평_기온']]
    st.line_chart(df_line)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("② 시각(0~23시)별 평균 기온차 (서울 - 양평)")
        df_hour = df_temp.groupby('시각')['기온차(서울-양평)'].mean().reset_index()
        st.bar_chart(df_hour.set_index('시각'))
        
    with col2:
        st.subheader("③ 월(1~12월)별 평균 기온차 (서울 - 양평)")
        df_month = df_temp.groupby('월')['기온차(서울-양평)'].mean().reset_index()
        st.bar_chart(df_month.set_index('월'))

# --- [탭2: 전력 연결] ---
with tab2:
    st.header("2. 서울 기온 변화에 따른 전력수요 연동 분석")
    st.markdown("기온 환경 요소가 실제 전력 부하에 미치는 통계적 특성을 파악합니다.")
    
    st.subheader("① 기온(가로)과 전력수요(세로)의 산점도")
    st.scatter_chart(data=df_power, x='서울_기온', y='전력수요(MWh)')
    
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("② 기온 구간별 평균 전력수요")
        df_bin = df_power.groupby('기온구간', observed=False)['전력수요(MWh)'].mean().reset_index()
        st.bar_chart(df_bin.set_index('기onn구간' if '기onn구간' in df_bin.columns else '기온구간'))
        
    with col4:
        st.subheader("③ 월(1~12월)별 평균 전력수요")
        df_month_p = df_power.groupby('월')['전력수요(MWh)'].mean().reset_index()
        st.bar_chart(df_month_p.set_index('월'))
