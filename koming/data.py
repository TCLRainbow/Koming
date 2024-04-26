import sqlite3
from abc import ABC


class _AttackableLevelData(ABC):
    def __init__(self, record: tuple[float, int]):
        self.damage_per_hit: float = record[0]
        self.hp: int = record[1]


class _AttackableData(ABC):
    def __init__(self, record: tuple[float, float]):
        self.range: float = record[0]
        self.atk_period: float = record[1]


class _TroopLevelData(_AttackableLevelData):
    def __init__(self, record):
        super().__init__(record)


class _TroopData(_AttackableData):
    def __init__(self, record: tuple[float, float]):
        super().__init__(record)
        self.__levels: list[_TroopLevelData] = []

    def get_level(self, level: int) -> _TroopLevelData:
        return self.__levels[level - 1]

    def add_level(self, lvl: _TroopLevelData):
        self.__levels.append(lvl)


class _DefenceLevelData(_AttackableLevelData):
    def __init__(self, record):
        super().__init__(record)


class _DefenceData(_AttackableData):
    def __init__(self, record: tuple[float, float, int, int]):
        parent_data: tuple[float, float] = record[0], record[1]
        super().__init__(parent_data)
        self.__levels: list[_DefenceLevelData] = []
        self.size: tuple[int, int]
        self.size = record[2:4]

    def get_level(self, level: int) -> _DefenceLevelData:
        return self.__levels[level - 1]

    def add_level(self, lvl: _DefenceLevelData):
        self.__levels.append(lvl)


class Database:
    def __init__(self, file):
        self.__con = sqlite3.connect(file)
        self.__troops = self._load_troops_()
        self.__defences = self._load_defences_()

    def _load_troops_(self):
        data = {}
        troop_records = self.__con.execute("SELECT * FROM Troops").fetchall()
        for troop_record in troop_records:
            troop_data = _TroopData(troop_record[1:])
            level_records = self.__con.execute(
                "SELECT * FROM TroopLevels WHERE Name = ?", (troop_record[0],)
            ).fetchall()
            for lvl_record in level_records:
                troop_data.add_level(_TroopLevelData(lvl_record[2:]))
            data[troop_record[0]] = troop_data
        return data

    def _load_defences_(self):
        data = {}
        defence_records = self.__con.execute("SELECT * FROM Defences").fetchall()
        for defence_record in defence_records:
            defence_data = _DefenceData(defence_record[1:])
            level_records = self.__con.execute(
                "SELECT * FROM DefenceLevels WHERE Name = ?", (defence_record[0],)
            ).fetchall()
            for lvl_record in level_records:
                defence_data.add_level(_DefenceLevelData(lvl_record[2:]))
            data[defence_record[0]] = defence_data
        return data

    def get_troop(self, name: str):
        return self.__troops[name]

    def get_defence(self, name: str):
        return self.__defences[name]
