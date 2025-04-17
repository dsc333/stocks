import yfinance as yf
import time
import pandas as pd
import datetime
from datetime import time
from pprint import pprint
import time
import pymongo
import os
import getpass
from pymongo.mongo_client import MongoClient
import certifi 
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import pytz 

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


def get_stock_data(tickers):
    """
    Fetches stock data from yfinance.  Handles errors and returns a list of dictionaries.

    Args:
        tickers (list): List of stock tickers (strings).

    Returns:
        list of dictionaries consisting of:
                      'Date', 'Ticker', 'Price'
    """
    data = []
    
    # Define the EST timezone
    est_tz = pytz.timezone('America/New_York')

    # Get the current date and time
    current_datetime = datetime.datetime.now(est_tz)
    now = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    for ticker_symbol in tickers:
        try:
            stock = yf.Ticker(ticker_symbol)
            info = stock.info  # Get the stock information
            if info:
                # Use regularMarketPrice if available, otherwise use currentPrice.
                current_price = info.get('regularMarketPrice') or info.get('currentPrice')
                stock_name = info.get('shortName', ticker_symbol) 
                stock_data = {
                    'Ticker': ticker_symbol,
                    'Date': now,
                    'Price': current_price
                }
                data.append(stock_data)
            else:
                st.error(f"Could not retrieve information for {ticker_symbol}.  Check the ticker symbol.")
                return None # Return None if any ticker fails.

        except Exception as e:
            st.error(f"Error fetching data for {ticker_symbol}: {e}")
            return None  # Return None on error

    return data


def is_time_between(start_time: time, end_time: time) -> bool:
    """Checks if the current time is between the start and end times.
    
    Args:
        start_time: The start time (datetime.time object).
        end_time: The end time (datetime.time object).
    
    Returns:
        True if the current time is between the start and end times, False otherwise.
    """

    # Define the EST timezone
    est_tz = pytz.timezone('America/New_York')

    now_time = datetime.datetime.now(est_tz).time()
    if start_time <= end_time:
        return start_time <= now_time <= end_time
    else:  # crosses midnight
        return start_time <= now_time or now_time <= end_time


def is_weekday():
    """
    Checks if the current day is a weekday (Monday-Friday).

    Returns:
        bool: True if the current day is a weekday, False otherwise.
    """
    now_time = datetime.datetime.now()
    # Monday is 0, Sunday is 6
    return now_time.weekday() < 5


def main():
    # Stock tickers for the "magnificient 7"
    tickers = ["AAPL", "GOOG", "MSFT", "NVDA", "AMZN", "META", "TSLA"]  

    db = connect(db_name='test')
    stocks = db['stocks']   # stocks collection on MongoDB
    
    # Example usage:
    trading_start = datetime.time(9, 30, 0)  # 9:30:00 AM
    trading_end = datetime.time(16, 30, 0)  # 4:30:00 PM

    # 2100 data fetches = approx one week of stock data at a minute resolution
    rem_fetches = 2100 
    while rem_fetches > 0:
        if is_time_between(trading_start, trading_end) and is_weekday():
            # fetch stock data
            stock_data = get_stock_data(tickers) 
            pprint(stock_data)

            # write to DB
            result = stocks.insert_many(stock_data)
            
            rem_fetches -= 1
        time.sleep(60)

if __name__ == "__main__":
    main()


