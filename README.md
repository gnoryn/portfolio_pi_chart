1. Purpose:

    To visually represent portfolio exposure of stocks with PI charts

    This will enable rebalancing or diversification if uncomfortable with exposure to certain stocks or industry in terms of investment value or annual dividend



2. Mechanism:

    Price of the stock is obtained using yfinance

    The value or dividend of the stocks are converted to a common currency to enable comparison and percentages using forex-python


3. Usage:

    Modify input file ( columns ): 
    - Stock symbol - find it on Yahoo Finance
    - No of shares held 
    - Dividend per share annually

    ./portfolio_pichart.py (input file)

    When using CSV example :

        ./portfolio_pichart.py -i example.csv

    When Using dataframe.pkl :

        ./portfolio_pichart.py -df dataframe.pkl


    Should get the same image as example.png

4. Requires: 

    1. yfinance 
    2. forex-python
    3. pandas
    4. matplotlib  
    5. argparse