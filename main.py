from koming.battlefield import UIVillage
from koming.data import Database
from koming.objects import *

VILLAGE_SIDE_LEN = 44

if __name__ == '__main__':
    db = Database('koming.sqlite')
    game = UIVillage(VILLAGE_SIDE_LEN, db, 'resources', True)

    game.add_troop(Barbarian, 1)
    game.add_troop(Archer, 1)
    game.add_troop(Giant, 1)
    game.add_troop(Goblin, 1)

    wall = game.add_defence(Wall, 1)
    game.add_defence(Wall, 1)
    game.add_defence(Wall, 1)
    game.add_defence(Wall, 1)

    game.render()
    input('Ready')
    game.run()
