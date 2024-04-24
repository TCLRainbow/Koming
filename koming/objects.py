from abc import ABC
from random import choice
from typing import Optional

import numpy as np
import pygame

from koming.data import _AttackableData, _AttackableLevelData, _TroopData, _TroopLevelData, _DefenceData, \
    _DefenceLevelData
from koming.pathfinding import a_star


class _CocObject(ABC):
    RESOURCE_FOLDER_PATH: str = None
    NAME: str = None

    def __init__(self, hp, hit_box: pygame.Rect):
        self.hp = hp
        self.hit_box = hit_box

    def __repr__(self):
        return f'{self.NAME}{self.hit_box.topleft}@{id(self):x}'

    @property
    def hit_box_slice(self):
        slice_x = slice(self.hit_box.x, self.hit_box.x+self.hit_box.w)
        slice_y = slice(self.hit_box.y, self.hit_box.y+self.hit_box.h)
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
    UPDATE_WEIGHT_WHEN_DAMAGED = False

    def __init__(self, data: _DefenceData, lvl_data: _DefenceLevelData,
                 lvl: int, hit_box: pygame.Rect):
        self.__data: _DefenceData = data
        self.__lvl_data: _DefenceLevelData = lvl_data
        self.__lvl = lvl
        super().__init__(self.__data, self.__lvl_data, hit_box)

        self.__on_damaged_callbacks = []
        self.__on_destroy_callbacks = []
        self.__on_destroy_completed_callbacks = []

        self.bound_box = hit_box.inflate(2, 2)
        self.map_weight = self.hp

    @property
    def size(self) -> tuple[int, int]:
        return self.__data.size

    def on_damaged(self, func):
        if self.UPDATE_WEIGHT_WHEN_DAMAGED:
            # print(f'{self} will update weight on damaged')
            self.__on_damaged_callbacks.append(func)
        else:
            pass
            # print(f'{self} will not update weight on damaged')

    def on_destroy(self, func):
        # print(f'{self} will update weight on destroyed')
        self.__on_destroy_callbacks.append(func)

    def on_destroy_completed(self, func):
        self.__on_destroy_completed_callbacks.append(func)

    def receive_dmg(self, dmg: int):
        self.hp -= dmg
        print(f'{self} received dmg. HP: {self.hp}')
        if self.hp > 0:
            for func in self.__on_damaged_callbacks:
                func()
        else:
            for func in self.__on_destroy_callbacks:
                func()
            for func in self.__on_destroy_completed_callbacks:
                func()


class _Troop(_Attackable, ABC):
    RESOURCE_FOLDER_PATH = 'troops'

    def __init__(self, data: _TroopData, lvl_data: _TroopLevelData,
                 lvl: int, hit_box: pygame.Rect):
        self.__data = data
        self.__lvl_data = lvl_data
        self.__lvl = lvl
        self.__color = np.random.randint(127, 256), np.random.randint(200, 256), np.random.randint(127, 256)
        super().__init__(self.__data, self.__lvl_data, hit_box)

        self.__on_moved_callback = []

        self.target: Optional[_Defence] = None
        self.target_path: list[tuple[int, int]] = []

    @property
    def color(self):
        return self.__color

    def select_target(self, defences: list[_Defence]):
        # Naive: Should filter targets then select closest
        self.target = choice(defences)
        print(f'{self} selected target {self.target}')

    def search_path(self, weight_map: np.ndarray):
        weight = weight_map[self.target.hit_box_slice].copy()
        weight_map[self.target.hit_box_slice] = 0
        self.target_path = a_star(weight_map, self.hit_box.topleft, self.target.hit_box.topleft)
        weight_map[self.target.hit_box_slice] = weight

    def approach_target(self):
        if self.target_path:
            old = self.hit_box.copy()
            self.hit_box.update(self.target_path[0], self.hit_box.size)
            self.target_path.pop(0)
            for func in self.__on_moved_callback:
                func(old)
            return True
        return False

    def attack(self):
        if self.target.hp > 0:  # Should remove later becuz should reselect target
            self.target.receive_dmg(int(self.dph))

    def on_moved(self, func):
        self.__on_moved_callback.append(func)


class Barbarian(_Troop):
    NAME = 'barbarian'

    def __init__(self, data: _TroopData, lvl_data: _TroopLevelData,
                 lvl: int, hit_box: pygame.Rect):
        super().__init__(data, lvl_data, lvl, hit_box)


class Archer(_Troop):
    NAME = 'archer'

    def __init__(self, data: _TroopData, lvl_data: _TroopLevelData,
                 lvl: int, hit_box: pygame.Rect):
        super().__init__(data, lvl_data, lvl, hit_box)


class Giant(_Troop):
    NAME = 'giant'

    def __init__(self, data: _TroopData, lvl_data: _TroopLevelData,
                 lvl: int, hit_box: pygame.Rect):
        super().__init__(data, lvl_data, lvl, hit_box)


class Goblin(_Troop):
    NAME = 'goblin'

    def __init__(self, data: _TroopData, lvl_data: _TroopLevelData,
                 lvl: int, hit_box: pygame.Rect):
        super().__init__(data, lvl_data, lvl, hit_box)


class OnePunchMan(_Troop):
    NAME = 'one punch man'

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
