import random
from abc import ABC
from typing import Optional

import numpy as np
import pygame
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.core.node import GridNode
from pathfinding.finder.a_star import AStarFinder

from koming.data import _AttackableData, _AttackableLevelData, _TroopData, _TroopLevelData, _DefenceData, \
    _DefenceLevelData


class _CocObject(ABC):
    RESOURCE_FOLDER_PATH: str = None
    NAME: str = None

    def __init__(self, hp, hit_box: pygame.Rect):
        self.hp = hp
        self.hit_box = hit_box

    def __repr__(self):
        return f'{self.NAME}{self.hit_box.topleft}'

    @property
    def hit_box_slice(self):
        slice_x = slice(self.hit_box.topleft[0], self.hit_box.size[0])
        slice_y = slice(self.hit_box.topleft[1], self.hit_box.size[1])
        return slice_y, slice_x


class _Attackable(_CocObject, ABC):
    def __init__(self, atk_able: _AttackableData, atk_able_lvl: _AttackableLevelData, hit_box: pygame.Rect):
        self.__data = atk_able
        self.__lvl_data = atk_able_lvl
        super().__init__(atk_able_lvl.hp, hit_box)

    @property
    def range(self) -> float:
        return self.__data.range

    @property
    def atk_period(self) -> float:
        return self.__data.atk_period

    @property
    def dph(self) -> float:
        return self.__lvl_data.damage_per_hit


class _Defence(_Attackable, ABC):
    RESOURCE_FOLDER_PATH = 'defences'

    def __init__(self, data: _DefenceData, lvl_data: _DefenceLevelData,
                 lvl: int, hit_box: pygame.Rect):
        self.__data: _DefenceData = data
        self.__lvl_data: _DefenceLevelData = lvl_data
        self.__lvl = lvl
        super().__init__(self.__data, self.__lvl_data, hit_box)
        self.bound_box = hit_box.inflate(2, 2)
        self.map_weight = self.hp

    @property
    def size(self) -> tuple[int, int]:
        return self.__data.size


class _Troop(_Attackable, ABC):
    RESOURCE_FOLDER_PATH = 'troops'

    def __init__(self, data: _TroopData, lvl_data: _TroopLevelData,
                 lvl: int, hit_box: pygame.Rect):
        self.__data = data
        self.__lvl_data = lvl_data
        self.__lvl = lvl
        self.__color = np.random.randint(127, 256), np.random.randint(200, 256), np.random.randint(127, 256)
        super().__init__(self.__data, self.__lvl_data, hit_box)
        self.target: Optional[_Defence] = None
        self.target_path: list[GridNode] = []

    @property
    def color(self):
        return self.__color

    def select_target(self, defences: list[_Defence]):
        # Naive: Should filter targets then select closest
        self.target = random.choice(defences)

    def search_path(self, grid: Grid):
        try:
            start = grid.node(*self.hit_box.topleft)
        except IndexError:
            print('INDEX ERROR', self.hit_box)
            raise
        end = grid.node(*self.target.hit_box.topleft)
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        self.target_path: list[GridNode] = finder.find_path(start, end, grid)[0]
        self.target_path.pop(0)

    def approach_target(self):
        if self.target_path:
            self.hit_box.update(self.target_path[0].x, self.target_path[0].y,
                                self.hit_box.size[0], self.hit_box.size[1])
            self.target_path.pop(0)
            return True
        return False


class Barbarian(_Troop):
    NAME = 'barbarian'

    def __init__(self, data: _TroopData, lvl_data: _TroopLevelData,
                 lvl: int, hit_box: pygame.Rect):
        super().__init__(data, lvl_data, lvl, hit_box)


class Cannon(_Defence):
    NAME = 'cannon'

    def __init__(self, data: _DefenceData, lvl_data: _DefenceLevelData,
                 lvl: int, hit_box: pygame.Rect):
        super().__init__(data, lvl_data, lvl, hit_box)


class Wall(_Defence):
    NAME = 'wall'

    def __init__(self, data: _DefenceData, lvl_data: _DefenceLevelData,
                 lvl: int, hit_box: pygame.Rect):
        super().__init__(data, lvl_data, lvl, hit_box)
