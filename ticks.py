import config
import robin_stocks.robinhood as rh
import robin_stocks.robinhood.helper as helper
import robin_stocks.urls as urls
import datetime as dt
import time

def login(days):
    time_logged_in = 60*60*24*days
    response = rh.authentication.login(username=config.USERNAME,
                            password=config.PASSWORD,
                            expiresIn=time_logged_in,
                            scope='internal',
                            by_sms=True,
                            store_session=True)
    print(response)


if __name__ == "__main__":
    print('running from __main__')
    
    login(5)
    #open_market()
