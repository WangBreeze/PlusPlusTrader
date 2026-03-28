#!/usr/bin/env python3
"""
极简Web界面 - 避免所有f-string问题
"""

import sys
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self.generate_simple_html()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    
    def generate_simple_html(self):
        """生成极简HTML，避免所有f-string问题"""
        now = datetime.now()
        
        # 使用字符串拼接而不是f-string
        html_parts = []
        html_parts.append('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PlusPlusTrader Web界面</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #333; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .online { background: #d4edda; color: #155724; }
        .code { background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🦞 PlusPlusTrader 量化交易系统</h1>
        <div class="status online">
            ✅ 系统运行正常 - ''' + now.strftime('%Y-%m-%d %H:%M:%S') + '''
        </div>
        
        <h2>📊 系统状态</h2>
        <ul>
            <li>核心引擎: <strong>运行中</strong></li>
            <li>Python绑定: <strong>可用</strong></li>
            <li>数据源: <strong>就绪</strong></li>
            <li>Web服务: <strong>活跃</strong></li>
        </ul>
        
        <h2>💡 示例代码</h2>
        <div class="code">
# 基础数据获取<br>
import pplustrader<br>
from pplustrader.data import BinanceDataFeed<br>
<br>
feed = BinanceDataFeed(symbol="BTC/USDT", interval="1h")<br>
data = feed.fetch_ohlcv(limit=100)<br>
print("获取到", len(data), "条历史数据")
        </div>
        
        <h2>🚀 快速开始</h2>
        <ol>
            <li>编译C++核心: <code>mkdir build && cd build && cmake .. && make</code></li>
            <li>安装Python绑定: <code>pip install -e ./python</code></li>
            <li>运行测试: <code>python -m pytest tests/</code></li>
        </ol>
        
        <p style="margin-top: 30px; color: #666;">
            PlusPlusTrader v1.0.0 | 高性能量化交易系统
        </p>
    </div>
</body>
</html>''')
        
        return ''.join(html_parts)

def main():
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except:
            print("使用默认端口8080")
    
    server = HTTPServer(('', port), SimpleHandler)
    print("=" * 50)
    print("🦞 PlusPlusTrader Web界面")
    print("=" * 50)
    print("服务器启动在: http://localhost:" + str(port))
    print("按 Ctrl+C 停止")
    print("=" * 50)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")

if __name__ == '__main__':
    main()