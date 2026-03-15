from typing import List, Dict
from .Drone import Drone
from .Zone import Zone, ZoneTypes
from .Graph import Graph
from heapq import heappush, heappop
from math import dist
from itertools import count
from collections import defaultdict


class PathFinder:
    """PathFinder the class is responsible about
        find the best path from the start to the end
        and the output of drone movements
    """

    def __init__(self, graph: Graph) -> None:
        """__init__ is use to assign values to the current instance
        """
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
        """get_path: Is used to find the best path from the start to end

        Args:
            drone (Drone): the current drone you want find
                it pass to move on it
            start (Zone): The start zone you want find the path from it
            end (Zone): The end zone you want find the path to it

        Returns:
            List[Zone]: Return the full path from the start zone to the end,
                otherwise return []
        """

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
        # TODO: I have to write a return msg
        """__is_zone_available: Is used to check if the current zone
            is available it or it contain the max of drones

        Args:
            zone (Zone): the zone you want check it
            turn (int): the turn you want check if the zone available on it

        Returns:
            bool: 
        """
        if zone == self.graph.start_zone or zone == self.graph.end_zone:
            return True
        max_capacity = getattr(zone, "max_drones")
        return self.zone_occupancy[turn][zone.name] < max_capacity

    def __is_link_available(self, z1: Zone, z2: Zone, turn: int) -> bool:
        # TODO: I have to write a return msg
        """__is_link_available: Is used to check if the current link
            connection between two zones is available it
            or it contain the max of link capacity

        Args:
            z1 (Zone): the first zone is connected with second
            z2 (Zone): the second zone is connected with first
            turn (int): the turn you want check if the link available on it

        Returns:
            bool: 
        """
        edge = tuple(sorted((z1.name, z2.name)))
        connection = self.graph.get_connection(
            f"{z1.name}-{z2.name}"
        )
        max_link = getattr(connection, "max_link_capacity", 1)
        return self.edge_occupancy[turn][edge] < max_link

    def __reserve_path(self, path: List[Zone]) -> None:
        # TODO: I have to write docstring for this function
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
        """__calc_h_distance: Is used to calculate the h(Approximate distance)
            between the current zone and the end's zone(goal)

        Args:
            zone (Zone): the current zone you want calculate
                h(Approximate distance) to it from the end's zone(goal)

        Returns:
            float: Return the (Euclidean distance) between two points
                current zone and end's zone(goal).
        """
        return (
            dist(
                (zone.x, zone.y),
                (self.graph.end_zone.x, self.graph.end_zone.y),
            )
        )

    def a_star_search(self) -> None:
        """a_star_search: Is used to start the algorithm's executing.
        """
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
        """generate_output: It used to count the max turn
            and print's drone movements
        """

        max_turns = 0
        for drone in self.graph.drones.values():
            max_turns = max(max_turns, len(drone.path))

        for t in range(1, max_turns):
            current_turn_moves = []
            for drone in self.graph.drones.values():
                if t < len(drone.path):
                    prev = drone.path[t-1]
                    curr = drone.path[t]
                    if curr.zone_type == ZoneTypes.RESTRICTED and prev == curr:
                        dest_zone = (
                            drone.path[t + 1]
                            if (t + 1) < len(drone.path) else drone.path[t]
                        )
                        current_turn_moves.append(
                            f"{drone.id}-{prev.name}-{dest_zone.name}"
                        )
                    elif curr != prev:
                        if (
                            (curr == self.graph.end_zone)
                            or (curr != self.graph.start_zone)
                        ):
                            current_turn_moves.append(
                                f"{drone.id}-{curr.name}"
                            )
            if current_turn_moves:
                print(" ".join(current_turn_moves))
