import ccxt
from pprint import pprint
import pandas as pd
import time
from decimal import *

# print('CCXT Version:', ccxt.__version__)

exchange = ccxt.binance({
    'apiKey': '50e73acd9fc2ce8fdcca78f978387e931d7d30bea49321a65778e0e5b454902d',
    'secret': '160588dfae35596c927b63a9da687b245f9ab4d6169f8d0d0ed70420108a4a5e',
    'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
    'options': {
        'defaultType': 'future',
    },
})

exchange.set_sandbox_mode(True)  # comment if you're not using the testnet
markets = exchange.load_markets()
exchange.verbose = False  # debug output

balance = exchange.fetch_balance()['USDT']
balance = balance['free']
usdt_per_lot = balance/100

def position_size():
    size = usdt_per_lot/BNB_price
    return size

def making_order(way):
    if way == 'long':
        stopLoss_price = 0.9*df3.iloc[0]
        takeProfit_price = 1.15*df3.iloc[0]
        text='BNB/USDT'+' RSI: '+str(rsi)
        print(text)
        print('Making BUY order')
        exchange.create_limit_buy_order(symbol='BNB/USDT', amount=position_size() , price=df3.iloc[0] ,params ={
            'stopLoss': {
                'type': 'limit', # or 'market'
                'stopLossPrice': stopLoss_price,
            },
            'takeProfit': {
                'type': 'market',
                'takeProfitPrice': takeProfit_price,
            }
        })
    else:
        stopLoss_price = 1.1*df3.iloc[0]
        takeProfit_price = 0.85*df3.iloc[0]
        text='BNB/USDT'+' RSI: '+str(rsi)
        print(text)
        print('Making SHORT order')
        exchange.create_limit_sell_order(symbol='BNB/USDT', amount=position_size() , price=df3.iloc[0] ,params ={
            'stopLoss': {
                'type': 'limit', # or 'market'
                'stopLossPrice': stopLoss_price,
            },
            'takeProfit': {
                'type': 'market',
                'takeProfitPrice': takeProfit_price,
            }
        })

while True:
    ohlcv = exchange.fetch_ohlcv(symbol='BNB/USDT', timeframe='1m')
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
              
     #RSI indicator  
    period=14
    df['close'] = df['close'].astype(float)
    df2=df['close'].to_numpy()

    df2 = pd.DataFrame(df2, columns = ['close'])
    delta = df2.diff()

    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    _gain = up.ewm(com=(period - 1), min_periods=period).mean()
    _loss = down.abs().ewm(com=(period - 1), min_periods=period).mean()

    RS = _gain / _loss

    rsi=100 - (100 / (1 + RS))  
    rsi=rsi['close'].iloc[-1]
    rsi=round(rsi,1)
    pprint(df)
    print('-------BNB/USDT RSI:'+str(rsi)+'-----------')
    time.sleep(60)
    ohlcv = exchange.fetch_ohlcv(symbol='BNB/USDT', timeframe='1m')
    df3 = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    # pprint(df3)
    BNB_price = df3.loc[0, 'open']
    Order_status = 'OFF'
    if rsi <= 30:
        making_order('long')
        Order_status = 'ON'
    if rsi >= 70:
        making_order('short')
        Order_status = 'ON'
    if Order_status == 'ON':
        ob = exchange.fetch_orders(symbol= 'BNB/USDT')
        df_ob = pd.DataFrame(ob, columns=['symbol', 'id', 'status'])
        active_ob = df_ob.loc[0, 'status']
        while active_ob == 'open':
            ob = exchange.fetch_orders(symbol= 'BNB/USDT')
            df_ob = pd.DataFrame(ob, columns=['symbol', 'id', 'status'])
            active_ob = df_ob.loc[0, 'status']
    else:
        print('-------Indicator not detect yet-----------\n-------Finding RSI-----------\n\n\n')
