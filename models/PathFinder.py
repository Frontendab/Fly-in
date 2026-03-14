from typing import List, Dict
from .Drone import Drone
from .Zone import Zone, ZoneTypes
from .Graph import Graph
from heapq import heappush, heappop
from math import dist
from itertools import count
from collections import defaultdict


class PathFinder:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.counter = count()
        self.zone_occupancy: Dict[int, Dict[str, int]] = (
            defaultdict(lambda: defaultdict(int))
        )
        self.edge_occupancy: Dict[int, Dict[tuple, int]] = (
            defaultdict(lambda: defaultdict(int))
        )

    def get_path(
        self, drone: Drone, start: Zone, end: Zone,
    ) -> List[Zone]:
        open_list = [(0.0, next(self.counter), 0, start, [start])]
        visited = set()

        while open_list:
            _, _, current_turn, current_zone, path = heappop(open_list)

            if current_zone == end:
                self.__reserve_path(path)
                return path

            state = (current_zone.name, current_turn)
            if state in visited:
                continue
            visited.add(state)

            for neighbor in current_zone.target_zone:

                if neighbor.zone_type == ZoneTypes.BLOCKED:
                    continue

                priority_bonus = (
                    0.1 if neighbor.zone_type == ZoneTypes.PRIORITY else 0.0
                )

                arrival_turn = current_turn + neighbor.g

                if (
                    self.__is_zone_available(neighbor, current_turn)
                    and self.__is_link_available(
                        current_zone, neighbor, current_turn
                    )
                ):
                    new_path = path + ([neighbor] * neighbor.g)

                    g = arrival_turn
                    h = self.__calc_h_distance(neighbor)
                    heappush(
                        open_list, (
                            g + h - priority_bonus,
                            next(self.counter), arrival_turn,
                            neighbor, new_path
                        )
                    )

                wait_turn = current_turn + 1
                if self.__is_zone_available(current_zone, wait_turn):
                    g = wait_turn
                    h = self.__calc_h_distance(current_zone)
                    heappush(
                        open_list, (
                            g + h + 0.5,
                            next(self.counter), wait_turn,
                            current_zone, path + ([current_zone] * wait_turn)
                        )
                    )
        return []

    def __is_zone_available(self, zone: Zone, turn: int) -> bool:
        if zone == self.graph.start_zone or zone == self.graph.end_zone:
            return True
        max_capacity = getattr(zone, "max_drones", 1)
        return self.zone_occupancy[turn][zone.name] < max_capacity

    def __is_link_available(self, z1: Zone, z2: Zone, turn: int) -> bool:
        edge = tuple(sorted((z1.name, z2.name)))
        connection = self.graph.get_connection(
            f"{z1.name}-{z2.name}"
        )
        max_link = getattr(connection, "max_link_capacity", 1)
        return self.edge_occupancy[turn][edge] < max_link

    def __reserve_path(self, path: List[Zone]) -> None:
        t = 0
        for i in range(len(path)):
            current_zone = path[i]
            self.zone_occupancy[t][current_zone.name] += 1

            if i < len(path) - 1:
                next_zone = path[i + 1]
                if next_zone.name != current_zone.name:
                    edge = tuple(
                        sorted(
                            (current_zone.name, next_zone.name)
                        )
                    )
                    self.edge_occupancy[t][edge] += 1
                t += 1
            else:
                t += 1

    def __calc_h_distance(self, zone: Zone) -> float:
        return (
            dist(
                (zone.x, zone.y),
                (self.graph.end_zone.x, self.graph.end_zone.y),
            )
        )

    def a_star_search(self) -> None:
        self.zone_occupancy.clear()
        self.edge_occupancy.clear()

        drones = sorted(
            self.graph.drones.values(),
            key=lambda drone: drone.id
        )

        for drone in drones:
            path = self.get_path(
                drone, self.graph.start_zone,
                self.graph.end_zone
            )
            drone.path = path
            if not path:
                print(f"Warning: No path found for {drone.id}")

    def generate_output(self) -> None:
        pass
