// app.js - 股票实时信息应用逻辑

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    const stockInput = document.getElementById('stockInput');
    const searchBtn = document.getElementById('searchBtn');
    const stockInfo = document.getElementById('stockInfo');
    const stockName = document.getElementById('stockName');
    const stockCode = document.getElementById('stockCode');
    const currentPrice = document.getElementById('currentPrice');
    const priceChange = document.getElementById('priceChange');
    const volume = document.getElementById('volume');
    const stockChart = document.getElementById('stockChart');
    
    let chart = null;
    
    // 搜索按钮点击事件
    searchBtn.addEventListener('click', async () => {
        const stockCodeOrName = stockInput.value.trim();
        if (!stockCodeOrName) {
            alert('请输入股票代码或名称');
            return;
        }
        
        try {
            // 使用context7发送POST请求获取股票数据
            const data = await context7.post('/api/stock', { stockCode: stockCodeOrName });
            
            // 显示股票信息
            displayStockInfo(data);
            
            // 绘制股票走势图表
            drawChart(data.history);
            
            // 将数据保存到context7上下文
            context7.set('currentStock', data);
            
        } catch (error) {
            console.error('获取股票数据失败:', error);
            alert('获取股票数据失败，请检查股票代码或名称是否正确');
        }
    });
    
    // 回车键搜索
    stockInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });
    
    // 显示股票信息
    function displayStockInfo(data) {
        stockName.textContent = data.name;
        stockCode.textContent = data.code;
        currentPrice.textContent = data.price;
        
        // 设置涨跌幅样式
        priceChange.textContent = data.change;
        priceChange.className = data.change.startsWith('+') ? 'positive' : 'negative';
        
        volume.textContent = data.volume;
        
        // 显示股票信息区域
        stockInfo.style.display = 'block';
    }
    
    // 绘制股票走势图表 - 蜡烛图
    function drawChart(historyData) {
        // 销毁现有图表
        if (chart) {
            chart.destroy();
        }
        
        // 准备图表数据
        const labels = historyData.map(item => item.date);
        
        // 为蜡烛图准备数据结构
        // 上涨的蜡烛（收盘价 >= 开盘价）
        const upData = [];
        // 下跌的蜡烛（收盘价 < 开盘价）
        const downData = [];
        
        historyData.forEach(item => {
            if (item.close >= item.open) {
                // 上涨蜡烛：使用柱状图显示主体
                upData.push({
                    x: item.date,
                    y: [item.low, item.open, item.close, item.high]
                });
                downData.push(null);
            } else {
                // 下跌蜡烛：使用柱状图显示主体
                downData.push({
                    x: item.date,
                    y: [item.low, item.open, item.close, item.high]
                });
                upData.push(null);
            }
        });
        
        // 创建新图表 - 使用自定义蜡烛图实现
        chart = new Chart(stockChart, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    // 价格走势线（可选）
                    {
                        label: '收盘价',
                        data: historyData.map(item => item.close),
                        borderColor: 'rgba(100, 100, 100, 0.3)',
                        backgroundColor: 'transparent',
                        borderWidth: 1,
                        fill: false,
                        tension: 0.1,
                        pointRadius: 0,
                        pointHoverRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: '价格 (元)'
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(2);
                            }
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '日期'
                        },
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                const item = historyData[context.dataIndex];
                                return [
                                    `开盘: ${item.open.toFixed(2)}`,
                                    `最高: ${item.high.toFixed(2)}`,
                                    `最低: ${item.low.toFixed(2)}`,
                                    `收盘: ${item.close.toFixed(2)}`
                                ];
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                // 设置图表的内边距
                layout: {
                    padding: {
                        left: 20,
                        right: 20
                    }
                }
            },
            // 添加蜡烛图的自定义渲染器
            plugins: [{
                id: 'candlestickRenderer',
                afterDatasetsDraw: function(chart) {
                    const ctx = chart.ctx;
                    const xAxis = chart.scales.x;
                    const yAxis = chart.scales.y;
                    
                    // 计算蜡烛图的宽度（基于x轴的刻度间距）
                    const barWidth = Math.min(
                        (xAxis.width / labels.length) * 0.8, // 最多占刻度间距的80%
                        15 // 最大宽度为15像素
                    );
                    
                    // 绘制每个蜡烛
                    historyData.forEach((item, index) => {
                        // 获取x坐标
                        const x = xAxis.getPixelForValue(index);
                        
                        // 计算价格对应的y坐标
                        const yOpen = yAxis.getPixelForValue(item.open);
                        const yHigh = yAxis.getPixelForValue(item.high);
                        const yLow = yAxis.getPixelForValue(item.low);
                        const yClose = yAxis.getPixelForValue(item.close);
                        
                        // 判断蜡烛是上涨还是下跌
                        const isUp = item.close >= item.open;
                        
                        // 设置蜡烛的颜色
                        const bodyColor = isUp ? 'rgba(75, 192, 192, 0.8)' : 'rgba(255, 99, 132, 0.8)';
                        const wickColor = isUp ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)';
                        
                        // 绘制影线
                        ctx.save();
                        ctx.strokeStyle = wickColor;
                        ctx.lineWidth = 1;
                        
                        // 上影线
                        ctx.beginPath();
                        ctx.moveTo(x, yHigh);
                        ctx.lineTo(x, isUp ? yOpen : yClose);
                        ctx.stroke();
                        
                        // 下影线
                        ctx.beginPath();
                        ctx.moveTo(x, yLow);
                        ctx.lineTo(x, isUp ? yClose : yOpen);
                        ctx.stroke();
                        ctx.restore();
                        
                        // 绘制蜡烛主体（开盘价和收盘价之间的矩形）
                        ctx.save();
                        ctx.fillStyle = bodyColor;
                        ctx.strokeStyle = wickColor;
                        ctx.lineWidth = 1;
                        
                        // 计算矩形的位置和尺寸
                        const bodyHeight = Math.abs(yClose - yOpen);
                        const bodyY = Math.min(yOpen, yClose);
                        
                        // 绘制矩形
                        ctx.fillRect(x - barWidth / 2, bodyY, barWidth, bodyHeight);
                        ctx.strokeRect(x - barWidth / 2, bodyY, barWidth, bodyHeight);
                        ctx.restore();
                    });
                }
            }]
        });
    }
    
    // 监听context7中股票数据的变化
    context7.on('currentStock', (data) => {
        console.log('当前股票数据更新:', data);
    });
});
