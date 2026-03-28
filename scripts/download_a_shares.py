#!/usr/bin/env python3
"""
A股数据下载脚本
按照PlusPlusTrader项目规则下载A股数据

功能：
1. 从多种数据源下载A股数据（yfinance, akshare, tushare）
2. 自动格式化数据以满足CSVDataSource要求
3. 按照项目目录结构保存数据
4. 支持批量下载

使用示例：
python download_a_shares.py --symbol 000001.SZ --start 2020-01-01 --end 2023-12-31
python download_a_shares.py --batch batch_stocks.txt --source akshare
"""

import argparse
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# 尝试导入不同的数据源库
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False

try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False

# 项目数据目录结构
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_STOCK_DIR = DATA_DIR / "raw" / "stock"
PROCESSED_DIR = DATA_DIR / "processed"

# A股代码映射
EXCHANGE_MAP = {
    'SZ': 'SZSE',  # 深圳证券交易所
    'SS': 'SSE',   # 上海证券交易所
    'SH': 'SSE',   # 上海证券交易所（旧代码）
    'SZSE': 'SZSE',
    'SSE': 'SSE',
}

# 频率映射
FREQUENCY_MAP = {
    '1d': 'D',     # 日线
    '1w': 'W',     # 周线
    '1mo': 'M',    # 月线
    '60m': '60',   # 60分钟
    '30m': '30',   # 30分钟
    '15m': '15',   # 15分钟
    '5m': '5',     # 5分钟
    '1m': '1',     # 1分钟
}

