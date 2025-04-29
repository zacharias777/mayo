
import pygame
import time
import random
import pandas as pd
from db_funcs import today_ticks
from datetime import datetime, timedelta
pygame.font.init()

WIDTH, HEIGHT = 1700, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
#WIN2 = pygame.display.set_mode((300,300))
pygame.display.set_caption('Candles')

FONT_HEIGHT = 15
FONT = pygame.font.SysFont("comicsans", FONT_HEIGHT)
STOP_LOSS = .88
STOP_GAIN = 1.12

def draw(box, rg, pnl, cum_pnl, show_pnl, x_position, buy_line = None):
    #WIN.fill((0, 0, 0))

    
    pygame.draw.rect(WIN, rg, box)
    if buy_line:
        pygame.draw.rect(WIN, 'white', buy_line)

    if show_pnl:
        if pnl >= 0:
            pnl_col = 'green'
        else:
            pnl_col = 'red'

        if cum_pnl >= 0:
            cum_pnl_col = 'green'
        else:
            cum_pnl_col = 'red'

        pnl_text = FONT.render('pnl: {}'.format(round(pnl,1)), 1, pnl_col)
        cum_pnl_text = FONT.render('cumulative: {}'.format(round(cum_pnl,1)), 1, cum_pnl_col)
        #WIN.blit(pnl_text, (x_position, HEIGHT - 95))
        #WIN.blit(cum_pnl_text, (x_position, HEIGHT - (95 - FONT_HEIGHT)))

        WIN.fill("black", (0, 0, 300, 120))
        WIN.blit(cum_pnl_text, (10,10))
        WIN.blit(pnl_text, (10,45))

    pygame.display.update()

    

dt = datetime.now() - timedelta(days=1)
df = today_ticks(dt, 'TSLA')
df.to_clipboard()

print(df)
 
scale_sub = 220
scale_mult = 8
for col in ['HIGH','OPEN','LOW','CLOSE']:
    df[col]= df[col] - scale_sub
    df[col]= df[col] * scale_mult

print(df)
def main():
    run = True
    clock = pygame.time.Clock()
    r = 0
    buy = False
    buy_price = 0
    buy_line = None
    pnl = 0
    stop_loss_px = 0 
    stop_gain_px = 0
    cumulative_pnl = 0


    while run:
        clock.tick(25)
        #print(df.iloc[r])
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                buy = True
                buy_price = df.iloc[r]['CLOSE']
                stop_loss_px = buy_price * STOP_LOSS
                stop_gain_px = buy_price * STOP_GAIN
            if event.type == pygame.QUIT:
                run = False
                break

        x_position = r*4
        top = HEIGHT - (df.iloc[r]['HIGH'])
        width = 2
        mb_height = abs(df.iloc[r]['HIGH'] - df.iloc[r]['LOW'])

        if df.iloc[r]['CLOSE'] > df.iloc[r]['OPEN']:
            rg = 'green'
        else:
            rg = 'red'

        main_box = pygame.Rect(x_position, top, width, mb_height)

        show_pnl = False
        if buy:
            buy_line = pygame.Rect(x_position, HEIGHT-100, 4, 1)
            pnl = df.iloc[r]['CLOSE'] - buy_price

            #IF WE SELL, 
            #EITHER BECAUSE THE STOPLOSS IS HIT OR WE TAKE PROFIT
            if df.iloc[r]['CLOSE'] < stop_loss_px or \
                df.iloc[r]['CLOSE'] > stop_gain_px or \
                r >= len(df)-1:
                buy = False
                show_pnl = True
                cumulative_pnl = cumulative_pnl + pnl

        draw(main_box, rg, pnl, cumulative_pnl, show_pnl, x_position, buy_line)

        if r % 10 == 0:
            print(r, buy, buy_price, pnl, stop_loss_px, stop_gain_px)
        if r < len(df)-1:
            r = r + 1


    pygame.quit()

if __name__ == "__main__":
    main()
