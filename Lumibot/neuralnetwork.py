import pandas as pd
import numpy as np
import datetime
from alpaca.data import StockBarsRequest, StockHistoricalDataClient
from config import API_KEY, API_SECRET
from alpaca.data.timeframe import TimeFrame
from backtesting import Strategy, Backtest
import pandas_ta as pa

class MyCandlesStrat(Strategy):  
    def init(self):
        super().init()
        self.signal1 = self.I(SIGNAL)

    def next(self):
        super().next() 
        if self.signal1==2:
            sl1 = self.data.Close[-1] - 600e-4
            tp1 = self.data.Close[-1] + 450e-4
            self.buy(sl=sl1, tp=tp1)
        elif self.signal1==1:
            sl1 = self.data.Close[-1] + 600e-4
            tp1 = self.data.Close[-1] - 450e-4
            self.sell(sl=sl1, tp=tp1)
# Initialize the data client
data_client = StockHistoricalDataClient(API_KEY, API_SECRET)

# Define the symbol and request parameters
symbol = "AAPL"
request_params = StockBarsRequest(
    symbol_or_symbols=symbol,
    timeframe=TimeFrame.Minute,
    start=datetime.datetime(2024, 1, 1),
    end=datetime.datetime(2024, 5, 31)
)

# Fetch the stock bars
bars = data_client.get_stock_bars(request_params).df
bars = bars[bars['volume'] != 0]
bars.reset_index(inplace=True)  # Reset the index to include the timestamp as a column
bars.isna().sum()

# Drop the trade_count and vwap columns
bars = bars.drop(columns=['trade_count', 'vwap','symbol'])

# Calculate necessary variables
length = len(bars)
high = list(bars['high'])
low = list(bars['low'])
close = list(bars['close'])
open = list(bars['open'])
bodydiff = [0] * length
highdiff = [0] * length
lowdiff = [0] * length
ratio1 = [0] * length
ratio2 = [0] * length

def isEngulfing(l):
    row = l
    bodydiff[row] = abs(open[row] - close[row])
    if bodydiff[row] < 0.000001:
        bodydiff[row] = 0.000001      

    bodydiffmin = 0.002
    if (bodydiff[row] > bodydiffmin and bodydiff[row - 1] > bodydiffmin and
        open[row - 1] < close[row - 1] and
        open[row] > close[row] and 
        (open[row] - close[row - 1]) >= -0e-5 and close[row] < open[row - 1]): 
        return 1

    elif(bodydiff[row] > bodydiffmin and bodydiff[row - 1] > bodydiffmin and
        open[row - 1] > close[row - 1] and
        open[row] < close[row] and 
        (open[row] - close[row - 1]) <= +0e-5 and close[row] > open[row - 1]): 
        return 2
    else:
        return 0
       
def isStar(l):
    bodydiffmin = 0.0020
    row = l
    highdiff[row] = high[row] - max(open[row], close[row])
    lowdiff[row] = min(open[row], close[row]) - low[row]
    bodydiff[row] = abs(open[row] - close[row])
    if bodydiff[row] < 0.000001:
        bodydiff[row] = 0.000001
    ratio1[row] = highdiff[row] / bodydiff[row]
    ratio2[row] = lowdiff[row] / bodydiff[row]

    if (ratio1[row] > 1 and lowdiff[row] < 0.2 * highdiff[row] and bodydiff[row] > bodydiffmin):
        return 1
    elif (ratio2[row] > 1 and highdiff[row] < 0.2 * lowdiff[row] and bodydiff[row] > bodydiffmin):
        return 2
    else:
        return 0
    
def closeResistance(l, levels, lim):
    if len(levels) == 0:
        return 0
    c1 = abs(bars.high[l] - min(levels, key=lambda x: abs(x - bars.high[l]))) <= lim
    c2 = abs(max(bars.open[l], bars.close[l]) - min(levels, key=lambda x: abs(x - bars.high[l]))) <= lim
    c3 = min(bars.open[l], bars.close[l]) < min(levels, key=lambda x: abs(x - bars.high[l]))
    c4 = bars.low[l] < min(levels, key=lambda x: abs(x - bars.high[l]))
    if (c1 or c2) and c3 and c4:
        return 1
    else:
        return 0
    
def closeSupport(l, levels, lim):
    if len(levels) == 0:
        return 0
    c1 = abs(bars.low[l] - min(levels, key=lambda x: abs(x - bars.low[l]))) <= lim
    c2 = abs(min(bars.open[l], bars.close[l]) - min(levels, key=lambda x: abs(x - bars.low[l]))) <= lim
    c3 = max(bars.open[l], bars.close[l]) > min(levels, key=lambda x: abs(x - bars.low[l]))
    c4 = bars.high[l] > min(levels, key=lambda x: abs(x - bars.low[l]))
    if (c1 or c2) and c3 and c4:
        return 1
    else:
        return 0

