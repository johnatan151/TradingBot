from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient
from alpaca.data import CryptoBarsRequest, CryptoHistoricalDataClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.timeframe import TimeFrame
from Indicators import EMA,RSI
import pandas as pd
from Lumibot.config import API_KEY, API_SECRET


#getting data 
def get_data(symbol,start,end,timeframe=TimeFrame.Hour):
    """
    Fetch historical price data for a given crypto symbol from Alpaca.
    :param symbol: The crypto symbol to fetch data for.
    :param start_date: Start date for fetching data.
    :param end_date: End date for fetching data.
    :param timeframe: The timeframe for the data.
    :return: A pandas DataFrame containing the historical price data.
    """

    data_client = CryptoHistoricalDataClient(API_KEY,API_SECRET)

    request_params = CryptoBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=timeframe,
        start = start,
        end = end
    )
    bars = data_client.get_crypto_bars(request_params).df
    return bars

def place_order(client, symbol, qty, side, order_type='market', time_in_force='gtc'):
    """
    Place an order with Alpaca.

    :param client: Alpaca TradingClient.
    :param symbol: The crypto symbol to trade.
    :param qty: Quantity of the crypto to trade.
    :param side: 'buy' or 'sell'.
    :param order_type: Type of order ('market' or 'limit').
    :param time_in_force: Order time in force ('gtc', 'day', etc.).
    """
    if order_type == 'market':
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide(side),
            time_in_force=TimeInForce(time_in_force)
        )
    else:
        raise ValueError("Only market orders are implemented in this example.")
    
    client.submit_order(order)


def trading_strategy(client, symbol):
    """
    Example trading strategy using EMA.

    :param client: Alpaca TradingClient.
    :param symbol: The crypto symbol to trade.
    """
    # Define the date range for historical data
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)

    # Fetch historical data
    data = get_data(symbol, start_date.isoformat(), end_date.isoformat())
    print(data)
    