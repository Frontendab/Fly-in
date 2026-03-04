from typing import List, Tuple
from .Drone import Drone
from .Zone import Zone, ZoneTypes
import heapq
import math


class PathFinder:
    def __init__(self) -> None:
        self.cost_zones = {
            ZoneTypes.NORMAL: 1,
            ZoneTypes.RESTRICTED: 2,
            ZoneTypes.PRIORITY: 1,
            ZoneTypes.BLOCKED: 0,
        }

    def get_path(
        self, drone: Drone, start: Zone, end: Zone,
        reserved_slots: int
    ) -> None:
        pq = [(0, start, [start])]

        print(
            f"Drone: {drone.id}, Start: {start.name}, End={end.name}, "
            f"Reserved slots: {reserved_slots}"
        )

        self.add_neighbors(drone, start, pq)

        print(pq)

    def add_neighbors(
        self, drone: Drone, start: Zone,
        pq: List[Tuple[int, Zone, List[Zone]]]
    ) -> None:
        _, zone, path = heapq.heappop(pq)
        for target in zone.target_zone:
            dx = target.x - drone.current_x
            dy = target.y - drone.current_y
            distance = math.hypot(dx, dy)
            heapq.heappush(
                pq,
                (distance, target, [path] + [target])
            )
            start = target
