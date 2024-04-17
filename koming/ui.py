from typing import Tuple

import pygame
from pygame.locals import *

from koming.battlefield import Village
from koming.objects import _Troop, _CocObject


class UIVillage(Village):
    SIZE = 800, 800

    def __init__(self, res_path: str):
        super().__init__()
        self.__resource_path = res_path + '/'
        self.screen = pygame.display.set_mode(UIVillage.SIZE)
        self.load_image(self.__resource_path + "background.png")
        pygame.display.init()
        pygame.display.set_caption("Pygame Tiled Demo")
        self.running = True

    def _get_coc_obj_resource_path_(self, obj: _CocObject):
        return f'{self.__resource_path}{obj.resource_folder_path}/{obj.name}.png'

    def add_troop(self, troop: _Troop, coord: Tuple[float, float]):
        super().add_troop(troop, coord)
        ui_coord = self.scaled_to_ui_coord(coord)
        tile_img = pygame.image.load(self._get_coc_obj_resource_path_(troop))
        self.screen.blit(tile_img, ui_coord)

    @staticmethod
    def scaled_to_ui_coord(scaled: Tuple[float, float]):
        return UIVillage.SIZE[0] * scaled[0], UIVillage.SIZE[1] * scaled[1]

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

                elif event.type == KEYDOWN:
                    if event.key == K_l:
                        pass

        pygame.quit()

    def load_image(self, file):
        image = pygame.image.load(file)
        image = pygame.transform.scale(image, UIVillage.SIZE)
        rect = image.get_rect()

        self.screen.blit(image, rect)
        pygame.display.update()
