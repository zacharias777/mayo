import os
import pygame
import time
import random
import neat
import pandas as pd
from db_funcs import today_ticks
from datetime import datetime, timedelta
pygame.font.init()

WIDTH, HEIGHT = 1700, 500
WIN = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption('Candles')
gen = 0
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

    def __init__(self, line_height):
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
        self.just_sold = False
        self.line_height = line_height

    def buy_share(self, price, x):
        """
        make the bird jump
        :return: None
        """
        self.bought = True
        self.buy_price = price
        self.stop_loss_px = self.buy_price * STOP_LOSS
        self.stop_gain_px = self.buy_price * STOP_GAIN

    
    def sell_if_needed(self, price, x, r):
        if self.bought:
            #CALCULATE PNL
            self.pnl = price - self.buy_price
            self.buy_line = pygame.Rect(x, self.line_height, 4, 1)

            #SELL IF STOPLOSS IS HIT OR WE TAKE PROFIT OR ITS EOD
            if price < self.stop_loss_px or \
                price > self.stop_gain_px or \
                r >= len(df)-1:
                self.bought = False
                self.cumulative_pnl = self.cumulative_pnl + self.pnl
                self.buy_line = None
                self.just_sold = True
            
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
    def __init__(self, pnl, cum_pnl, k):
        #self.pnl_color = self.rg_color(pnl)
        self.cum_pnl_color = self.rg_color(cum_pnl)

        self.pnl_text = FONT.render('Algo {}: Cumulative PnL: {}, recent pnl: {}'.format(
            k,round(pnl),round(cum_pnl)), 1, self.cum_pnl_color)
        # self.cum_pnl_text = FONT.render('cumulative: {}'.format(
        #     round(cum_pnl,1)), 1, self.cum_pnl_color)
        print('Algo {}: Cumulative PnL: {}, recent pnl: {}'.format(
            k,round(pnl),round(cum_pnl)))

    def rg_color(self, num):
        if num >= 0:
            return 'green'
        else:
            return 'red' 
        
def log(algo, r):
    if r % 10 == 0:
        print('{}: bought: {}, buy_price: {}, pnl: {}, stop_loss: {}, stop_gain: {}'.format(
            r, algo.bought, 
            round(algo.buy_price,1), 
            round(algo.pnl,1), 
            round(algo.stop_loss_px,1), 
            round(algo.stop_gain_px,1)))
                
def draw(box, algos, reset_ui):

    #Reset the UI at the start of each loop thru the df
    if reset_ui:
        WIN.fill((0, 0, 0))
    #Draw the Candlestick 
    pygame.draw.rect(WIN, box.color, box.box)

    #If we've bought, draw the line
    k=0 #TODO - fix this. make algos a dict with 0123 keys
    WIN.fill("black", (0, 0, 300, 120))
    for algo in algos:
        if algo.buy_line:
            pygame.draw.rect(WIN, 'white', algo.buy_line)

        #If we've sold, calculate pnl, hide the line, and write statistics
        #if algo.just_sold:
        pbox = PNL_Box(algo.pnl, algo.cumulative_pnl, k)
        #WIN.fill("black", (0, 0, 300, 120))
        WIN.blit(pbox.pnl_text, (10,10+k*14))

        k=k+1
    pygame.display.update()
        
def eval_genomes(genomes, config):
    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = []
    algos = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        algos.append(Algo(random.randint(380,420)))
        ge.append(genome)

    run = True
    clock = pygame.time.Clock()
    r = 0

    while run and r < len(df)-1:
        reset_ui = False
        if r==0:
            reset_ui = True

        clock.tick(25)
        close_price = df.iloc[r]['CLOSE']
        box = CandleBox(df.iloc[r], r)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        for x, algo in enumerate(algos):  # give each bird a fitness of 0.1 for each frame it stays alive
            algo.just_sold = False
            ge[x].fitness = ge[x].fitness - 0.00001
            #bird.move()
            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[algos.index(algo)].activate((close_price, df.iloc[r]['VOLUME'], df.iloc[r]['OPEN']))

            if output[0] > 0.6 and algo.bought==False:
                algo.buy_share(close_price, box.x_position)
                #print(r, x, 'bought')

            algo.sell_if_needed(close_price, box.x_position, r)

            if algo.just_sold==True:
                #print(r, 'just sold',ge[x].fitness, x)
                ge[x].fitness = ge[x].fitness + algo.pnl

        draw(box, algos, reset_ui)

        #log(algo, r)
        #if r < len(df)-1:
        r = r + 1


def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 3)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
