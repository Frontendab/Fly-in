from .Drone import Drone
from .Zone import Zone


class PathFinder:
    def get_path(
        self, drone: Drone, start: Zone, end: Zone,
        reserved_slots: int
    ) -> None:
        pass
