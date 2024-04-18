import pygame.display

from koming.objects import *
from koming.battlefield import UIVillage

if __name__ == '__main__':
    game = UIVillage('resources')
    db = Database('koming.sqlite')

    barb = Barbarian(db, 1, (0.2, 0.4))
    game.add_troop(barb)
    cannon = Cannon(db, 1, (0.4, 0.6))
    game.add_defence(cannon)
    wall = Wall(db, 1, (0.1, 0.56))
    game.add_defence(wall)

    pygame.display.update()
    game.run()