class AShareDownloader:
    """A股数据下载器"""
    
    def __init__(self, source='yfinance'):
        """
        初始化下载器
        
        Parameters:
        -----------
        source : str
            数据源，可选值：'yfinance', 'akshare', 'tushare'
        """
        self.source = source.lower()
        self._validate_source()
        
    def _validate_source(self):
        """验证数据源是否可用"""
        if self.source == 'yfinance' and not YFINANCE_AVAILABLE:
            raise ImportError("yfinance未安装，请运行: pip install yfinance")
        elif self.source == 'akshare' and not AKSHARE_AVAILABLE:
            raise ImportError("akshare未安装，请运行: pip install akshare")
        elif self.source == 'tushare' and not TUSHARE_AVAILABLE:
            raise ImportError("tushare未安装，请运行: pip install tushare")
        elif self.source not in ['yfinance', 'akshare', 'tushare']:
            raise ValueError(f"不支持的数据源: {self.source}")
    
    def _parse_symbol(self, symbol):
        """解析股票代码，提取交易所信息"""
        if '.' in symbol:
            code, suffix = symbol.split('.')
        else:
            code = symbol
            suffix = 'SZ' if code.startswith('0') or code.startswith('3') else 'SS'
        
        exchange = EXCHANGE_MAP.get(suffix.upper(), 'UNKNOWN')
        return code, suffix, exchange
    
    def _format_dataframe(self, df, symbol, frequency):
        """格式化DataFrame以符合CSVDataSource要求"""
        # 确保索引是datetime类型
        if not isinstance(df.index, pd.DatetimeIndex):
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.set_index('timestamp')
            elif 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
            elif 'datetime' in df.columns:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df = df.set_index('datetime')
        
        # 重命名列以符合规范
        column_map = {}
        for col in df.columns:
            col_lower = col.lower()
            if col_lower in ['open', '开盘', 'openprice']:
                column_map[col] = 'open'
            elif col_lower in ['high', '最高', 'highprice']:
                column_map[col] = 'high'
            elif col_lower in ['low', '最低', 'lowprice']:
                column_map[col] = 'low'
            elif col_lower in ['close', '收盘', 'closeprice']:
                column_map[col] = 'close'
            elif col_lower in ['volume', '成交量', 'vol', '成交股数']:
                column_map[col] = 'volume'
            elif col_lower in ['amount', '成交额', 'turnover']:
                column_map[col] = 'amount'
            elif col_lower in ['adj close', 'adjclose', '复权收盘价']:
                column_map[col] = 'adj_close'
        
        if column_map:
            df = df.rename(columns=column_map)
        
        # 添加timestamp列
        df = df.reset_index()
        if 'index' in df.columns:
            df = df.rename(columns={'index': 'timestamp'})
        
        # 确保必要的列存在
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in df.columns:
                if col == 'timestamp':
                    df['timestamp'] = df.index if 'index' in df.columns else pd.date_range(
                        start='2000-01-01', periods=len(df), freq='D'
                    )
                else:
                    # 填充默认值
                    df[col] = 0.0 if col != 'volume' else 0
        
        # 排序并去重
        df = df.sort_values('timestamp').drop_duplicates(subset=['timestamp'])
        
        # 添加元数据列
        df['symbol'] = symbol
        df['exchange'] = self._parse_symbol(symbol)[2]
        df['frequency'] = FREQUENCY_MAP.get(frequency, frequency)
        
        # 选择列顺序
        columns_order = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        optional_cols = ['adj_close', 'amount', 'symbol', 'exchange', 'frequency']
        
        final_cols = []
        for col in columns_order + optional_cols:
            if col in df.columns:
                final_cols.append(col)
        
        return df[final_cols]
    
    def _get_yfinance_symbol(self, symbol):
        """获取yfinance可识别的股票代码"""
        code, suffix, _ = self._parse_symbol(symbol)
        if suffix.upper() == 'SS':
            return f"{code}.SS"
        elif suffix.upper() == 'SZ':
            return f"{code}.SZ"
        else:
            return symbol
    
    def download_yfinance(self, symbol, start_date, end_date, interval='1d'):
        """使用yfinance下载数据"""
        yf_symbol = self._get_yfinance_symbol(symbol)
        
        print(f"下载 {symbol} 数据 (yfinance: {yf_symbol})...")
        print(f"时间范围: {start_date} 到 {end_date}")
        print(f"频率: {interval}")
        
        try:
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(start=start_date, end=end_date, interval=interval)
            
            if df.empty:
                print(f"警告: 未找到 {symbol} 的数据")
                return None
            
            print(f"下载完成，共 {len(df)} 条记录")
            return self._format_dataframe(df, symbol, interval)
            
        except Exception as e:
            print(f"下载失败: {e}")
            return None
    
    def download_akshare(self, symbol, start_date, end_date, interval='1d'):
        """使用akshare下载数据"""
        code, suffix, exchange = self._parse_symbol(symbol)
        
        print(f"下载 {symbol} 数据 (akshare)...")
        print(f"时间范围: {start_date} 到 {end_date}")
        print(f"频率: {interval}")
        
        try:
            # 根据频率选择不同的akshare函数
            if interval == '1d':
                # 日线数据
                df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', ''),
                    adjust="qfq"  # 前复权
                )
            elif interval in ['1m', '5m', '15m', '30m', '60m']:
                # 分钟数据
                period = interval.replace('m', '')
                df = ak.stock_zh_a_hist_min_em(
                    symbol=code,
                    period=period,
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', ''),
                    adjust=''
                )
            else:
                print(f"警告: akshare不支持频率 {interval}，使用日线数据")
                df = ak.stock_zh_a_hist(
                    symbol=code,
                    period="daily",
                    start_date=start_date.replace('-', ''),
                    end_date=end_date.replace('-', ''),
                    adjust="qfq"
                )
            
            if df.empty:
                print(f"警告: 未找到 {symbol} 的数据")
                return None
            
            # akshare返回的列名是中文，需要重命名
            column_mapping = {
                '日期': 'timestamp',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change',
                '换手率': 'turnover_rate'
            }
            
            df = df.rename(columns=column_mapping)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            print(f"下载完成，共 {len(df)} 条记录")
            return self._format_dataframe(df, symbol, interval)
            
        except Exception as e:
            print(f"下载失败: {e}")
            return None
    
    def download_tushare(self, symbol, start_date, end_date, interval='1d'):
        """使用tushare下载数据"""
        code, suffix, exchange = self._parse_symbol(symbol)
        
        print(f"下载 {symbol} 数据 (tushare)...")
        print(f"时间范围: {start_date} 到 {end_date}")
        print(f"频率: {interval}")
        
        try:
            # 注意：tushare需要API token，这里只是示例
            # 请先设置token: ts.set_token('your_token_here')
            pro = ts.pro_api()
            
            # 日线数据
            df = pro.daily(
                ts_code=f"{code}.{suffix}",
                start_date=start_date.replace('-', ''),
                end_date=end_date.replace('-', '')
            )
            
            if df.empty:
                print(f"警告: 未找到 {symbol} 的数据")
                return None
            
            # 重命名列
            column_mapping = {
                'trade_date': 'timestamp',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'vol': 'volume',
                'amount': 'amount'
            }
            
            df = df.rename(columns=column_mapping)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            print(f"下载完成，共 {len(df)} 条记录")
            return self._format_dataframe(df, symbol, interval)
            
        except Exception as e:
            print(f"下载失败: {e}")
            print("注意：tushare需要API token，请先设置token")
            return None
    
    def download(self, symbol, start_date, end_date, interval='1d'):
        """下载数据"""
        if self.source == 'yfinance':
            return self.download_yfinance(symbol, start_date, end_date, interval)
        elif self.source == 'akshare':
            return self.download_akshare(symbol, start_date, end_date, interval)
        elif self.source == 'tushare':
            return self.download_tushare(symbol, start_date, end_date, interval)
        else:
            raise ValueError(f"未知的数据源: {self.source}")
    
    def save_to_csv(self, df, symbol, output_dir=None, frequency='1d'):
        """保存数据到CSV文件，按照项目规则命名"""
        if df is None or df.empty:
            print("错误: 没有数据可保存")
            return False
        
        # 解析股票代码信息
        code, suffix, exchange = self._parse_symbol(symbol)
        
        # 确定输出目录
        if output_dir is None:
            exchange_dir = 'SSE' if exchange == 'SSE' else 'SZSE'
            output_dir = RAW_STOCK_DIR / exchange_dir
        
        # 创建目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        freq_code = FREQUENCY_MAP.get(frequency, frequency)
        filename = f"{code}.{suffix}_{exchange}_{freq_code}.csv"
        filepath = Path(output_dir) / filename
        
        # 保存文件
        try:
            df.to_csv(filepath, index=False, encoding='utf-8')
            print(f"数据已保存: {filepath}")
            print(f"文件大小: {os.path.getsize(filepath)} 字节")
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False
    
    def download_batch(self, symbols_file, start_date, end_date, interval='1d', source=None):
        """批量下载股票数据"""
        if source:
            self.source = source.lower()
            self._validate_source()
        
        # 读取股票列表
        try:
            with open(symbols_file, 'r', encoding='utf-8') as f:
                symbols = [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"读取股票列表失败: {e}")
            return
        
        print(f"开始批量下载 {len(symbols)} 只股票...")
        
        success_count = 0
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] 下载 {symbol}")
            
            # 跳过注释行
            if symbol.startswith('#'):
                continue
            
            # 下载数据
            df = self.download(symbol, start_date, end_date, interval)
            
            # 保存数据
            if df is not None and not df.empty:
                if self.save_to_csv(df, symbol, frequency=interval):
                    success_count += 1
            
            # 避免请求过于频繁
            if i < len(symbols):
                import time
                time.sleep(1)
        
        print(f"\n批量下载完成，成功 {success_count}/{len(symbols)} 只股票")

