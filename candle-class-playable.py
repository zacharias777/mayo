
import pygame
import time
import random
import pandas as pd
from db_funcs import today_ticks
from datetime import datetime, timedelta
pygame.font.init()

WIDTH, HEIGHT = 1700, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Candles')

FONT_HEIGHT = 15
FONT = pygame.font.SysFont("comicsans", FONT_HEIGHT)
STOP_LOSS = .88
STOP_GAIN = 1.12

#GET THE DATAFRAME FROM THE DB
dt = datetime.now() - timedelta(days=12)
df = today_ticks(dt, 'TSLA')
df.to_clipboard()
df = df.drop_duplicates()
df = df.sort_values(by='TIMESTAMP', ascending=True)
#df = df.head(350)

#SCALE IT TO THE WINDOW. (TODO: IMPROVE THIS)
scale_sub = 220
scale_mult = 8
for col in ['HIGH','OPEN','LOW','CLOSE']:
    df[col]= df[col] - scale_sub
    df[col]= df[col] * scale_mult

print(df)


class Algo:
    """
    Algo class representing the individual trade strategy
    """

    def __init__(self):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.buy_price = 0  
        self.buy_line = None
        self.pnl = 0
        self.stop_loss_px = 0 
        self.stop_gain_px = 0
        self.cumulative_pnl = 0
        self.bought = False
        self.show_pnl = False

    def buy_share(self, price, x):
        """
        make the bird jump
        :return: None
        """
        self.bought = True
        self.buy_price = price
        self.stop_loss_px = self.buy_price * STOP_LOSS
        self.stop_gain_px = self.buy_price * STOP_GAIN
        self.show_pnl = False

    
    def sell_if_needed(self, price, x, r):
        if self.bought:
            #CALCULATE PNL
            self.pnl = price - self.buy_price
            self.buy_line = pygame.Rect(x, HEIGHT-100, 4, 1)

            #SELL IF STOPLOSS IS HIT OR WE TAKE PROFIT OR ITS EOD
            if price < self.stop_loss_px or \
                price > self.stop_gain_px or \
                r >= len(df)-1:
                self.bought = False
                self.cumulative_pnl = self.cumulative_pnl + self.pnl
                self.buy_line = None
                self.show_pnl = True
            
class CandleBox:
    def __init__(self, row, r):
        """

        """
        self.open = row['OPEN']
        self.close = row['CLOSE']
        self.x_position = r*4 
        self.top = HEIGHT - (row['HIGH'])
        self.width = 2
        self.height = abs(row['HIGH'] - row['LOW']) 
        self.box = pygame.Rect(self.x_position, self.top, self.width, self.height)
        self.color = self.rg_color(self.open, self.close)

    def rg_color(self, open, close):
        if close > open:
            return 'green'
        else:
            return 'red'    

class PNL_Box:
    def __init__(self, pnl, cum_pnl):
        self.pnl_color = self.rg_color(pnl)
        self.cum_pnl_color = self.rg_color(cum_pnl)
        self.pnl_text = FONT.render('pnl: {}'.format(round(pnl,1)), 1, self.pnl_color)
        self.cum_pnl_text = FONT.render('cumulative: {}'.format(
            round(cum_pnl,1)), 1, self.cum_pnl_color)

    def rg_color(self, num):
        if num >= 0:
            return 'green'
        else:
            return 'red' 
        
def draw(box, algo):

    #Draw the Candlestick 
    pygame.draw.rect(WIN, box.color, box.box)

    #If we've bought, draw the line
    if algo.buy_line:
        pygame.draw.rect(WIN, 'white', algo.buy_line)

    #If we've sold, calculate pnl, hide the line, and write statistics
    if algo.show_pnl:
        pbox = PNL_Box(algo.pnl, algo.cumulative_pnl)
        WIN.fill("black", (0, 0, 300, 120))
        WIN.blit(pbox.cum_pnl_text, (10,10))
        WIN.blit(pbox.pnl_text, (10,45))

    pygame.display.update()

def log(algo, r):
    if r % 10 == 0:
        print('{}: bought: {}, buy_price: {}, pnl: {}, stop_loss: {}, stop_gain: {}'.format(
            r, algo.bought, 
            round(algo.buy_price,1), 
            round(algo.pnl,1), 
            round(algo.stop_loss_px,1), 
            round(algo.stop_gain_px,1)))
        
def main():
    run = True
    clock = pygame.time.Clock()
    r = 0

    algo = Algo()
    while run:
        clock.tick(25)

        box = CandleBox(df.iloc[r], r)

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                algo.buy_share(df.iloc[r]['CLOSE'], box.x_position)

            if event.type == pygame.QUIT:
                run = False
                break

        algo.sell_if_needed(df.iloc[r]['CLOSE'], box.x_position, r)

        draw(box, algo)

        log(algo, r)
        if r < len(df)-1:
            r = r + 1


    pygame.quit()

if __name__ == "__main__":
    main()
