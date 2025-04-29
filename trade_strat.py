import pandas as pd
import robin_stocks.robinhood.helper as helper
import robin_stocks.urls as urls
import config

class Trader():
    def __init__(self, stocks, test_mode):
        self.stocks = stocks
        self.sma_hour = {stock: 0 for stock in stocks}
        self.run_time = 0
        self.price_sma_hour = {stock: 0 for stock in stocks}
        self.test_mode = test_mode
        
        print('price_sma_hour: ', self.price_sma_hour)

    def get_historical_price(self, stock, span):
        span_interval = {'day': '5minute','week':'10minute','month':'hour','3month':'hour'}
        interval = span_interval[span]
        symbols = helper.inputs_to_set(stock)
        url = urls.historicals()
        payload = {'symbols': ','.join(symbols),
                   'interval': interval,
                   'span': span,
                   'bounds': 'regular'}

        if self.test_mode == True:
            data = config.EASY_24HR_HIST
        else:
            data = helper.request_get(url, 'results',payload)
        historical_data= []
        for item in data:
            for s in item['historicals']:
                historical_data.append(s)
        
        df = pd.DataFrame(historical_data)
    
        df['begins_at'] = pd.to_datetime(df['begins_at'])
        df['close_price'] = df['close_price'].astype('float')

        df = df.rename(columns={'close_price': stock})
        df = df.set_index('begins_at')
        df = df[[stock]]
        # df.to_clipboard()
        print(df) if self.test_mode else None
        return df

    def get_sma(self, stock, df, window=2):
        sma = df.rolling(window=window).mean()
        sma = round(float(sma[stock].iloc[-1]),4)
        print('SMA for {} periods: {}'.format(sma,window))
        return sma
    
    def get_price_sma(self, price, sma):
        price_sma = round(price/sma,4)
        print('Price div by SMA: {}'.format(price_sma))
        return price_sma
    
    def trade_signal(self,stock,price):
        # get new sma_hour every 5 min
        if self.run_time % 5 == 0:
            df_historical_prices = self.get_historical_price(stock, span='day')
            self.sma_hour[stock] = self.get_sma(stock, df_historical_prices[-4:])

        self.price_sma_hour[stock] = self.get_price_sma(price, self.sma_hour[stock])
        p_sma = self.price_sma_hour[stock]

        i1 = 'BUY' if self.price_sma_hour[stock]<1.0 else 'SELL' if self.price_sma_hour[stock]>1.0 else 'NONE'
        print('{}: {}'.format(stock, i1))
        return i1

if __name__ == "__main__":
    t = Trader(stocks=['CNET'], test_mode=True)  
    # print('jere')           
    # print(helper.inputs_to_set(['tsla', 'F','F']))   
    # print(urls.historicals())
    # print('----')

    df_hist = t.get_historical_price(stock=t.stocks[0], span='week')
    sma = t.get_sma(stock=t.stocks[0], df=df_hist, window=3)
    t.get_price_sma(df_hist[t.stocks[0]].iloc[-1], sma)
    t.trade_signal(stock=t.stocks[0], price=df_hist[t.stocks[0]].iloc[-1])