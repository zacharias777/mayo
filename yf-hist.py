import yfinance as yf
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, time
import time as tm

conn_string = 'mysql+pymysql://admin:Mustard99!@homelander.cjysa866ww26.us-east-2.rds.amazonaws.com:3306/Stocks'

def get_yf_prices(tickers):
    """
    Downloads and transforms stock price data from Yahoo Finance.
    
    This function downloads 1-minute interval stock price data for the specified 
    tickers for the most recent trading day. It then reshapes the multi-level 
    DataFrame into a more usable format with a single-level column structure.
    
    Parameters:
    -----------
    tickers : str or list
        The stock ticker symbol(s) to download data for. Can be a single ticker
        as a string (e.g., 'AAPL') or a list of tickers (e.g., ['AAPL', 'MSFT']).
        
    Returns:
    --------
    pandas.DataFrame

      TIMESTAMP           DATE        TICKER CLOSE    HIGH     LOW      OPEN     VOLUME
    0 2023-06-01 09:30:00 2023-06-01  AAPL   173.450  173.750  173.270  173.320  134754
    1 2023-06-01 09:31:00 2023-06-01  AAPL   173.435  173.590  173.320  173.450   17137
    """
    df = yf.download(tickers=tickers,
                    period="1d",
                    interval="1m", 
                    progress=False, 
                    auto_adjust= True)
    df = df.stack(1, future_stack=True)
    df = df.reset_index()
    df.columns = ['Datetime'] + list(df.columns[1:])
    df = df.sort_values(by=['Ticker', 'Datetime'])
    df['Date'] = df['Datetime'].dt.date
    df.rename(columns={'Datetime': 'TIMESTAMP', 
                       'Date': 'DATE',
                       'Ticker': 'TICKER',
                       'Close': 'CLOSE',
                       'High': 'HIGH',
                       'Low': 'LOW',
                       'Open': 'OPEN',
                       'Volume': 'VOLUME'}, inplace=True)
    df = df[['TIMESTAMP', 'DATE', 'TICKER', 'HIGH', 'LOW', 'OPEN', 'CLOSE', 'VOLUME']]

    df['TIMESTAMP'] = df['TIMESTAMP'].dt.tz_localize(None)
    df = df.drop_duplicates()
    print('--Found {} row for {} from Yahoo Finance'.format(len(df), str(tickers)))
    return df


def today_ticks(conn_string, dt):
    '''Retrieves stock minute data from the database for the current day.
    
    This function connects to a database using the provided connection string,
    queries the stock_minutes2 table for all records matching today's date,
    and returns the results as a pandas DataFrame.
    
    Parameters:
    -----------
    conn_string : str
        The database connection string used to establish a connection to the database.
        Should be in a format compatible with SQLAlchemy's create_engine function.
    
    Returns:
    --------
    pandas.DataFrame
      TIMESTAMP           DATE        TICKER CLOSE    HIGH     LOW      OPEN     VOLUME
    0 2023-06-01 09:30:00 2023-06-01  AAPL   173.450  173.750  173.270  173.320  134754
    1 2023-06-01 09:31:00 2023-06-01  AAPL   173.435  173.590  173.320  173.450   17137
    '''
    print('--Getting Todays ticks from the database')
    engine = create_engine(conn_string)
    formatted_date = dt.strftime("%Y-%m-%d")
    query = '''select * from stock_minutes2 where date = '{}';'''.format(formatted_date)
    try:
        # Execute query and load results into DataFrame
        df = pd.read_sql_query(query, engine)
        tickers = df['TICKER'].unique().tolist()
        print('--Found {} rows in the DB for {} as of {}'.format(len(df), 
                                                                 tickers, formatted_date))
        return df
    finally:
        # Always dispose of the engine when done
        engine.dispose()

def isolate_new_ticks(dft, dfy):
    '''Identifies and extracts new stock tick data by comparing two DataFrames.
    
    This function performs a left merge between two DataFrames to identify rows in the second
    DataFrame (dfy) that don't exist in the first DataFrame (dft), based on the 'TIMESTAMP' 
    and 'TICKER' columns. It then filters and returns only these new records with selected columns.
    
    Returns:
    --------
    pandas.DataFrame
        columns: ['TIMESTAMP', 'DATE', 'TICKER', 'HIGH', 'LOW', 'OPEN', 'CLOSE', 'VOLUME']
    '''
    df = dfy.merge(dft.drop_duplicates(), on=['TIMESTAMP','TICKER'], 
                   how='left', indicator=True, suffixes=(None, '_r'))
    df = df[df['_merge']=='left_only']
    df = df[['TIMESTAMP', 'DATE', 'TICKER', 'HIGH', 'LOW', 'OPEN', 'CLOSE', 'VOLUME']]
    tickers = df['TICKER'].unique().tolist()
    print('--Isolated {} new rows for {}'.format(len(df), tickers))
    return df

def insert_rows(df):
    '''Inserts rows from a DataFrame into the stock_minutes2 database table.
    
    This function takes a pandas DataFrame containing stock minute data and
    appends it to the 'stock_minutes2' table in a database specified by a global
    connection string. It handles the database connection, performs the insertion
    operation, and ensures proper cleanup of database resources'''

    table = "stock_minutes2"
    print('--Inserting {} rows into {}'.format(len(df), table))
    engine = create_engine(conn_string)
    try:
        df.to_sql(
            name=table,
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000
        )
        print('--Success!')
    finally:
        engine.dispose()   


def add_new_ticks(conn_string, dt):
    #get the existing ticks from the db for today
    dft = today_ticks(conn_string, dt)
    
    #get the new ticks from yahoo finance
    dfy = get_yf_prices(["F", "TSLA"])
    
    #make a df of differences
    df_new = isolate_new_ticks(dft, dfy)

    #insert the new rows to the database
    insert_rows(df_new)

def open_market(dt):
    market = True 
    time_now = dt.time()
    market_open = time(8,30,0)
    market_close = time(14,59,0)

    if time_now > market_open and time_now < market_close:
        market = True
        print('---market is open')
    else:
        market = False
        print('---market is closed')
    return market
    
if __name__ == "__main__":
    dt = datetime.now()
    formatted_date = dt.strftime("%Y-%m-%d")
    print('YH-HIST INITIAL STARTUP')
    print('$$$$$$$$$$$$$$$$$$$$$$$$$$')
    print('TODO: deal with NA Data')
    print('TODO: make it handle afternoon runs where it doesnt get eod data')

    while True:
        dt = datetime.now()
        print(dt.strftime("%Y-%m-%d %H:%M:%S"))
        print('-----------------------')
        if open_market(dt):
            add_new_ticks(conn_string, dt)
        tm.sleep(45*60) #run every 45 min