from koming.battlefield import UIVillage
from koming.data import Database
from koming.objects import *

VILLAGE_SIDE_LEN = 44

if __name__ == '__main__':
    db = Database('koming.sqlite')
    game = UIVillage(VILLAGE_SIDE_LEN, db, 'resources', True)

    cannon = game.add_defence(Cannon, 1)
    walls = [game.add_defence(Wall, 1) for i in range(16)]

    barb = game.add_troop(Barbarian, 1)

    game.render()
    input('Ready')
    game.run()
