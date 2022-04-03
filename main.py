import pandas as pd, math
from datetime import datetime as dt
from ta.momentum import RSIIndicator
import numpy as np
from os import walk


# The Data will be tested across this range of RSI values
rsi_range = [14, 20]

def sortino_ratio(returns, rfr=0):
    downside_returns = returns[returns < 0]
    expected_return = returns.mean()
    down_stdev = downside_returns.std()
    if down_stdev == 0:
        return None

    sortino_ratio = (expected_return - rfr) / down_stdev
    return sortino_ratio


def max_drawdown(df):
    df = df[['close']]
    Roll_Max = df.cummax()
    Daily_Drawdown = df / Roll_Max - 1.0
    Max_DD = Daily_Drawdown.cummin()
    return Max_DD.min()



def backtest_RSI(dataname, rsi_window, buy_rsi_value=30, sell_rsi_value=70, to_excel=True):
    # For each trade
    entry_dates = []
    entry_prices = []
    exit_dates = []
    exit_prices = []

    trade_durations = []
    profits = []
    max_drawdowns = []
    returns = []


    df = pd.read_csv(f'Data/{dataname}')

    rsi = RSIIndicator(close=df['close'], window=rsi_window).rsi()
    df['RSI'] = rsi

    i = 0
    open_trade = False

    entry_index = 0

    for _ in df.itertuples(index=False):

        i += 1
        if i < len(df.index):

            # BUY
            if not open_trade:
                if df['RSI'][i - 1] > buy_rsi_value and df['RSI'][i] < buy_rsi_value:
                    entry_dates.append(df['datetime'][i])
                    entry_prices.append(df['close'][i])
                    entry_index = i
                    open_trade = True

            # SELL
            elif open_trade:

                if df['RSI'][i - 1] < sell_rsi_value and df['RSI'][i] > sell_rsi_value:
                    profit = ((df['close'][i] - entry_prices[-1]) * 100) / entry_prices[-1]
                    duration = dt.strptime(df['datetime'][i], '%Y-%m-%d %H:%M:%S') - \
                               dt.strptime(entry_dates[-1], '%Y-%m-%d %H:%M:%S')

                    exit_dates.append(df['datetime'][i])
                    exit_prices.append(df['close'][i])
                    trade_durations.append(str(duration))
                    profits.append(f'{round(profit, 3)}%')
                    returns.append(profit)

                    df1 = df.loc[entry_index:i]
                    mdd = max_drawdown(df1)
                    max_drawdowns.append(mdd[0])
                    open_trade = False

    if len(entry_dates) > len(exit_dates):
        duration = dt.strptime(df['datetime'][i - 1], '%Y-%m-%d %H:%M:%S') - \
                   dt.strptime(entry_dates[-1], '%Y-%m-%d %H:%M:%S')
        profit = ((df['close'][i - 1] - entry_prices[-1]) * 100) / entry_prices[-1]
        df1 = df.loc[entry_index:i - 1]
        mdd = max_drawdown(df1)
        exit_dates.append('Current Position')
        exit_prices.append('Current Position')
        trade_durations.append(str(duration))
        profits.append(f'{round(profit, 3)}%')
        returns.append(profit)
        max_drawdowns.append(mdd[0])

    # TOTAL
    total_profit = sum(returns)
    total_trades = len(returns)
    returns = np.array(returns)
    if len(returns)>1:
        sortino_r = sortino_ratio(returns)
    else:
        sortino_r = 0
    avg_profit_per_trade = returns.mean()
    greatest_max_drawdown = min(max_drawdowns)
    winning_trades = len(returns[returns > 0])
    losing_trades = len(returns[returns < 0])
    win_rate = winning_trades * 100 / total_trades

    if to_excel:

        for _ in range(0, 9):
            entry_dates.append('')
            entry_prices.append('')
            exit_dates.append('')
            exit_prices.append('')
            trade_durations.append('')
            max_drawdowns.append('')

        profits.append('')
        profits.append(f'Total Trades: {total_trades}')
        profits.append(f'Win Rate: {round(win_rate, 2)}%')
        profits.append(f'Winning Trades: {winning_trades}')
        profits.append(f'Losing Trades: {losing_trades}')
        profits.append(f'Total Profit: {round(total_profit, 2)}%')
        profits.append(f'Avg % per trade : {round(avg_profit_per_trade, 2)}%')
        profits.append(f'Sortino Ratio: {sortino_r}')
        profits.append(f'Greatest Max Drawdown: {greatest_max_drawdown}')

        headers = ['Entry Date', 'Entry Price', 'Exit Price', 'Exit Date', 'Profit', 'Trade Duration', 'Max Drawdown']

        df = pd.DataFrame(columns=headers)
        df['Entry Date'] = entry_dates
        df['Entry Price'] = entry_prices
        df['Exit Date'] = exit_dates
        df['Exit Price'] = exit_prices
        df['Profit'] = profits
        df['Trade Duration'] = trade_durations
        df['Max Drawdown'] = max_drawdowns

        df = df.style \
            .applymap(
            lambda x: 'background-color: %s' % 'steelblue' if len(x) > 1 and str(x)[0] in ['T','W','L','A','S','G']
            \
            else len(x) > 1 and ('background-color: %s' % 'salmon' if str(x)[0] == '-' and str(x)[-1] == '%' else
                                 ('background-color: %s' % 'lightgreen' if str(x)[0]!= '-' and str(x)[-1] == '%' else None)),
            subset=['Profit'])


        name = dataname.split('.')

        writer = pd.ExcelWriter(f'Backtested/{name[0]}-RSI{rsi_window}.xlsx')
        df.to_excel(writer)
        writer.save()

    return total_trades, winning_trades, losing_trades, total_profit, avg_profit_per_trade, sortino_r, greatest_max_drawdown,win_rate


def optimize(datanames):
    total = []
    for data in datanames:
        try:
            for rsi in range(rsi_range[0],rsi_range[1]):
                tt, wt, lt, tp, appt, sr, gmd,wr = backtest_RSI(data,rsi)
                name = data.split('.')

                win_rate = f'{round(wr,2)}%'
                tp = f'{round(tp, 2)}%'
                appt = f'{round(appt, 2)}%'
                total.append([name[0],rsi,win_rate,tt, wt, lt, tp, appt, sr, gmd])
        except:
            pass
    headers = ['Name','RSI VALUE','Win Rate', 'Total Trades','Winning Trades','Losing Trades',
               'Total Profit','Avg % per trade','Sortino Ratio','Greatest Max Drawdown']

    df = pd.DataFrame(total, columns=headers)

    writer = pd.ExcelWriter(f'Optimized.xlsx')
    df.to_excel(writer)

    writer.save()

if __name__ == '__main__':
    run_optimizer = input('Run Optimizer (y/n): ')
    if run_optimizer == 'y':
        datanames = next(walk('Data/'), (None, None, []))[2]
        optimize(datanames)
    else:
        data = str(input('Dataname: '))
        for rsi in range(rsi_range[0],rsi_range[1]):
            tt, wt, lt, tp, appt, sr, gmd,wr = backtest_RSI(data,rsi)
