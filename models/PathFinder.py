from typing import List, Tuple
from .Drone import Drone
from .Zone import Zone, ZoneTypes
from .Graph import Graph
from heapq import heappush, heappop
from math import dist
from itertools import count


# TODO: I have to add max_drones, max_link_capacity, use space time...


class PathFinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.counter = count()

    def get_path(
        self, drone: Drone, start: Zone, end: Zone,
    ) -> None:
        open_list = []
        closed_list = {
            (start.x, start.y):
            (False, start.x, start.y),
        }
        closed_list.update({
            (zone.x, zone.y):
            (False, zone.x, zone.y)
            for zone in self.graph.zones.values()
        })

        # HINT: Initialize start node
        start.h = 0
        start.f = 0

        heappush(
            open_list,
            (0.0, next(self.counter), start)
        )
        while len(open_list) > 0:
            _, _, best_zone = heappop(open_list)
            closed_list[(best_zone.x, best_zone.y)] = (
                True, best_zone.x, best_zone.y
            )
            for zone in best_zone.target_zone:

                if zone.zone_type == ZoneTypes.BLOCKED:
                    continue

                if self.__is_destination(zone) and not closed_list.get(
                    (zone.x, zone.y), None
                ):
                    return self.__get_final_path(best_zone)
                else:
                    new_h = self.__calc_h_distance(zone)
                    new_f = zone.g + new_h
                    if zone.f == float("inf") or zone.f >= new_f:
                        zone.h = new_h
                        zone.f = new_f
                        zone.parent = best_zone
                        heappush(
                            open_list,
                            (zone.f, next(self.counter), zone)
                        )

    def a_star_search(self) -> None:
        for drone in self.graph.drones.values():
            drone_surface = self.graph.get_drone(drone.id)
            drone_surface.path = self.get_path(
                drone_surface, self.graph.start_zone,
                self.graph.end_zone
            )

    def __is_destination(self, node: Zone) -> bool:
        if node == self.graph.end_zone:
            return True
        return False

    def __calc_h_distance(self, zone: Zone) -> int:
        return (
            dist(
                (zone.x, zone.y),
                (self.graph.end_zone.x, self.graph.end_zone.y),
            )
        )

    def __get_final_path(self, zone: Zone) -> List[Zone]:
        path = []
        current = zone
        while current is not None:
            path.append(current)
            current = getattr(current, "parent", None)
        path.reverse()
        path += [self.graph.end_zone]
        return path
