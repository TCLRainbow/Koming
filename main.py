from koming.data import Database
from koming.ui import Game

if __name__ == '__main__':
    game = Game('resources/background.png')
    db = Database('koming.sqlite')
    game.run()
