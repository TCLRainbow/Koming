from koming.battlefield import UIVillage
from koming.data import Database
from koming.objects import *

if __name__ == '__main__':
    db = Database('koming.sqlite')
    game = UIVillage(44, db, 'resources', True)

    barb = game.add_troop(Barbarian, 1, (0.2, 0.4))
    cannon = game.add_defence(Cannon, 1, (0.4, 0.6))
    wall = game.add_defence(Wall, 1, (0.1, 0.56))

    game.render()
    game.run()
