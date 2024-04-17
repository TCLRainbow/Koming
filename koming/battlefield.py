from typing import List, Tuple

from koming.objects import _Troop


class Village:
    SIDE_LENGTH = 44

    def __init__(self):
        self.troops: List[Tuple[_Troop, Tuple[float, float]]] = []
        self.defences = []

    def add_troop(self, troop: _Troop, coord: Tuple[float, float]):
        self.troops.append((troop, coord))
