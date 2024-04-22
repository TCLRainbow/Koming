import time
from typing import Type

import numpy as np
import pygame

from koming.data import Database, _DefenceData, _DefenceLevelData
from koming.objects import _Troop, _CocObject, _Defence


class Village:
    def __init__(self, side_len: int, db: Database):
        self.__side_len = side_len
        self.__db = db
        self.__rng = np.random.default_rng()
        self.troops: list[_Troop] = []
        self.defences: list[_Defence] = []
        self.map_weights = np.zeros((side_len, side_len), dtype=np.uint)

    @property
    def side_len(self):
        return self.__side_len

    def random_pos(self):
        return self.__rng.uniform(0, (self.side_len-0.5)/self.side_len, 2)

    def add_troop(self, cls: Type[_Troop], lvl, scaled_pos=None):
        if not scaled_pos:
            scaled_pos = self.random_pos()

        data = self.__db.get_troop(cls.NAME)
        lvl_data = data.get_level(lvl)
        rect = pygame.Rect(self.scaled_to_village_coord(scaled_pos), (1, 1))
        troop = cls(data, lvl_data, lvl, rect)
        self.troops.append(troop)
        return troop

    def add_defence(self, cls: Type[_Defence], lvl, scaled_pos=None):
        if not scaled_pos:
            scaled_pos = self.random_pos()

        data: _DefenceData = self.__db.get_defence(cls.NAME)
        lvl_data: _DefenceLevelData = data.get_level(lvl)
        hit_box = pygame.Rect(self.scaled_to_village_coord(scaled_pos), data.size)
        defence = cls(data, lvl_data, lvl, hit_box)

        self.defences.append(defence)
        self.update_map_defence_weight(defence)
        return defence

    def remove_defence(self, defence: _Defence):
        self.map_weights[defence.hit_box_slice] = 0
        self.defences.remove(defence)

    def update_map_defence_weight(self, defence: _Defence):
        self.map_weights[defence.hit_box_slice] = defence.map_weight

    def scaled_to_village_coord(self, coord: tuple[float, float], translate=0):
        return round(coord[0] * self.side_len + translate), round(coord[1] * self.side_len + translate)

    def scaled_translate_by_village(self, coord: tuple[float, float], x, y):
        r = coord[0] + x / self.side_len, coord[1] + y / self.side_len
        return r

    def village_to_scaled_coord(self, coord: tuple[float, float], translate=0):
        return (coord[0] + translate) / self.side_len, (coord[1] + translate) / self.side_len

    def collide_defence_hit_box(self, rect: pygame.Rect):
        return rect.collideobjects(self.defences, key=lambda d: d.hit_box)

    def run(self):
        for i, troop in enumerate(self.troops):
            troop.select_target(self.defences, i)
            troop.search_path(self.map_weights)
            self.draw_path(troop)
        troops_to_move = [troop for troop in self.troops if troop.target_path]
        while troops_to_move:
            for troop in troops_to_move:
                troop.approach_target()
                if not troop.target_path:
                    troops_to_move.remove(troop)
            time.sleep(1/4)
            pygame.event.pump()
            self.end_tick()

        print('Program ended')
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                return

    def draw_path(self, troop: _Troop):
        pass

    def end_tick(self):
        pass


class UIVillage(Village):

    def __init__(self, side_len: int, db: Database, res_path: str, ui_debug: bool):
        super().__init__(side_len, db)
        pygame.display.init()
        pygame.display.set_caption("Pygame Tiled Demo")
        display_info = pygame.display.Info()
        display_w = round(min(display_info.current_w, display_info.current_h) * 0.9)
        print('Window size', display_w)

        self.__size = display_w, display_w
        self.__resource_path = res_path + '/'
        self.__ui_debug = ui_debug
        self.__bg = self._get_bg_()
        self.screen = pygame.display.set_mode(self.__size)

    def _get_coc_obj_resource_path_(self, obj: _CocObject):
        return f'{self.__resource_path}{obj.RESOURCE_FOLDER_PATH}/{obj.NAME}.png'

    def _get_bg_(self):
        surface = pygame.Surface(self.__size)
        if self.__ui_debug:
            cmyk = (
                (255, 0, 0),
                (200, 0, 0),
                (0, 0, 255),
                (0, 0, 200)
            )
            for x in range(self.side_len):
                color_i = x % 4
                for y in range(self.side_len):
                    rect = pygame.Rect((x, y), (1, 1))
                    self.draw_rect(rect, cmyk[color_i], surface)
                    color_i = (color_i + 1) % 4
        else:
            image = pygame.image.load(self.__resource_path + "background.png")
            image = pygame.transform.scale(image, self.__size)
            rect = image.get_rect()
            surface.blit(image, rect)
        return surface

    def scaled_to_ui_coord(self, scaled: tuple[float, float], translate=0):
        return self.__size[0] * scaled[0] + translate, self.__size[1] * scaled[1] + translate

    def village_rect_to_ui(self, rect: pygame.Rect):
        ratio = self.__size[0] / self.side_len
        ui_rect = rect.copy()
        ui_rect.update(
            rect.topleft[0] * ratio, rect.topleft[1] * ratio,
            rect.size[0] * ratio, rect.size[1] * ratio
        )
        return ui_rect

    def draw_rect(self, rect: pygame.Rect, rgb=(255, 255, 255), surface: pygame.Surface = None, scale=True):
        ui_rect = self.village_rect_to_ui(rect) if scale else rect
        if surface is None:
            surface = self.screen
        # ui_rect_surface = pygame.Surface(ui_rect.size)
        # ui_rect_surface.fill(rgb)
        # surface.blit(ui_rect_surface, ui_rect)
        pygame.draw.rect(surface, rgb, ui_rect)

    def draw_troop(self, troop: _Troop):
        tile_img = pygame.image.load(self._get_coc_obj_resource_path_(troop))
        self.screen.blit(tile_img, self.village_rect_to_ui(troop.hit_box))

    def draw_defence(self, defence: _Defence, bound_box, hit_box):
        if bound_box:
            bound_rect = defence.bound_box
            self.draw_rect(bound_rect)
        if hit_box:
            tile_img = pygame.image.load(self._get_coc_obj_resource_path_(defence))
            self.screen.blit(tile_img, self.village_rect_to_ui(defence.hit_box))

    def render(self):
        self.screen.blit(self.__bg, (0, 0))
        for defence in self.defences:
            self.draw_defence(defence, True, False)
        for defence in self.defences:
            self.draw_defence(defence, False, True)
        for troop in self.troops:
            self.draw_troop(troop)
        pygame.display.update()

    def draw_path(self, troop: _Troop):
        for i in range(len(troop.target_path) - 1):
            step = troop.target_path[i]
            self.draw_rect(pygame.Rect(step, (1, 1)), troop.color)
        pygame.display.update()

    def end_tick(self):
        for troop in self.troops:
            self.draw_troop(troop)
        pygame.display.update()
