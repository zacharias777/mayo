import config
import trade_strat
import robin_stocks.robinhood as rh
import datetime as dt
import time



def login(days):
    time_logged_in = 60*60*24*days
    response = rh.authentication.login(username=config.USERNAME,
                            password=config.PASSWORD,
                            expiresIn=time_logged_in,
                            scope='internal',
                            by_sms=False,
                            store_session=True)
    #print(response)

def open_market():
    market = True 
    time_now = dt.datetime.now().time()
    market_open = dt.time(8,30,0)
    market_close = dt.time(14,59,0)

    if time_now > market_open and time_now < market_close:
        market = True
        #print('### market is open')
    else:
        #print('### market is closed')
        #market = False #comment in or out to un after hrs
        pass
    return market

def logout():
    rh.authentication.logout()    
    print('logged out')            

def get_stocks():
    stocks = ['F','CNET']      
    #stocks = ['TSLA']      
    return stocks   

def get_cash():
    rh_cash = rh.account.build_user_profile()
    cash = float(rh_cash['cash'])
    equity = float(rh_cash['equity'])
    print('Available Cash: {}, Equity: {}'.format(cash, equity))
    return(cash, equity)

def get_holdings_and_bought_price(stocks):
    holdings= {stocks[i]: 0 for i in range(0, len(stocks))}
    bought_price= {stocks[i]: 0 for i in range(0, len(stocks))}
    rh_holdings = rh.account.build_holdings()
    for stock in stocks:
        try: 
            holdings[stock] = int(float(rh_holdings[stock]['quantity']))
            bought_price[stock] = float(rh_holdings[stock]['average_buy_price'])
        except:
            holdings[stock] = 0
            bought_price[stock] = 0
        print('We currently own {} of {} for avg buy price {}'.format(holdings[stock],
                                                                  stock,
                                                                  bought_price[stock]))
    return (holdings, bought_price)


def sell(stock):
    print('### Trying to SELL {}'.format(stock))
    sell_order = rh.orders.order_sell_market(symbol=stock, quantity=1)
    print('sell_order',sell_order)

def buy(stock):
    print('### Trying to BUY {}'.format(stock))
    buy_order = rh.orders.order_buy_market(symbol=stock, quantity=1)
    print('buy_order:',buy_order)

if __name__ == "__main__":
    print('running from __main__')
    login(5)
    open_market()

    stocks = get_stocks()
    print('lets make some money')
    cash, equity = get_cash()
    holdings, bought_price = get_holdings_and_bought_price(stocks)
    ts = trade_strat.Trader(stocks, False)
    while open_market():
        print('-------------------')
        prices = rh.stocks.get_latest_price(stocks)
        print('prices:', prices)
        
        for i, stock in enumerate(stocks):
            price = float(prices[i])
            print('{} = ${}'.format(stock, price))

            data = ts.get_historical_price(stock,span='day')
            sma = ts.get_sma(stock, data, 4)
            p_sma = ts.get_price_sma(price, sma)
            trade = ts.trade_signal(stock, price)
            if trade == 'BUY':
                if holdings[stock] == 0:                    
                    buy(stock)
            elif trade == 'SELL':
                if holdings[stock] != 0:
                    sell(stock)
        time.sleep(30)