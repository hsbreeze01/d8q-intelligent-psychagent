const express = require('express');
const path = require('path');
const { exec } = require('child_process');
const app = express();
const port = process.env.PORT || 3000;

// 设置模板引擎
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../public'));

// 静态文件服务
app.use(express.static(path.join(__dirname, '../public')));

// 解析请求体
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 主页面路由
app.get('/', (req, res) => {
  res.render('index');
});

// 获取股票数据的API路由
app.post('/api/stock', async (req, res) => {
  try {
    const { stockCode } = req.body;
    if (!stockCode) {
      return res.status(400).json({ error: '股票代码或名称不能为空' });
    }
    
    // 这里将使用akshare获取股票数据
    const stockData = await getStockData(stockCode);
    res.json(stockData);
  } catch (error) {
    console.error('获取股票数据失败:', error);
    res.status(500).json({ error: '获取股票数据失败，请稍后重试' });
  }
});

// 使用Python脚本获取股票数据的函数
async function getStockData(stockCode) {
  return new Promise((resolve, reject) => {
    const pythonScriptPath = path.join(__dirname, 'stock_data.py');
    const command = `python3.11 "${pythonScriptPath}" "${stockCode}"`;
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error('执行Python脚本失败:', error);
        reject(new Error('获取股票数据失败'));
        return;
      }
      
      if (stderr) {
        console.error('Python脚本错误:', stderr);
      }
      
      try {
        const result = JSON.parse(stdout);
        if (result.error) {
          reject(new Error(result.error));
        } else {
          resolve(result);
        }
      } catch (parseError) {
        console.error('解析Python脚本输出失败:', parseError);
        reject(new Error('获取股票数据失败'));
      }
    });
  });
}

// 启动服务器
app.listen(port, () => {
  console.log(`服务器运行在 http://localhost:${port}`);
});