def main():
    parser = argparse.ArgumentParser(description='A股数据下载脚本')
    parser.add_argument('--symbol', type=str, help='股票代码，如 000001.SZ 或 600000.SS')
    parser.add_argument('--batch', type=str, help='批量下载的股票列表文件')
    parser.add_argument('--start', type=str, default='2020-01-01', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, default=datetime.now().strftime('%Y-%m-%d'), 
                       help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--interval', type=str, default='1d', 
                       choices=['1d', '1w', '1mo', '60m', '30m', '15m', '5m', '1m'],
                       help='数据频率')
    parser.add_argument('--source', type=str, default='yfinance',
                       choices=['yfinance', 'akshare', 'tushare'],
                       help='数据源')
    parser.add_argument('--output_dir', type=str, help='输出目录')
    
    args = parser.parse_args()
    
    # 检查参数
    if not args.symbol and not args.batch:
        parser.error("必须提供 --symbol 或 --batch 参数")
    
    # 创建下载器
    try:
        downloader = AShareDownloader(source=args.source)
    except (ImportError, ValueError) as e:
        print(f"初始化下载器失败: {e}")
        print("\n请安装所需的依赖库:")
        print("  pip install yfinance pandas")
        print("  pip install akshare")
        print("  pip install tushare")
        sys.exit(1)
    
    # 批量下载
    if args.batch:
        downloader.download_batch(
            symbols_file=args.batch,
            start_date=args.start,
            end_date=args.end,
            interval=args.interval,
            source=args.source
        )
    # 单只股票下载
    else:
        df = downloader.download(
            symbol=args.symbol,
            start_date=args.start,
            end_date=args.end,
            interval=args.interval
        )
        
        if df is not None and not df.empty:
            downloader.save_to_csv(
                df=df,
                symbol=args.symbol,
                output_dir=args.output_dir,
                frequency=args.interval
            )
            
            # 显示数据摘要
            print("\n数据摘要:")
            print(f"时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}")
            print(f"记录数: {len(df)}")
            print(f"列: {', '.join(df.columns)}")
            print(f"开盘价范围: {df['open'].min():.2f} - {df['open'].max():.2f}")
            print(f"成交量范围: {df['volume'].min():.0f} - {df['volume'].max():.0f}")
        else:
            print("下载失败，未获取到数据")

if __name__ == '__main__':
    main()