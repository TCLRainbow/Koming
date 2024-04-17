from abc import ABC, abstractmethod

from koming.data import Database


class _CocObject(ABC):
    def __init__(self, hp):
        self.hp = hp

    @property
    @abstractmethod
    def resource_folder_path(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class _Troop(_CocObject, ABC):
    def __init__(self, db: Database, lvl: int):
        self.__data = db.get(self.name)
        self.__lvl_data = self.__data.get_level(lvl)
        super().__init__(self.__lvl_data.hp)

    @property
    def resource_folder_path(self) -> str:
        return 'troops'

    @property
    def range(self) -> float:
        return self.__data.range

    @property
    def atk_period(self) -> float:
        return self.__data.atk_period

    @property
    def dph(self) -> float:
        return self.__lvl_data.damage_per_hit


class Barbarian(_Troop):
    def __init__(self, db: Database, lvl: int):
        super().__init__(db, lvl)

    @property
    def name(self) -> str:
        return 'barbarian'
