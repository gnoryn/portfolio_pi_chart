#!/usr/bin/python3

import yfinance as yf # for getting stock info
import sys # for command line inputs 
import pandas as pd 
from forex_python.converter import CurrencyRates # for forex rates
import matplotlib.pyplot as plt # show the plot ?

local_currency = 'SGD'


def get_stock_info (stock_name,spec_info = 'regularMarketPrice'):
    stock_data = yf.Ticker(stock_name)
    return stock_data.info[spec_info]

def pandas_read(input_name):
    df = pd.read_csv(input_name)
    return df

def split_values_into_dict(data,i):
    stock_name = data.iloc[i,0]
    stock_count = data.iloc[i,1]
    stock_dividend = data.iloc[i,2]
    stock_price = get_stock_info(stock_name)
    stock_exchange = get_stock_info(stock_name, 'exchange')
    # price are not shown in pounds but rather pence 
    if stock_exchange == 'LSE':
        stock_price = stock_price / 100.00
    stock_total = stock_count * stock_price
    local_stock_total = get_local_value(stock_exchange, stock_total)
    foreign_dividend = float(stock_dividend) * float(stock_count)
    total_dividend = get_local_value(stock_exchange,foreign_dividend)
    return {'Exchange': stock_exchange, 'Symbol': stock_name,'Count':stock_count, 'Stock Price' : stock_price , 'Stock total value' : stock_total,'SGD total value' : local_stock_total, 'SGD Dividend': total_dividend}

# loop to get the name of stock from the csv field 
def csv_file_content(data):
    i = 0
    data_size = len(data.index)
    output_df = pd.DataFrame()
    while( i < data_size ):
        dictionary = split_values_into_dict(data,i)
        print(dictionary)
        dictionary_df = pd.DataFrame(dictionary, index=[i])      
        i = i + 1
        output_df = pd.concat([output_df,dictionary_df])
    return output_df

# get local value of the total value on the particular exchange 
def get_local_value(exchange,total):
    c = CurrencyRates()
    sgd_value = 0
    if exchange == 'LSE':
        sgd_value=c.get_rate('GBP', local_currency)*total
        # print(f'{exchange} GBP : {total}')
    else:
        sgd_value=c.get_rate('USD', local_currency)*total
        # print(f'{exchange} USD : {total}')
    # print(f'{exchange} {local_currency} : {sgd_value}')
    return sgd_value

# add up value of all stocks on a particular stock exchange 
def exchange_total_value(output_df,exchange):               
    exchange_df= output_df.loc[output_df['Exchange']== exchange]
    print(exchange_df)
    total = exchange_df['Stock total value'].sum()
    return get_local_value(exchange, total)

# add values of all exhcnage for total value of all 
def sum_exchange_value(output_df):
    tv = 0 
    tv = exchange_total_value(output_df,'LSE')
    tv += exchange_total_value(output_df,'NMS')
    tv += exchange_total_value(output_df,'NYQ')
    return tv

def main(argv):
    # argv includes name of the script 
    # print ('Number of arguments:', len(sys.argv), 'arguments.')
    # print ('Argument List:', str(sys.argv))
    if(len(sys.argv) == 2):
        tv = 0 
        input_file = str(sys.argv[1])
        data = pandas_read(input_file)
        output_df = csv_file_content(data)
        # output_df = pd.read_pickle("dataframe.pkl")
        tv = sum_exchange_value(output_df)
        output_df.to_pickle("dataframe.pkl")
        print(f'All Exchange {local_currency} : {tv}')
        print(output_df)
        fig, (ax1 , ax2) = plt.subplots(1,2)
        dividend_df = output_df[f"{local_currency} Dividend"]
        print(dividend_df.sum())
        ax1.pie(dividend_df, labels= output_df['Symbol'], autopct='%1.1f%%',textprops={'fontsize': 14})
        ax2.pie(output_df[f"{local_currency} total value"], labels= output_df['Symbol'], autopct='%1.1f%%',textprops={'fontsize': 14})
        ax1.set_title(f"{local_currency} Dividend")
        ax2.set_title(f"{local_currency} Total Value")
        
        fig = plt.gcf()
        fig.set_size_inches(20,20)
        plt.show()

if __name__ == "__main__":
   main(sys.argv[1:])

