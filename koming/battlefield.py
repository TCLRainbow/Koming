import time
from typing import Type

import numpy as np
import pygame

from koming.data import Database, _DefenceData, _DefenceLevelData
from koming.objects import _Troop, _CocObject, _Defence

# Listening to Astronaut In The Ocean


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

    def try_direction_project(self, obj: _CocObject, scaled_distance: int):
        pos = obj.hit_box.topleft
        new_pos = pos[0] + scaled_distance, pos[1]
        if new_pos[0] < self.side_len:
            return new_pos, (1, 0)
        new_pos = pos[0] - scaled_distance, pos[1]
        if new_pos[0] >= 0:
            return new_pos, (-1, 0)
        new_pos = pos[0], pos[1] + scaled_distance
        if new_pos[1] < self.side_len:
            return new_pos, (0, 1)
        new_pos = pos[0], pos[1] - scaled_distance
        if new_pos[1] >= 0:  # Optimisation: Cond should be removed
            return new_pos, (0, -1)

    def random_troop_pos(self):
        return self.__rng.integers(0, self.side_len, 2)

    def random_defence_pos(self, defence_size: tuple[int, int]):
        return self.__rng.integers(0, self.side_len - np.array(defence_size) + 1, 2)

    def random_move_troop(self, troop: _Troop):
        if troop not in self.troops:
            raise ValueError(f'{troop} is not a part of this village!')
        pos = self.random_troop_pos()
        rect = pygame.Rect(pos, (1, 1))
        while self.collide_defence_bound_box(rect) or self.out_of_range(rect):
            pos = self.random_troop_pos()
            rect.update(pos, (1, 1))
        troop.hit_box.update(pos, (1, 1))

    def random_move_defence(self, defence: _Defence):
        if defence not in self.defences:
            raise ValueError(f'{defence} is not a part of this village!')
        pos = self.random_defence_pos(defence.size)
        rect = pygame.Rect(pos, defence.size)
        while self.collide_defence_hit_box(rect) or self.out_of_range(rect):
            pos = self.random_defence_pos(defence.size)
            rect.update(pos, defence.size)
        self.move_defence(defence, rect)

    def add_troop(self, cls: Type[_Troop], lvl, scaled_pos=None, retry=True):
        if scaled_pos is None:
            pos = self.random_troop_pos()
        else:
            pos = self.scaled_to_village_coord(scaled_pos)

        data = self.__db.get_troop(cls.NAME)
        lvl_data = data.get_level(lvl)
        rect = pygame.Rect(pos, (1, 1))

        if self.collide_defence_bound_box(rect) or self.out_of_range(rect):
            if not retry:
                return
            pos = self.random_troop_pos()
            rect.update(pos, (1, 1))
            while self.collide_defence_bound_box(rect) or self.out_of_range(rect):
                pos = self.random_troop_pos()
                rect.update(pos, (1, 1))

        troop = cls(data, lvl_data, lvl, rect)
        self.troops.append(troop)
        return troop

    def add_defence(self, cls: Type[_Defence], lvl, scaled_pos=None, retry=True):
        if self.troops:
            raise Exception("Cannot add defences once you start adding troops!")

        data: _DefenceData = self.__db.get_defence(cls.NAME)
        lvl_data: _DefenceLevelData = data.get_level(lvl)

        if scaled_pos is None:
            pos = self.random_defence_pos(data.size)
        else:
            pos = self.scaled_to_village_coord(scaled_pos)
        hit_box = pygame.Rect(pos, data.size)
        if self.collide_defence_hit_box(hit_box) or self.out_of_range(hit_box):
            if not retry:
                return
            pos = self.random_defence_pos(data.size)
            hit_box.update(pos, data.size)
            while self.collide_defence_hit_box(hit_box) or self.out_of_range(hit_box):
                pos = self.random_defence_pos(data.size)
                hit_box.update(pos, data.size)

        defence = cls(data, lvl_data, lvl, hit_box)

        @defence.on_damaged
        def on_dmg():
            print(f'Defence dmg callback, HP: {defence.hp}')
            self.update_map_defence_weight(defence)

        @defence.on_destroy
        def on_destroyed():
            print(f'Defence destroy callback, HP: {defence.hp}')
            self.remove_defence(defence)

        self.defences.append(defence)
        self.update_map_defence_weight(defence)
        return defence

    def remove_defence(self, defence: _Defence):
        self.map_weights[defence.hit_box_slice] = 0
        self.defences.remove(defence)

    def move_defence(self, defence: _Defence, new_rect):
        old_hit_box = defence.hit_box.copy()
        old_bound_box = defence.bound_box.copy()
        defence.hit_box.update(new_rect)
        defence.bound_box = new_rect.inflate(2, 2)
        return old_hit_box, old_bound_box

    def move_defences(self, defences: list[_Defence], new_rects: list[pygame.Rect]):
        old_hit_boxes = []
        old_bound_boxes = []
        for defence, new_rect in zip(defences, new_rects):
            old_hit_boxes.append(defence.hit_box.copy())
            old_bound_boxes.append(defence.bound_box.copy())
            defence.hit_box.update(new_rect)
            defence.bound_box = new_rect.inflate(2, 2)
        return old_hit_boxes, old_bound_boxes

    def update_map_defence_weight(self, defence: _Defence):
        self.map_weights[defence.hit_box_slice] = defence.map_weight

    def scaled_to_village_coord(self, coord: tuple[float, float]):
        return np.floor(np.array(coord) * self.side_len)

    def village_to_scaled_coord(self, coord: tuple[int, int]):
        return np.array(coord) / self.side_len

    def collide_defence_hit_box(self, rect: pygame.Rect):
        return rect.collideobjects(self.defences, key=lambda d: d.hit_box)

    def collide_defence_bound_box(self, rect: pygame.Rect):
        return rect.collideobjects(self.defences, key=lambda d: d.bound_box)

    def out_of_range(self, rect: pygame.Rect):
        return rect.x < 0 or rect.x >= self.side_len or rect.y < 0 or rect.y >= self.side_len

    def test_hit_valid(self, rect: pygame.Rect):
        return not (self.out_of_range(rect) or self.collide_defence_hit_box(rect))

    def setup_troop_target(self, troop: _Troop):
        troop.select_target(self.defences)
        if troop.target is None:
            return
        troop.search_path(self.map_weights)

        @troop.target.on_destroy
        def on_destroyed():
            print(f'{troop}: target {troop.target} destroyed')
            if self.defences:
                self.setup_troop_target(troop)
            else:
                troop.target = None

    def run(self):
        for troop in self.troops:
            self.setup_troop_target(troop)
        self.draw_troops_path()

        while self.defences:
            for troop in self.troops:
                if troop.target and not troop.approach_target():
                    troop.attack()
            time.sleep(1/3)
            pygame.event.pump()
            self.end_tick()

        print('Program ended')

    def draw_troops_path(self):
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
        self.__ratio = self.__size[0] / side_len
        self.__resource_path = res_path + '/'
        self.__ui_debug = ui_debug
        self.__tile_set = {}
        self.__bg = self._get_bg_()
        self.__defences_debug_surface = self._new_empty_surface()
        self.__defences_surface = self._new_empty_surface()
        self.__troops_debug_surface = self._new_empty_surface()
        self.__troops_surface = self._new_empty_surface()
        self.screen = pygame.display.set_mode(self.__size)

    def _get_coc_obj_resource_path_(self, obj: _CocObject):
        return f'{self.__resource_path}{obj.RESOURCE_FOLDER_PATH}/{obj.NAME}.png'

    def _new_empty_surface(self):
        return pygame.Surface(self.__size, pygame.SRCALPHA)

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
        ui_rect = rect.copy()
        ui_rect.update(
            rect.topleft[0] * self.__ratio, rect.topleft[1] * self.__ratio,
            rect.size[0] * self.__ratio, rect.size[1] * self.__ratio
        )
        return ui_rect

    def add_troop(self, cls: Type[_Troop], lvl, scaled_pos=None, retry=True):
        troop = super().add_troop(cls, lvl, scaled_pos, retry)
        tile = pygame.image.load(self._get_coc_obj_resource_path_(troop))
        tile = pygame.transform.scale(tile, (self.__ratio, self.__ratio))
        self.__tile_set.setdefault(troop.NAME, tile)
        self.draw_troop(troop)

        @troop.on_moved
        def on_moved(old: pygame.Rect):
            blank = (0,) * 4
            if self.__ui_debug:
                self.draw_rect(old, blank, self.__troops_debug_surface)
            self.draw_rect(old, blank, self.__troops_surface)
            self.draw_troop(troop)

        return troop

    def add_defence(self, cls: Type[_Defence], lvl, scaled_pos=None, retry=True):
        defence = super().add_defence(cls, lvl, scaled_pos, retry)
        if defence is None:
            return

        @defence.on_destroy_completed
        def on_destroy_completed():
            self.__troops_debug_surface.fill((0,) * 4)
            self.draw_troops_path()

        tile = pygame.image.load(self._get_coc_obj_resource_path_(defence))
        tile = pygame.transform.scale(tile, (self.__ratio*defence.size[0], self.__ratio*defence.size[1]))
        self.__tile_set.setdefault(defence.NAME, tile)
        self.draw_defence(defence)
        return defence

    def remove_defence(self, defence: _Defence):
        super().remove_defence(defence)
        blank = (0,)*4
        if self.__ui_debug:
            self.draw_rect(defence.bound_box, blank, self.__defences_debug_surface)
        self.draw_rect(defence.hit_box, blank, self.__defences_surface)

    def move_defence(self, defence: _Defence, new_rect):
        old_hit_box, old_bound_box = super().move_defence(defence, new_rect)
        blank = (0,) * 4
        if self.__ui_debug:
            self.draw_rect(old_bound_box, blank, self.__defences_debug_surface)
        self.draw_rect(old_hit_box, blank, self.__defences_surface)
        self.draw_defence(defence)
        return old_hit_box, old_bound_box

    def move_defences(self, defences: list[_Defence], new_rects: list[pygame.Rect]):
        old_hit_boxes, old_bound_boxes = super().move_defences(defences, new_rects)
        blank = (0,) * 4
        if self.__ui_debug:
            for bound_box in old_bound_boxes:
                self.draw_rect(bound_box, blank, self.__defences_debug_surface)
        for hit_box in old_hit_boxes:
            self.draw_rect(hit_box, blank, self.__defences_surface)
        for defence in defences:
            self.draw_defence(defence)
        return old_hit_boxes, old_bound_boxes

    def draw_rect(self, rect: pygame.Rect, rgb=(255, 255, 255), surface: pygame.Surface = None, scale=True):
        ui_rect = self.village_rect_to_ui(rect) if scale else rect
        if surface is None:
            surface = self.screen
        pygame.draw.rect(surface, rgb, ui_rect)

    def draw_troop(self, troop: _Troop):
        tile_img = self.__tile_set[troop.NAME]
        self.__troops_surface.blit(tile_img, self.village_rect_to_ui(troop.hit_box))

    def draw_defence(self, defence: _Defence):
        if self.__ui_debug:
            self.draw_rect(defence.bound_box, surface=self.__defences_debug_surface)
        tile_img = self.__tile_set[defence.NAME]
        self.__defences_surface.blit(tile_img, self.village_rect_to_ui(defence.hit_box))

    def render(self):
        surfaces_top_left = (0, 0)
        self.screen.blit(self.__bg, surfaces_top_left)
        if self.__ui_debug:
            self.screen.blit(self.__defences_debug_surface, surfaces_top_left)
        self.screen.blit(self.__defences_surface, surfaces_top_left)
        if self.__ui_debug:
            self.screen.blit(self.__troops_debug_surface, surfaces_top_left)
        self.screen.blit(self.__troops_surface, surfaces_top_left)
        pygame.display.update()

    def redraw_defences(self):
        blank = (0,)*4
        if self.__ui_debug:
            self.__defences_debug_surface.fill(blank)
        self.__defences_surface.fill(blank)
        for defence in self.defences:
            self.draw_defence(defence)

    def draw_troops_path(self):
        if self.__ui_debug:
            for troop in self.troops:
                for i in range(len(troop.target_path) - 1):
                    step = troop.target_path[i]
                    self.draw_rect(pygame.Rect(step, (1, 1)), troop.color, self.__troops_debug_surface)

    def end_tick(self):
        self.render()
