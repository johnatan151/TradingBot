from alpaca.trading.client import TradingClient
from alpaca.data import StockHistoricalDataClient,StockTradesRequest
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide,TimeInForce, QueryOrderStatus
from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.traders import trader
import requests
import pandas as pd
from tradingLogic import trading_strategy
from Lumibot.config import API_KEY, API_SECRET
import time




def main():
    trading_client = TradingClient(API_KEY,API_SECRET)
    data_client = StockHistoricalDataClient(API_KEY,API_SECRET)
    symbol = 'LTC/USD'
    while True:
        #making money hopefully
        trading_strategy(trading_client,symbol)
        time.sleep(30)

if __name__ == "__main__":
    main()