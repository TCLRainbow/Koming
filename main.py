import pygame.display

from koming.objects import *
from koming.ui import UIVillage

if __name__ == '__main__':
    game = UIVillage('resources')
    db = Database('koming.sqlite')

    barb = Barbarian(db, 1)
    game.add_troop(barb, (0.2, 0.4))
    cannon = Cannon(db, 1)
    game.add_defence(cannon, (0.4, 0.6))

    pygame.display.update()
    game.run()
