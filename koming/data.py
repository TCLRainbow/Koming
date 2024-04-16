import sqlite3
from typing import Tuple


class _TroopLevelData:
    def __init__(self, record):
        self.damage_per_hit = record[0]
        self.hp = record[1]


class _TroopData:
    def __init__(self, record: Tuple[float, float]):
        self.range: float = record[0]
        self.atk_period: float = record[1]
        self.__levels: [_TroopLevelData] = []

    def get_level(self, level: int) -> _TroopLevelData:
        return self.__levels[level - 1]

    def add_level(self, lvl: _TroopLevelData):
        self.__levels.append(lvl)


class Database:
    def __init__(self, file):
        self.__con = sqlite3.connect(file)
        self.__troops = self.__load_data__()

    def __load_data__(self):
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

    def get(self, name: str):
        return self.__troops[name]
