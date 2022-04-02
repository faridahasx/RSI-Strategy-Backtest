# Backtest RSI
This script is meant to backtest a simple RSI strategy across range of RSI windows.

    Buy when RSI crosses from below to above 30

    Sell when RSI crosses from above to below 70

## Testing  
For each trade: Entry Date, Entry Price, Exit Price, Exit Date, Profit, Trade Duration, Max Drawdown

In Total: Win Rate, Total Trades, Winning Trades, Losing Trades, Total Profit, Avg % per trade, Sortino Ratio, Greatest Max Drawdown

## Run the script
1. Put your the data you want to backtest to Data folder. 
2. Run the main.py file
3. If you want to backtest all the files in the Data folder, input `y` 
4. If you want to backtest only one file then input `n`, then input the filename. e.g., `CRUDEOIL-1Hour.csv`.
6. After testing is done, results will be in `Backtested` folder and the optimized results will be saved in the main directory.

