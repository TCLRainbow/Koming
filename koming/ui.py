import pygame
from pygame.locals import *

from koming.battlefield import Village
from koming.objects import _Troop, _CocObject, _Defence


class UIVillage(Village):

    def __init__(self, res_path: str):
        super().__init__()
        pygame.display.init()
        pygame.display.set_caption("Pygame Tiled Demo")
        display_info = pygame.display.Info()
        display_w = min(display_info.current_w, display_info.current_h) * 0.9
        self.size = display_w, display_w
        self.__resource_path = res_path + '/'
        self.running = True
        self.screen = pygame.display.set_mode(self.size)
        self.load_image(self.__resource_path + "background.png")

    def _get_coc_obj_resource_path_(self, obj: _CocObject):
        return f'{self.__resource_path}{obj.resource_folder_path}/{obj.name}.png'

    def add_troop(self, troop: _Troop, coord: tuple[float, float]):
        super().add_troop(troop, coord)
        ui_coord = self.scaled_to_ui_coord(coord)
        tile_img = pygame.image.load(self._get_coc_obj_resource_path_(troop))
        self.screen.blit(tile_img, ui_coord)

    def add_defence(self, defence: _Defence, coord: tuple[float, float]):
        super().add_defence(defence, coord)
        ui_coord = self.scaled_to_ui_coord(coord)
        tile_img = pygame.image.load(self._get_coc_obj_resource_path_(defence))
        self.screen.blit(tile_img, ui_coord)

    def scaled_to_ui_coord(self, scaled: tuple[float, float]):
        return self.size[0] * scaled[0], self.size[1] * scaled[1]

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
        image = pygame.transform.scale(image, self.size)
        rect = image.get_rect()

        self.screen.blit(image, rect)
        pygame.display.update()
