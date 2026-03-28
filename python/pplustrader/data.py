"""
Data feed adapters for PlusPlusTrader
"""

class DataFeed:
    """Base data feed class"""
    pass

class CSVDataFeed(DataFeed):
    """CSV file data feed"""
    pass

class BinanceDataFeed(DataFeed):
    """Binance data feed"""
    pass

class OKXDataFeed(DataFeed):
    """OKX data feed"""
    pass