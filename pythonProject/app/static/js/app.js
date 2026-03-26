let chartInstances = [];

window.onload = function() {
    chartInstances.forEach(chart => chart.dispose());
    chartInstances = [];
    initPageCharts();
};

window.onresize = function() {
    chartInstances.forEach(chart => chart.resize());
};

function initPageCharts() {
    const pageId = document.body.getAttribute('data-page');
    switch(pageId) {
        case 'index': initIndexCharts(); break;
        case 'consumption-trend': initTrendCharts(); break;
        case 'dish-hot': initHotDishChart(); break;
        case 'forecast': initForecastChart(); break;
        case 'user-portrait': initUserPortraitChart(); break;
        case 'reports': initReportsCharts(); break;
    }
}

// 首页图表
function initIndexCharts() {
    // 趋势图
    const trendChart = echarts.init(document.getElementById('trend-chart'));
    chartInstances.push(trendChart);
    const trendData = window.trendData || [];
    trendChart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['消费金额', '订单数量'] },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: trendData.map(item => item.date) },
        yAxis: [
            { type: 'value', name: '金额(元)', position: 'left' },
            { type: 'value', name: '订单数', position: 'right' }
        ],
        series: [
            { name: '消费金额', type: 'line', smooth: true, data: trendData.map(item => item.total_amount), itemStyle: { color: '#3498db' } },
            { name: '订单数量', type: 'line', smooth: true, yAxisIndex: 1, data: trendData.map(item => item.order_count), itemStyle: { color: '#e74c3c' } }
        ]
    });

    // 食堂排行
    const canteenChart = echarts.init(document.getElementById('canteen-chart'));
    chartInstances.push(canteenChart);
    const canteenData = window.canteenData || [];
    canteenChart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', data: canteenData.map(item => item.canteen_name) },
        yAxis: { type: 'value', name: '金额(元)' },
        series: [{ type: 'bar', data: canteenData.map(item => item.total_amount), itemStyle: { color: '#2ecc71' } }]
    });

    // 热销TOP10
    const hotDishChart = echarts.init(document.getElementById('hot-dish-chart'));
    chartInstances.push(hotDishChart);
    const hotDishData = window.hotDishData || [];
    hotDishChart.setOption({
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', radius: '60%', data: hotDishData.slice(0, 10).map(item => ({ value: item.sale_count, name: item.dish_name })) }]
    });
}

// 消费趋势页
function initTrendCharts() {
    const trendChart = echarts.init(document.getElementById('trend-line-chart'));
    chartInstances.push(trendChart);
    const trendData = window.trendData || [];
    trendChart.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: trendData.map(item => item.date) },
        yAxis: { type: 'value' },
        series: [{ type: 'line', smooth: true, data: trendData.map(item => item.total_amount), areaStyle: { opacity: 0.3 } }]
    });

    const mealChart = echarts.init(document.getElementById('meal-pie-chart'));
    chartInstances.push(mealChart);
    const mealData = window.mealData || [];
    mealChart.setOption({
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', radius: ['40%', '70%'], data: mealData.map(item => ({ value: item.total_amount, name: item.meal_name })) }]
    });
}

// 热销菜品页
function initHotDishChart() {
    const chart = echarts.init(document.getElementById('hot-dish-bar-chart'));
    chartInstances.push(chart);
    const data = window.hotDishData || [];
    chart.setOption({
        tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'value' },
        yAxis: { type: 'category', data: data.map(item => item.dish_name).reverse() },
        series: [{ type: 'bar', data: data.map(item => item.sale_count).reverse(), itemStyle: { color: '#f39c12' } }]
    });
}

// 销量预测页
function initForecastChart() {
    const chart = echarts.init(document.getElementById('forecast-chart'));
    chartInstances.push(chart);
    const history = window.historyData || [];
    const forecast = window.forecastData || [];
    const allDates = [...history.map(d => d.date), ...forecast.map(d => d.date)];
    chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['历史金额', '预测金额'] },
        grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: allDates },
        yAxis: { type: 'value' },
        series: [
            { name: '历史金额', type: 'line', smooth: true, data: history.map(d => d.amount), itemStyle: { color: '#3498db' } },
            { name: '预测金额', type: 'line', smooth: true, data: [...new Array(history.length).fill(null), ...forecast.map(d => d.forecast_amount)], itemStyle: { color: '#e74c3c' }, lineStyle: { type: 'dashed' } }
        ]
    });
}

// 用户画像页
function initUserPortraitChart() {
    const chart = echarts.init(document.getElementById('user-cluster-chart'));
    chartInstances.push(chart);
    const data = window.clusterResult || [];
    chart.setOption({
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', radius: '60%', data: data.map(item => ({ value: item.user_count, name: item.cluster_label })) }]
    });
}

// 报表页
function initReportsCharts() {
    const canteenChart = echarts.init(document.getElementById('reports-canteen-pie'));
    chartInstances.push(canteenChart);
    const canteenData = window.canteenData || [];
    canteenChart.setOption({
        tooltip: { trigger: 'item' },
        series: [{ type: 'pie', radius: '60%', data: canteenData.map(item => ({ value: item.total_amount, name: item.canteen_name })) }]
    });

    const mealChart = echarts.init(document.getElementById('reports-meal-bar'));
    chartInstances.push(mealChart);
    const mealData = window.mealData || [];
    mealChart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: mealData.map(item => item.meal_name) },
        yAxis: { type: 'value' },
        series: [{ type: 'bar', data: mealData.map(item => item.order_count), itemStyle: { color: '#9b59b6' } }]
    });
}