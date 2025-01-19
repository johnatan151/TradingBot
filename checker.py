from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.data import StockHistoricalDataClient,StockTradesRequest
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide,TimeInForce
import pytz

trading_client = TradingClient("PKIWOGD9FY9D9FMML978","nFSQdepxmLedfHF1SrjLuMDkmpeWk7qDGEdaucTN")
data_client = StockHistoricalDataClient("PKIWOGD9FY9D9FMML978","nFSQdepxmLedfHF1SrjLuMDkmpeWk7qDGEdaucTN")

print("the marker is curr: " + str(trading_client.get_clock()))
positions = trading_client.get_all_positions()
orders = trading_client.get_orders()

print(positions,orders)

