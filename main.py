from koming.data import Database
from koming.ui import UIVillage

if __name__ == '__main__':
    game = UIVillage('resources')
    db = Database('koming.sqlite')

    game.run()
