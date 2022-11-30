#!/usr/bin/python3

import yfinance as yf # for getting stock info
import pandas as pd # for data frame or series
from forex_python.converter import CurrencyRates # for forex rates
import matplotlib.pyplot as plt # show the plot 
import argparse

local_currency = "SGD"
local_c_string = "SGD Dividend"
exchanges_list = ['LSE','NMS','NYQ','SES','HKG']

def get_stock_info (stock_name,spec_info = ''):
    print(stock_name)
    stock_data = yf.Ticker(stock_name)
    # print(stock_data.info)
    return stock_data.info[spec_info]

def pandas_read(input_name):
    df = pd.read_csv(input_name)
    return df

def split_values_into_dict(data,i):
    stock_name = data.iloc[i,0]
    stock_count = data.iloc[i,1]
    stock_dividend = data.iloc[i,2]
    stock_price = get_stock_info(stock_name,'regularMarketPrice')
    try:
        stock_exchange = get_stock_info(stock_name, 'exchange')
    except:
        stock_exchange = get_stock_info(stock_name, 'Exchange')
    # price are not shown in pounds but rather pence 
    if stock_exchange == exchanges_list[0]:
        stock_price = stock_price / 100.00
    stock_total = stock_count * stock_price
    local_stock_total = convert_local_value(stock_exchange, stock_total)
    foreign_dividend = float(stock_dividend) * float(stock_count)
    total_dividend = convert_local_value(stock_exchange,foreign_dividend)
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
def convert_local_value(exchange,total):
    c = CurrencyRates()
    sgd_value = 0
    if exchange == exchanges_list[0]:
        sgd_value=c.get_rate('GBP', local_currency)*total
    elif exchange == exchanges_list[3]:
        sgd_value = total
    elif exchange == exchanges_list[4]:
        sgd_value=c.get_rate('HKD', local_currency)*total
    else:
        sgd_value=c.get_rate('USD', local_currency)*total
        print(f'{exchange} USD : {total}')
    
    print(f'{exchange} {local_currency} : {sgd_value}')
    return sgd_value

# add up value of all stocks on a particular stock exchange 
def exchange_total_value(output_df,exchange):               
    exchange_df= output_df.loc[output_df['Exchange']== exchange]
    print(exchange_df)
    total = exchange_df['Stock total value'].sum()
    return convert_local_value(exchange, total)

# add values of all exhcnage for total value of all 
def sum_exchange_value(output_df):
    tv = 0 
    tv = exchange_total_value(output_df,exchanges_list[0])
    tv += exchange_total_value(output_df,exchanges_list[1])
    tv += exchange_total_value(output_df,exchanges_list[2])
    tv += exchange_total_value(output_df,exchanges_list[3])
    tv += exchange_total_value(output_df,exchanges_list[4])
    print(f'All Exchange {local_currency} : {tv}')

def argument_parsing():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i","--inputfile", action="store_true")
    group.add_argument("-df","--dataframe", action="store_true")
    parser.add_argument("filename", type=str, help="input dataframe file")
    args = parser.parse_args()
    print(args.filename)

    if args.inputfile:
        data = pandas_read(args.filename).dropna()
        output_df = csv_file_content(data)
    elif args.dataframe:
        output_df = pd.read_pickle(args.filename)
    return output_df

def matplotlib_pi_chart(output_df):
    # for plotting of matplotplib graph 
    fig, ( ax1) = plt.subplots(1)
    dividend_df = output_df[local_c_string]
    print(dividend_df.sum())
    ax1.pie(dividend_df, labels= output_df['Symbol'], autopct='%1.1f%%',textprops={'fontsize': 14},pctdistance= 1.2, labeldistance= 1.3)
    ax1.set_title(local_c_string,loc='left')
    # ax2.pie(output_df[f"{local_currency} total value"], labels= output_df['Symbol'], autopct='%1.1f%%',textprops={'fontsize': 14},pctdistance= 1.2, labeldistance= 1.3)
    # ax2.set_title(f"{local_currency} Total Value")
    fig = plt.gcf()
    fig.set_size_inches(22,22)
    plt.show()

def save_to_file(output_df):
    output_df.to_pickle("../dataframe.pkl")
    output_df.to_csv("../output_dataframe.csv")


def main(argv):
    # argv includes name of the script 
    # print ('Number of arguments:', len(sys.argv), 'arguments.')
    # print ('Argument List:', str(sys.argv))
    output_df = argument_parsing()
    pd.set_option("display.max_columns", None)
    # drop anything with zero dividends
    output_df.drop(output_df[output_df[local_c_string]<=0.01].index,inplace=True)
    # sort dividends by size 
    output_df = output_df.sort_values(by=[local_c_string],ascending=False)
    
    output_df2 = output_df.loc[(output_df[local_c_string]>0)]
    
    #save to file 
    save_to_file(output_df)

    # show all exchange values
    sum_exchange_value(output_df)

    del output_df['Stock Price']
    print(output_df.iloc[: ,1:])
    matplotlib_pi_chart(output_df2)


if __name__ == "__main__":
   main(sys.argv[1:])

