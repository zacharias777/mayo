import yfinance as yf
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, time
import time as tm

conn_string = 'mysql+pymysql://admin:Mustard99!@homelander.cjysa866ww26.us-east-2.rds.amazonaws.com:3306/Stocks'

def today_ticks(dt, ticker='all', conn_string=conn_string):
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
    if ticker=='all':
        query = '''select * from stock_minutes2 where date = '{}';'''.format(formatted_date)
    else:
        query = '''select * from stock_minutes2 
                   where DATE = '{}'
                   and TICKER = '{}';'''.format(formatted_date, ticker)
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

if __name__ == "__main__":
    dt = datetime.now()
    df = today_ticks(dt, 'TSLA')
    print(df)