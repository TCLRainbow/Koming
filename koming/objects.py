from abc import ABC

import pygame

from koming.data import _AttackableData, _AttackableLevelData, _TroopData, _TroopLevelData, _DefenceData, \
    _DefenceLevelData


class _CocObject(ABC):
    RESOURCE_FOLDER_PATH: str = None
    NAME: str = None

    def __init__(self, hp, hit_box: pygame.Rect):
        self.hp = hp
        self.hit_box = hit_box


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


class _Troop(_Attackable, ABC):
    RESOURCE_FOLDER_PATH = 'troops'

    def __init__(self, data: _TroopData, lvl_data: _TroopLevelData,
                 lvl: int, hit_box: pygame.Rect):
        self.__data = data
        self.__lvl_data = lvl_data
        self.__lvl = lvl
        super().__init__(self.__data, self.__lvl_data, hit_box)


class _Defence(_Attackable, ABC):
    RESOURCE_FOLDER_PATH = 'defences'

    def __init__(self, data: _DefenceData, lvl_data: _DefenceLevelData,
                 lvl: int, hit_box: pygame.Rect):
        self.__data: _DefenceData = data
        self.__lvl_data: _DefenceLevelData = lvl_data
        self.__lvl = lvl
        super().__init__(self.__data, self.__lvl_data, hit_box)
        self.bound_box = hit_box.inflate(2, 2)

    @property
    def size(self) -> tuple[int, int]:
        return self.__data.size


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
