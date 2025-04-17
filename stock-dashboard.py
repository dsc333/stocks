import streamlit as st
import time
import pandas as pd
import datetime
from datetime import time
from pprint import pprint
import pymongo
import os
import getpass
from pymongo.mongo_client import MongoClient
import certifi 
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import pytz 
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

load_dotenv()

MONGO_USER=os.environ.get('MONGO_USER')
MONGO_PASS=os.environ.get('MONGO_PASS')

# prompt user for username and password if not defined in .env
if not MONGO_USER:
    MONGO_USER = input('MongoDB username: ')
if not MONGO_PASS:
    MONGO_PASS = getpass.getpass()

def connect(db_name):
    # REPLACE THE DOMAIN WITH THE DOMAIN IN YOUR CONNECTION STRING
    uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}"+\
        f"@dsc333.qmlmqnt.mongodb.net/?retryWrites=true&w=majority&appName=dsc333"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    database = client[db_name]

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
    except Exception as e:
        print(e)
    
    return database


def get_stock_data(tickers, stocks):
    """Get all stock prices available in the stocks collection for the given tickers 
    
    Args:
        tickers: List of tickers 
        stocks: MongoDB collection of stock prices
    
    Returns:
        pd.DataFrame of stock prices indexed by datetime.
    """
    results = stocks.find({}, {"_id":0, "Ticker":1, "Date": 1, "Price":1})
    df = pd.DataFrame(results)
    
    return df.loc[df['Ticker'].isin(tickers)]


def main():
    st.title("Tech Stocks")

    # Get stocks collection
    db = connect(db_name='test')
    stocks = db['stocks']   # stocks collection on MongoDB

    # Stock tickers for the "Magnificient 7"
    tickers = ["AAPL", "GOOG", "MSFT", "NVDA", "AMZN", "TSLA", "META"]  
    selected_tickers = st.multiselect(
        "Select stock tickers",
        tickers,
        default=["AAPL"],
    )
    if not selected_tickers:
        st.warning("Please select at least one stock ticker.")
        return  # Stop if no tickers are selected

    # Refresh button for manual refresh
    if st.button("Refresh Data"):
        stock_data_df = get_stock_data(selected_tickers, stocks)
       
        for ticker in selected_tickers:
            df_filtered = stock_data_df.loc[stock_data_df['Ticker'] == ticker]
            fig = plt.figure()
            plt.plot(df_filtered['Date'], df_filtered['Price'])
            plt.title(ticker)
            plt.xlabel('Time')
            plt.ylabel('Price ($)')
            plt.rc('xtick', labelsize=6)

            ax = plt.gca()
            ax.xaxis.set_major_locator(MaxNLocator(20)) # Show maximum of 20 labels
            plt.gcf().autofmt_xdate()

            st.pyplot(fig)

        st.dataframe(stock_data_df)
        stock_data_df.to_csv('stocks.csv')  # save results to csv file
        

if __name__ == "__main__":
    main()


