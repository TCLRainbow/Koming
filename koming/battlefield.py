from koming.objects import _Troop, _Defence


class Village:
    SIDE_LENGTH = 44

    def __init__(self):
        self.troops: list[tuple[_Troop, tuple[float, float]]] = []
        self.defences: list[tuple[_Defence, tuple[float, float]]] = []

    def add_troop(self, troop: _Troop, coord: tuple[float, float]):
        self.troops.append((troop, coord))

    def add_defence(self, defence: _Defence, coord: tuple[float, float]):
        self.defences.append((defence, coord))