# Support and Resistance functions
def support(bars, l, n1, n2):
    for i in range(l - n1 + 1, l + 1):
        if bars['low'].iloc[i] > bars['low'].iloc[i - 1]:
            return 0
    for i in range(l + 1, l + n2 + 1):
        if bars['low'].iloc[i] < bars['low'].iloc[i - 1]:
            return 0
    return 1

def resistance(bars, l, n1, n2):
    for i in range(l - n1 + 1, l + 1):
        if bars['high'].iloc[i] < bars['high'].iloc[i - 1]:
            return 0
    for i in range(l + 1, l + n2 + 1):
        if bars['high'].iloc[i] > bars['high'].iloc[i - 1]:
            return 0
    return 1

pipdiff = 200*1e-4 #for TP
SLTPRatio = 2 #pipdiff/Ratio gives SL
def mytarget(barsupfront, df1):
    length = len(df1)
    high = list(df1['high'])
    low = list(df1['low'])
    close = list(df1['close'])
    open = list(df1['open'])
    trendcat = [None] * length
    for line in range (0,length-barsupfront-2):
        valueOpenLow = 0
        valueOpenHigh = 0
        for i in range(1,barsupfront+2):
            value1 = open[line+1]-low[line+i]
            value2 = open[line+1]-high[line+i]
            valueOpenLow = max(value1, valueOpenLow)
            valueOpenHigh = min(value2, valueOpenHigh)
        #if ( (valueOpenLow >= (pipdiff/SLTPRatio)) and (-valueOpenHigh >= (pipdiff/SLTPRatio)) ):
        #    trendcat[line] = 2 # bth limits exceeded
        #elif ( (valueOpenLow >= pipdiff) and (-valueOpenHigh <= (pipdiff/SLTPRatio)) ):
        #    trendcat[line] = 3 #-1 downtrend
        #elif ( (valueOpenLow <= (pipdiff/SLTPRatio)) and (-valueOpenHigh >= pipdiff) ):
        #    trendcat[line] = 1 # uptrend
        #elif ( (valueOpenLow <= (pipdiff/SLTPRatio)) and (-valueOpenHigh <= (pipdiff/SLTPRatio)) ):
        #    trendcat[line] = 0 # no trend
        #elif ( (valueOpenLow >= (pipdiff/SLTPRatio)) and (-valueOpenHigh <= (pipdiff/SLTPRatio)) ):
        #    trendcat[line] = 5 # light trend down
        #elif ( (valueOpenLow <= (pipdiff/SLTPRatio)) and (-valueOpenHigh >= (pipdiff/SLTPRatio)) ):
        #    trendcat[line] = 4 # light trend up
            if ( (valueOpenLow >= pipdiff) and (-valueOpenHigh <= (pipdiff/SLTPRatio)) ):
                trendcat[line] = 1 #-1 downtrend
                break
            elif ( (valueOpenLow <= (pipdiff/SLTPRatio)) and (-valueOpenHigh >= pipdiff) ):
                trendcat[line] = 2 # uptrend
                break
            else:
                trendcat[line] = 0 # no clear trend
            
    return trendcat

n1 = 2
n2 = 2
backCandles = 30

signal = [0] * length

# Generate signals
for row in range(backCandles, length - n2):
    ss = []
    rr = []
    for subrow in range(row - backCandles + n1, row + 1):
        if support(bars, subrow, n1, n2):
            ss.append(bars['low'].iloc[subrow])
        if resistance(bars, subrow, n1, n2):
            rr.append(bars['high'].iloc[subrow])
    if ((isEngulfing(row) == 1 or isStar(row) == 1) and closeResistance(row, rr, 150e-5)):
        signal[row] = 1
    elif ((isEngulfing(row) == 2 or isStar(row) == 2) and closeSupport(row, ss, 150e-5)):
        signal[row] = 2
    else:
        signal[row] = 0

bars['signal'] = signal
print(bars[bars['signal'] == 1].count())

# Ensure you have the correct number of column names
bars.columns = ['Local time', 'Open', 'High', 'Low', 'Close', 'Volume', 'signal']

print(bars)

def SIGNAL():
    return bars.signal


bt = Backtest(bars, MyCandlesStrat, cash=200, commission=.00)
stat = bt.run()

bars['Target'] = mytarget(30, bars)
bars["RSI"] = pa.rsi(df.Close, length=16)
bars.dropna(inplace=True)
bars.reset_index(drop=True, inplace=True)
bars.tail()