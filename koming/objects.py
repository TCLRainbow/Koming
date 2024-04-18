from abc import abstractmethod, ABC

from koming.data import _AttackableData, _AttackableLevelData, _TroopData, Database, _TroopLevelData, _DefenceData, \
    _DefenceLevelData


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


class _Attackable(_CocObject, ABC):
    def __init__(self, atk_able: _AttackableData, atk_able_lvl: _AttackableLevelData):
        self.__data = atk_able
        self.__lvl_data = atk_able_lvl
        super().__init__()

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
    def __init__(self, db: Database, lvl: int, pos):
        self.__data: _TroopData = db.get_troop(self.name)
        self.__lvl_data: _TroopLevelData = self.__data.get_level(lvl)
        super().__init__(self.__data, self.__lvl_data)
        self.pos = pos

    @property
    def resource_folder_path(self) -> str:
        return 'troops'


class _Defence(_Attackable, ABC):
    def __init__(self, db: Database, lvl: int, pos: tuple[float, float]):
        self.__data: _DefenceData = db.get_defence(self.name)
        self.__lvl_data: _DefenceLevelData = self.__data.get_level(lvl)
        super().__init__(self.__data, self.__lvl_data)
        self.__pos = pos

    @property
    def resource_folder_path(self) -> str:
        return 'defences'

    @property
    def size(self) -> tuple[int, int]:
        return self.__data.size

    @property
    def pos(self):
        return self.__pos


class Barbarian(_Troop):
    def __init__(self, db: Database, lvl: int, pos):
        super().__init__(db, lvl, pos)

    @property
    def name(self) -> str:
        return 'barbarian'


class Cannon(_Defence):
    def __init__(self, db: Database, lvl: int, pos):
        super().__init__(db, lvl, pos)

    @property
    def name(self) -> str:
        return 'cannon'


class Wall(_Defence):
    def __init__(self, db: Database, lvl: int, pos):
        super().__init__(db, lvl, pos)

    @property
    def name(self) -> str:
        return 'wall'
