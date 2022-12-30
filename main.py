import pandas as pd
import pandas_ta as ta
import yfinance as yf
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from pandas.tseries.offsets import MonthEnd

tickers = pd.read_html('https://en.wikipedia.org/wiki/S%26P_100')[2]
tickers = tickers.Symbol.to_list()
print(tickers)
tickers = [i.replace('.','-') for i in tickers]
print(tickers)
#df = yf.download(tickers, start = '2017-01-01')
#df.to_csv('df')
#df = pd.read_csv('df')
#print(df)

#technical analysis

def RSIstrategy():
    df = yf.download('BTC-USD', datetime.datetime(2020,1,1))
    df['SMA200'] = ta.sma(df['Adj Close'], length = 200)
    df['Price_change'] = np.log(df['Adj Close']/df['Adj Close'].shift(1))
    df['Up_move'] = df['Price_change'].apply(lambda x: x if x > 0 else 0)
    df['Down_move'] = df['Price_change'].apply(lambda x: abs(x) if x <0 else 0)
    df['Ave_up'] = df['Up_move'].ewm(span = 19).mean()
    df['Ave_down'] = df['Down_move'].ewm(span = 19).mean()
    df['RSI'] = ta.rsi(df['Adj Close'], length = 12)
    df.loc[(df['Adj Close'] > df['SMA200']) & (df['RSI'] < 30), 'Buy'] = 'Yes'
    df.loc[(df['Adj Close'] < df['SMA200']) | (df['RSI'] > 30), 'Buy'] = 'No'
    #df = df.dropna()
    return df

def getSignal(df):
    buy_data = []
    sell_data = []

    for i in range(len(df)):
        if 'Yes' in df['Buy'].astype(str).iloc[i]:
            buy_data.append(df.iloc[i+1].name)
            for j in range(1,11):
                if df['RSI'].iloc[i+j] > 40:
                    sell_data.append(df.iloc[i+j+1].name)
                    break
                elif j ==10 :
                    sell_data.append(df.iloc[i+j+1].name)
    return buy_data, sell_data

df = RSIstrategy()
buy , sell = getSignal(df)

fig = make_subplots(rows = 2, cols = 1, print_grid = True ,subplot_titles = ('Candel Line', 'RSI'))
fig.add_trace(go.Candlestick(x = df.index, open = df['Open'], high = df['High'], low = df['Low'], close = df['Close']), row = 1, col = 1)
fig.add_trace(go.Scatter(x = df.index, y = df['SMA200'], line = dict(color = 'orange', width = 1), name = 'SMA200'), row = 1, col = 1)
fig.add_trace(go.Scatter(x = df.index, y = df['RSI'], line = dict(color = 'red', width = 1), name = 'RSI'), row = 2, col = 1)
#fig.add_scatter(df.index, df.loc[buy]['Adj Close'], mode = 'markers',  marker = dict(color = 'darkgreen', size = 6), name = 'Buy Signal',row = 1, col = 1)
fig.show()




