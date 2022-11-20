from math import pi
import numpy as np
import pandas as pd

df = pd.read_csv('C:\\Users\\Anarkali\\Documents\\Python\\Stocks\\stockdata.csv')
df2 = pd.read_csv('C:\\Users\\Anarkali\\Documents\\Python\\Stocks\\finaldata.csv')

# Create empty list to append unique tickers to
tickers = []
# Create empty list to append current values to
current_values = []
for i in df['Ticker'].unique():
    new_df = df2.loc[df2['date']==df2['date'].max()]
    new_df = new_df.loc[:,new_df.columns.str.contains(i)]
    new_df = new_df.loc[:,(new_df.columns.str.endswith('_val'))|(new_df.columns.str.endswith('_sell'))]
    summation = new_df.sum(axis=1)
    if summation.values[0] != 0:
        tickers.append(i)
        current_values.append(summation.values[0])
    else:
        pass


base_values = []
# Get unique tickers
for i in df['Ticker'].unique():
    # Create sub df for buys
    ticker_df = df[df['Ticker']==i]
    # Filter that down further to just rows where order type = BUY
    buy_df = ticker_df[ticker_df['Order Type']=='BUY']
    # Create list of buy sizes
    buys = buy_df['Units'].to_list()
    # Create list of buy prices
    buy_prices = buy_df['Price'].to_list()

    # Create sub df for sells
    sell_df = ticker_df[ticker_df['Order Type']=='SELL']
    # If sells sub df is not empty
    if not sell_df.empty:
        # Create a list of sell sizes
        sells = sell_df['Units'].to_list()
        # Edit buys list such that it's now aggregate holding size after each buy
        for i in range(1,len(buys)):
            buys[i]=buys[i]+buys[i-1]
        # Create a variable which is the sum of units sold
        total_sells = sum(sells)
        # Look at each value in buys list
        for i in range(len(buys)):
            # If value is less than total units ever sold
            if buys[i] <= total_sells:
                # Change that value to 0
                buys[i] = 0
            else:
                # Otherwise change the value to be current value minus total units ever sold
                buys[i] = buys[i]-total_sells
        # For entries starting with 2nd entry in buys list
        new_buys_list = []
        new_buys_list.append(buys[0])
        for i in range(1,len(buys)):
            # Change the value to be current value minus the value of the entry to the left of it
            x = buys[i]-buys[i-1]
            new_buys_list.append(x)
        buys = new_buys_list
    else:
        pass
    # Multiply purchase prices list by buys list which represents current number of units held at each price point (FIFO)
    ticker_base_vals = [a*b for a,b in zip(buys,buy_prices)]
    # Now sum base_values list to get total current base value for the ticker
    current_base_value = sum(ticker_base_vals)
    # Append current base value to base_values list
    if current_base_value != 0:
        base_values.append(current_base_value)
    else:
        pass


df = pd.DataFrame({'ticker': tickers,
                   'current_value': current_values,
                   'base_value':base_values})
df['return'] = ((df['current_value']-df['base_value'])/df['base_value'])*100
df['current_value'] = round(df['current_value'],2)
df['base_value'] = round(df['base_value'],2)
df['return'] = round(df['return'],2)
df['return'] = df['return'].astype(str)
df['return'] = df['return']+'%'


df.to_csv('C:\\Users\\Anarkali\\Documents\\Python\\Stocks\\currentvalues.csv', index=False)
