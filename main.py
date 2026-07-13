<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>열섬현상과 전력수요의 관계</title>
    <!-- Chart.js 라이브러리 로드 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --primary-blue: #2b6cb0;
            --primary-orange: #dd6b20;
            --bg-light: #f7fafc;
            --card-bg: #ffffff;
            --text-dark: #2d3748;
            --text-muted: #718096;
            --border-color: #e2e8f0;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, sans-serif;
        }

        body {
            background-color: var(--bg-light);
            color: var(--text-dark);
            line-height: 1.6;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* 헤더 디자인 */
        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 40px 20px;
            background: linear-gradient(135deg, var(--primary-blue), #1a365d);
            color: white;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        /* 카드 공통 스타일 */
        .card {
            background-color: var(--card-bg);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid var(--border-color);
        }

        .card h2 {
            font-size: 1.5rem;
            color: var(--primary-blue);
            margin-bottom: 15px;
            border-left: 5px solid var(--primary-orange);
            padding-left: 10px;
        }

        /* 필터 컨트롤 영역 */
        .filter-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-top: 15px;
        }

        .filter-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        select, input {
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 1rem;
        }

        /* 에러 메시지 */
        #error-message {
            display: none;
            background-color: #fff5f5;
            border: 1px solid #fed7d7;
            color: #c53030;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 25px;
        }

        #error-message ul {
            margin-left: 20px;
            margin-top: 10px;
        }

        /* 데이터 요약 스탯 */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }

        .stat-box {
            background-color: var(--bg-light);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-box .value {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--primary-orange);
        }

        /* 그래프 영역 */
        .chart-container {
            position: relative;
            width: 100%;
            height: 400px;
            margin-top: 15px;
        }

        /* 결과 분석 및 안내 */
        .interpretation-box {
            background-color: #ebf8ff;
            border-left: 4px solid var(--primary-blue);
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin-top: 15px;
        }

        .notice-box {
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-top: 10px;
            font-style: italic;
        }

        /* 반응형 대응 */
        @media (max-width: 768px) {
            header h1 { font-size: 1.8rem; }
            body { padding: 10px; }
            .chart-container { height: 300px; }
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>열섬현상과 전력수요의 관계</h1>
        <p>❓ 탐구 질문: 열섬 강도가 커질수록 전력수요도 증가할까?</p>
    </header>

    <!-- 에러 안내 메시지 -->
    <div id="error-message">
        <h3>⚠️ 데이터를 불러오지 못했습니다!</h3>
        <p>원인 및 해결 방법:</p>
        <ul>
            <li><strong>파일 위치 확인:</strong> <code>index.html</code>과 같은 폴더에 <code>서울_기온.csv</code>, <code>양평_기온.csv</code>, <code>전력수요.csv</code> 파일이 정확히 있는지 확인해주세요.</li>
            <li><strong>보안 정책(CORS):</strong> 브라우저에서 HTML 파일을 직접 더블 클릭해 열면 보안 문제로 CSV 로드가 제한됩니다. <strong>VS Code의 Live Server 확장 기능</strong>을 사용하거나, <strong>GitHub Pages</strong>에 업로드하여 확인해야 합니다.</li>
        </ul>
    </div>

    <!-- 1. 데이터 안내 및 필터 -->
    <div class="card">
        <h2>1. 데이터 확인</h2>
        <p>본 분석은 2025년 1년 동안의 시간별 관측 데이터를 기준으로 합니다. 도심(서울)과 교외(양평)의 기온 격차를 통해 열섬현상을 파악하고 동시간대 전력수요와의 연관성을 도출합니다.</p>
        
        <div class="filter-group">
            <div class="filter-item">
                <label for="month-select">📅 분석 월 선택</label>
                <select id="month-select">
                    <option value="all">1년 전체 데이터</option>
                    <option value="1">1월 (겨울)</option>
                    <option value="8">8월 (여름)</option>
                </select>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-box">
                <div class="label">총 분석 데이터 수</div>
                <div id="stat-count" class="value">-</div>
            </div>
            <div class="stat-box">
                <div class="label">평균 열섬 강도</div>
                <div id="stat-uhi" class="value">-</div>
            </div>
            <div class="stat-box">
                <div class="label">평균 전력수요</div>
                <div id="stat-power" class="value">-</div>
            </div>
        </div>
    </div>

    <!-- 2. 열섬현상 분석 -->
    <div class="card">
        <h2>2. 열섬현상 분석 (기온 변화 및 열섬 강도)</h2>
        <p>공식 계산: <code>열섬 강도 = 도심 기온(서울) - 교외 기온(양평)</code></p>
        <div class="chart-container">
            <canvas id="tempChart"></canvas>
        </div>
    </div>

    <!-- 3. 전력수요 분석 -->
    <div class="card">
        <h2>3. 전력수요 변화 분석</h2>
        <p>시간 및 날짜의 흐름에 따른 전력수요(MWh) 변동을 시각화합니다. 기온 변화 추이와 비교해볼 수 있습니다.</p>
        <div class="chart-container">
            <canvas id="powerChart"></canvas>
        </div>
    </div>

    <!-- 4. 상관관계 분석 -->
    <div class="card">
        <h2>4. 열섬 강도와 전력수요의 상관관계</h2>
        <div class="chart-container">
            <canvas id="scatterChart"></canvas>
        </div>
        <div class="interpretation-box">
            <h4>📊 데이터 통계적 해석 결과</h4>
            <p style="margin-top: 5px;">피어슨 상관계수 ($r$): <strong><span id="correlation-r">-</span></strong></p>
            <p>상관관계 자동 해석: <strong><span id="correlation-text">데이터를 로드하는 중입니다...</span></strong></p>
        </div>
        <div class="notice-box">
            ※ 주의: 상관관계가 존재한다고 해서 반드시 두 변수 간의 직접적인 인과관계(원인과 결과)를 의미하는 것은 아닙니다. 기온 상승이라는 공통적 계절성 요인이 두 지표에 동시에 영향을 주었을 가능성이 큽니다.
        </div>
    </div>

    <!-- 5. 탐구 결과 -->
    <div class="card">
        <h2>5. 최종 탐구 결과 요약</h2>
        <p id="final-summary">데이터를 로딩하고 분석하는 중입니다...</p>
    </div>
</div>

<script>
    // 전역 차트 객체 관리용 변수
    let tempChart, powerChart, scatterChart;
    let mergedData = [];

    // CP949 디코딩 및 간이 CSV 파서 기능
    async function fetchCSV(filename) {
        const response = await fetch(filename);
        if (!response.ok) throw new Error(`File not found: ${filename}`);
        
        // 브라우저 Fetch는 기본 UTF-8이므로 CP949 형식 데이터를 정상 가공하기 위해 arrayBuffer로 수신 후 변환
        const buffer = await response.arrayBuffer();
        const decoder = new TextDecoder('euc-kr'); // CP949 호환 호칭
        const text = decoder.decode(buffer);
        
        const lines = text.split(/\r?\n/);
        const headers = lines[0].split(',').map(h => h.trim());
        
        const result = [];
        for(let i = 1; i < lines.length; i++) {
            if(!lines[i]) continue;
            const cols = lines[i].split(',');
            const obj = {};
            headers.forEach((header, index) => {
                obj[header] = cols[index] ? cols[index].trim() : null;
            });
            result.push(obj);
        }
        return result;
    }

    // 데이터 초기화 및 결합 실행
    async function initApp() {
        try {
            // 3개 파일 동시 로드 시도
            const [seoulTemp, yangpyeongTemp, powerDemand] = await Promise.all([
                fetchCSV('서울_기온.csv'),
                fetchCSV('양평_기온.csv'),
                fetchCSV('전력수요.csv')
            ]);

            // 매핑 데이터 맵 생성 (일시 기준 탐색 최적화)
            const ypMap = new Map(yangpyeongTemp.map(d => [d['일시'], d['기온(°C)']]));
            const pMap = new Map(powerDemand.map(d => [d['일시'], d['전력수요(MWh)']]));

            // 서울 기온 기준으로 내부 조인(Inner Join) 연산 수행
            seoulTemp.forEach(s => {
                const datetimeStr = s['일시'];
                if (ypMap.has(datetimeStr) && pMap.has(datetimeStr)) {
                    const seoulT = parseFloat(s['기온(°C)']);
                    const yangpyeongT = parseFloat(ypMap.get(datetimeStr));
                    const power = parseFloat(pMap.get(datetimeStr));

                    if(!isNaN(seoulT) && !isNaN(yangpyeongT) && !isNaN(power)) {
                        const dateObj = new Date(datetimeStr);
                        mergedData.push({
                            datetime: datetimeStr,
                            month: dateObj.getMonth() + 1,
                            seoulTemp: seoulT,
                            ypTemp: yangpyeongT,
                            uhi: seoulT - yangpyeongT, // 열섬 강도 연산
                            power: power
                        });
                    }
                }
            });

            if (mergedData.length === 0) {
                throw new Error("결합된 데이터가 없습니다. '일시' 데이터 형식을 매칭할 수 없습니다.");
            }

            // 첫 로드 시 이벤트 리스너 바인딩 및 기본 분석 실행
            document.getElementById('month-select').addEventListener('change', updateCharts);
            updateCharts();

        } catch (error) {
            console.error(error);
            document.getElementById('error-message').style.display = 'block';
        }
    }

    // 피어슨 상관계수 구하기 함수
    function calculatePearson(x, y) {
        const n = x.length;
        if (n === 0) return 0;
        const sumX = x.reduce((a, b) => a + b, 0);
        const sumY = y.reduce((a, b) => a + b, 0);
        const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
        const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
        const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);

        const num = (n * sumXY) - (sumX * sumY);
        const den = Math.sqrt(((n * sumX2) - (sumX * sumX)) * ((n * sumY2) - (sumY * sumY)));
        return den === 0 ? 0 : num / den;
    }

    // 데이터 필터링 및 차트 갱신 기능 핵심 로직
    function updateCharts() {
        const selectedMonth = document.getElementById('month-select').value;
        
        // 필터링 처리
        const filtered = selectedMonth === 'all' 
            ? mergedData 
            : mergedData.filter(d => d.month === parseInt(selectedMonth));

        // 일부 월 선택 시 차트의 가독성 향상을 위해 간격 조절용 샘플링 비율 계산
        const sampleStep = selectedMonth === 'all' ? 48 : 4; 
        const sampled = filtered.filter((_, i) => i % sampleStep === 0);

        // 요약 정보 계산 및 화면 갱신
        const avgUHI = filtered.reduce((acc, d) => acc + d.uhi, 0) / filtered.length;
        const avgPower = filtered.reduce((acc, d) => acc + d.power, 0) / filtered.length;

        document.getElementById('stat-count').innerText = `${filtered.length.toLocaleString()}건`;
        document.getElementById('stat-uhi').innerText = `${avgUHI.toFixed(2)} °C`;
        document.getElementById('stat-power').innerText = `${Math.round(avgPower).toLocaleString()} MWh`;

        // 1. 기온 및 열섬 분석 차트 생성/갱신
        const ctxTemp = document.getElementById('tempChart').getContext('2d');
        if(tempChart) tempChart.destroy();
        tempChart = new Chart(ctxTemp, {
            type: 'line',
            data: {
                labels: sampled.map(d => d.datetime),
                datasets: [
                    { label: '도심 기온 (서울, °C)', data: sampled.map(d => d.seoulTemp), borderColor: '#e53e3e', borderWidth: 1.5, pointRadius: 0, fill: false },
                    { label: '교외 기온 (양평, °C)', data: sampled.map(d => d.ypTemp), borderColor: '#3182ce', borderWidth: 1.5, pointRadius: 0, fill: false },
                    { label: '열섬 강도 (°C)', data: sampled.map(d => d.uhi), borderColor: '#dd6b20', borderWidth: 1.5, pointRadius: 0, fill: false }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { display: false } } }
        });

        // 2. 전력 수요 차트 생성/갱신
        const ctxPower = document.getElementById('powerChart').getContext('2d');
        if(powerChart) powerChart.destroy();
        powerChart = new Chart(ctxPower, {
            type: 'line',
            data: {
                labels: sampled.map(d => d.datetime),
                datasets: [{ label: '전력수요 (MWh)', data: sampled.map(d => d.power), borderColor: '#319795', borderWidth: 1.5, pointRadius: 0, fill: false }]
            },
            options: { responsive: true, maintainAspectRatio: false, scales: { x: { display: false } } }
        });

        // 3. 상관관계 계산 및 산점도 추세선 연산
        const uhiArr = filtered.map(d => d.uhi);
        const powerArr = filtered.map(d => d.power);
        const rValue = calculatePearson(uhiArr, powerArr);
        
        document.getElementById('correlation-r').innerText = rValue.toFixed(4);
        
        let interpretation = '';
        if (Math.abs(rValue) < 0.2) interpretation = '상관관계가 매우 약하거나 거의 없습니다.';
        else if (rValue >= 0.2 && rValue < 0.4) interpretation = '약한 양의 상관관계가 관찰됩니다.';
        else if (rValue >= 0.4) interpretation = '뚜렷한 양의 상관관계가 관찰됩니다.';
        else if (rValue <= -0.2 && rValue > -0.4) interpretation = '약한 음의 상관관계가 관찰됩니다.';
        else if (rValue <= -0.4) interpretation = '뚜렷한 음의 상관관계가 관찰됩니다.';
        
        document.getElementById('correlation-text').innerText = interpretation;

        // 선형 추세선 작성을 위한 최소제곱법 구현
        const xMean = uhiArr.reduce((a,b)=>a+b,0)/uhiArr.length;
        const yMean = powerArr.reduce((a,b)=>a+b,0)/powerArr.length;
        let num = 0, den = 0;
        for(let i=0; i<uhiArr.length; i++) {
            num += (uhiArr[i] - xMean) * (powerArr[i] - yMean);
            den += Math.pow(uhiArr[i] - xMean, 2);
        }
        const slope = num / den;
        const intercept = yMean - (slope * xMean);

        const minX = Math.min(...uhiArr);
        const maxX = Math.max(...uhiArr);
        const trendlineData = [
            {x: minX, y: slope * minX + intercept},
            {x: maxX, y: slope * maxX + intercept}
        ];

        // 산점도 렌더링
        const ctxScatter = document.getElementById('scatterChart').getContext('2d');
        if(scatterChart) scatterChart.destroy();
        scatterChart = new Chart(ctxScatter, {
            type: 'scatter',
            data: {
                datasets: [
                    { label: '실제 관측치', data: filtered.filter((_,i)=>i%5===0).map(d => ({x: d.uhi, y: d.power})), backgroundColor: 'rgba(43, 108, 176, 0.5)', pointRadius: 3 },
                    { label: '선형 추세선', data: trendlineData, type: 'line', borderColor: '#dd6b20', borderDash: [5, 5], pointRadius: 0, fill: false }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { title: { display: true, text: '열섬 강도 (°C)' } },
                    y: { title: { display: true, text: '전력수요 (MWh)' } }
                }
            }
        });

        // 5. 최종 탐구 결과 요약 작성
        let summaryText = `2025년 관측 데이터를 분석한 결과, 선택한 기간 동안 도심과 교외의 평균 기온차(열섬 강도)는 ${avgUHI.toFixed(2)}°C로 관측되었습니다. `;
        summaryText += `동기간 열섬 강도와 전력수요 데이터의 피어슨 상관계수는 r = ${rValue.toFixed(2)} 지표를 나타내고 있습니다. `;
        if(rValue >= 0.2) {
            summaryText += `실제 데이터 흐름상 도심지의 기온 과열 현상이 대조 지역에 비해 심화되는 조건(열섬 강도 증가)일 때 전력수요 역시 상승 곡선을 그리는 경향이 정량적으로 확인됩니다. 단, 계절성과 냉난방 기기 가동 여부 등 외부 환경 변수가 통계치에 동시 작용하므로 주 원인으로 직결 시에는 해석 상 주의가 필요합니다.`;
        } else {
            summaryText += `제시된 전체 기간의 데이터 분포 특성상 열섬 현상의 격차 심화 유무가 전체 전력 수요 변동성에 직접적인 지배 요소로 작용하기에는 통계적 유의미성이 다소 부족하거나 복합적인 요인이 관여하고 있는 것으로 풀이됩니다.`;
        }
        document.getElementById('final-summary').innerText = summaryText;
    }

    // 초기 구동
    window.onload = initApp;
</script>
</body>
</html>
