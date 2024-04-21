from koming.battlefield import UIVillage
from koming.data import Database
from koming.objects import *

if __name__ == '__main__':
    db = Database('koming.sqlite')
    game = UIVillage(44, db, 'resources', True)

    barb = game.add_troop(Barbarian, 1, (0.2, 0.4))
    for _ in range(3):
        game.add_troop(Barbarian, 1)
    # cannon = game.add_defence(Cannon, 1, (0.4, 0.6))
    wall = game.add_defence(Wall, 1, (0.1, 0.1))
    game.add_defence(Wall, 1, (0.5, 0.5))
    game.add_defence(Wall, 1, (0.8, 0.8))

    game.render()
    game.run()
