#!/usr/bin/env python3
"""
简化的Web界面 - 修复f-string问题
"""

import sys
import os
import json
from datetime import datetime, timedelta
import random
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleWebHandler(BaseHTTPRequestHandler):
    """简单的HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = self.generate_html()
            self.wfile.write(html_content.encode('utf-8'))
            
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            data = self.generate_mock_data()
            self.wfile.write(json.dumps(data).encode('utf-8'))
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')
    
    def generate_html(self):
        """生成HTML页面"""
        # 这里的关键是确保HTML模板中的代码块是纯文本
        # 不会被执行
        
        # 读取原始文件，但修复f-string问题
        with open('web/simple_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 找到HTML模板部分
        start = content.find("def generate_html(self):")
        if start == -1:
            # 如果找不到，使用备用模板
            return self.generate_fallback_html()
        
        # 提取return语句
        return_start = content.find("return f'''", start)
        if return_start == -1:
            return_start = content.find("return '''", start)
        
        if return_start == -1:
            return self.generate_fallback_html()
        
        # 找到结束位置
        return_end = content.find("'''", return_start + 10)
        if return_end == -1:
            return self.generate_fallback_html()
        
        html_template = content[return_start + 10:return_end]
        
        # 修复f-string问题：将 print(f"...") 替换为 print("...".format())
        # 但更简单的方法是直接使用修复后的模板
        return self.generate_fixed_html()
    
    def generate_fixed_html(self):
        """生成修复后的HTML"""
        now = datetime.now()
        
        html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🦞 PlusPlusTrader 量化交易系统</title>
    <style>
        /* 简化的样式 */
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        .code-block {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🦞 PlusPlusTrader Web界面</h1>
        <p>系统时间: {now.strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>💡 示例代码</h2>
        <div class="code-block">
# 基础数据获取示例
import pplustrader
from pplustrader.data import BinanceDataFeed

feed = BinanceDataFeed(symbol="BTC/USDT", interval="1h")
data = feed.fetch_ohlcv(limit=100)
print("获取到", len(data), "条历史数据")
        </div>
        
        <p>✅ Web界面运行正常</p>
    </div>
</body>
</html>'''
        
        return html
    
    def generate_fallback_html(self):
        """生成备用HTML"""
        return '''<!DOCTYPE html>
<html>
<head><title>PlusPlusTrader</title></head>
<body>
<h1>🦞 PlusPlusTrader Web界面</h1>
<p>系统运行正常</p>
</body>
</html>'''
    
    def generate_mock_data(self):
        """生成模拟数据"""
        return {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "message": "API数据获取成功"
        }

def run_server(port=8080):
    """运行HTTP服务器"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleWebHandler)
    
    print(f"🌐 服务器启动在: http://127.0.0.1:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器错误: {e}")

if __name__ == '__main__':
    port = 8080
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"⚠️ 无效的端口号，使用默认端口8080")
    
    run_server(port)