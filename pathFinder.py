"""
    PathFinder module for drone navigation.
"""

from typing import List, Tuple, Dict, cast
from classes import Zone, ZoneTypes, Graph
from heapq import heappush, heappop
from itertools import count
from collections import defaultdict


class PathFinder:
    """
    A* pathfinder for drone navigation with capacity constraints.

    Uses A* algorithm to find paths for drones while respecting zone
    and link capacities, and considering priority zones.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initialize a PathFinder instance.

        Args:
            graph (Graph): The graph containing zones and connections.
        """
        self.graph: Graph = graph
        self.counter: count[int] = count()
        self.shortest_dist: Dict[str, float] = self.__precompute_distances()
        # turn -> {'zones': {name: (current, max)},
        # 'connections': {name: (current, max)}}
        self.tracking: Dict[int, Dict[str, Dict[str, Tuple[int, int]]]] = {}

    def __precompute_distances(self) -> Dict[str, float]:
        """
        Precompute shortest distances from all zones to the end zone.

        Uses Dijkstra's algorithm (reversed from end) to calculate
        heuristic distances for A*.

        Returns:
            Dict[str, float]: Dictionary mapping zone names to distances.
        """

        dist: Dict[str, float] = {
            zone.name: float("inf") for zone in self.graph.zones.values()
        }
        start_name = self.graph.start_zone.name
        dist[start_name] = float("inf")

        end_name = self.graph.end_zone.name
        dist[end_name] = 0.0

        counter = 0
        open_list: List[Tuple[float, int, Zone]] = [
            (0, counter, self.graph.end_zone)
        ]

        while open_list:
            distance, _, zone = heappop(open_list)

            if distance > dist[zone.name]:
                continue

            if zone == self.graph.start_zone:
                break

            for neighbor in zone.target_zone_from_end:
                if neighbor.zone_type == ZoneTypes.BLOCKED:
                    continue

                # INFO: calculate the movement cost into the neightbor zone
                move_cost: float = float(neighbor.g)
                # Priority zones are considered "closer" to
                # the end to encourage routing through them
                if neighbor.zone_type == ZoneTypes.PRIORITY:
                    move_cost -= 0.5
                new_distance = distance + move_cost
                if new_distance < dist[neighbor.name]:
                    dist[neighbor.name] = new_distance
                    counter += 1
                    heappush(open_list, (new_distance, counter, neighbor))

        return dist

    def a_star_search(self) -> None:
        """
        Simulate the movement of all drones using
        a simplified A* search approach.

        This method iterates through simulation turns, for each turn
        deciding the best move or wait action for each unfinished
        drone based on heuristic distances to the end zone.
        It respects zone and link capacities, prioritizing drones closer
        to the end and encouraging movement through priority zones.
        The simulation continues until all drones have reached the end zone.
        Modifies drone paths and states in place.
        """
        drones = list(self.graph.drones.values())
        turn = 0

        # Track drones currently in transit toward a restricted zone.
        # {drone_id: (destination_zone, turns_left, connection_name)}
        in_transit: Dict[str, Tuple[Zone, int, str]] = {}

        while not all(drone.finished for drone in drones):
            turn += 1

            # reset per-turn usage
            edge_usage: Dict[Tuple[str, str], int] = defaultdict(int)
            moves: List[Tuple] = []
            edge: Tuple[str, str] = ("", "")

            # Count current occupancy excluding drones that
            # are already in transit
            current_zone_count: Dict[str, int] = defaultdict(int)
            for drone in drones:
                if drone.finished or drone.id in in_transit:
                    continue
                current_zone_count[drone.current_zone.name] += 1

            # Future occupancy for next turn, including stays
            # and accepted moves
            zone_next_count: Dict[str, int] = defaultdict(
                int, current_zone_count
            )

            # Short drones from 1 to last
            drones_sorted = sorted(
                drones,
                key=lambda d: self.shortest_dist.get(
                    d.current_zone.name, float("inf")
                )
            )

            for drone in drones_sorted:
                if drone.finished:
                    moves.append((drone, drone.current_zone, False, None))
                    continue

                # Drone currently in transit (restricted zone, turn 2)
                if drone.id in in_transit:
                    dest_zone, turns_left, conn_name = in_transit[drone.id]
                    turns_left -= 1

                    edge = cast(
                        Tuple[str, str],
                        tuple((conn_name.split("-")))
                    )
                    edge_usage[edge] += 1

                    if turns_left == 0:
                        # Arrives at destination this turn
                        del in_transit[drone.id]
                        zone_next_count[dest_zone.name] += 1
                        moves.append((drone, dest_zone, False, conn_name))
                    else:
                        # Still in transit (shouldn't happen with g=2)
                        # Kept for forward-compatibility with g > 2
                        in_transit[drone.id] = (
                            dest_zone, turns_left, conn_name
                        )
                        moves.append((drone, None, True, conn_name))

                    continue

                current = drone.current_zone
                best_neighbor = None
                best_score = float("inf")
                best_edge: Tuple[str, str] = ("", "")

                for neighbor in current.target_zone:
                    if neighbor.zone_type == ZoneTypes.BLOCKED:
                        continue

                    connection = self.graph.get_connection(
                        f"{current.name}-{neighbor.name}"
                    )

                    if not connection:
                        continue

                    edge = cast(
                        Tuple[str, str],
                        (current.name, neighbor.name)
                    )

                    # Link capacity check
                    if edge_usage[edge] >= connection.max_link_capacity:
                        continue

                    # Zone capacity check (skip for end zone)
                    if neighbor != self.graph.end_zone:
                        if neighbor.zone_type == ZoneTypes.RESTRICTED:
                            # Destination zone will be occupied next turn.
                            if (
                                zone_next_count[neighbor.name] >=
                                neighbor.max_drones
                            ):
                                continue
                        elif (
                            zone_next_count[neighbor.name] >=
                            neighbor.max_drones
                        ):
                            continue

                    # Heuristic score
                    distance = self.shortest_dist.get(
                        neighbor.name, float("inf")
                    )

                    # Priority bonus
                    if distance < best_score:
                        best_score = distance
                        best_neighbor = neighbor
                        best_edge = edge

                # Apply move
                if best_neighbor:
                    edge_usage[best_edge] += 1

                    # if the drone leaves its current zone this turn,
                    # decrement future count for the origin zone.
                    if drone.current_zone.name != best_neighbor.name:
                        zone_next_count[drone.current_zone.name] -= 1

                    if best_neighbor.zone_type == ZoneTypes.RESTRICTED:
                        # Turn 1 of 2: drone enters the connection
                        conn_name = f"{current.name}-{best_neighbor.name}"
                        in_transit[drone.id] = (best_neighbor, 1, conn_name)
                        moves.append((drone, None, True, conn_name))
                        zone_next_count[best_neighbor.name] += 1
                    else:
                        zone_next_count[best_neighbor.name] += 1
                        moves.append((drone, best_neighbor, False, None))
                else:
                    # Wait the current zone
                    moves.append((drone, current, False, None))

            # Apply moves
            for drone, new_zone, is_in_transit, conn_name in moves:
                if drone.finished:
                    continue

                if is_in_transit and conn_name:
                    # Record the connection waypoint in path
                    drone.path.append((turn, conn_name))

                elif new_zone is not None:
                    drone.current_zone = new_zone
                    drone.path.append((turn, new_zone.name))

                    if (
                        new_zone != self.graph.end_zone
                        and not self.is_valid_path(drone.current_zone)
                    ):
                        # Invalid state: drone didn't move but is
                        # not waiting in the same zone
                        raise ValueError(
                            "Invalid path: found a path that " +
                            "doesn't lead to the end zone."
                        )

                    if new_zone == self.graph.end_zone:
                        drone.finished = True

    def is_valid_path(self, current_zone: Zone) -> bool:
        """Check if there the valid path or not from start to end

        Args:
            current_zone (Zone): Current zone you want check
                if there valid path from it

        Returns:
            bool: If there valid path return True,
                otherwise return False
        """
        valid = []
        distance = self.shortest_dist.get(
            current_zone.name, float("inf")
        )

        if distance == float("inf"):
            return False

        for neighbor in current_zone.target_zone:
            if neighbor.zone_type != ZoneTypes.BLOCKED:
                valid.append(neighbor.name)
        if not valid:
            return False
        return True

    def generate_output(self) -> None:
        """
        Print the step-by-step drone movements in the required format.

        Each non-empty turn is printed as a space-separated list of
        movements in the form D<id>-<zone> or D<id>-<connection>.
        Followed by the state of zones and connections
        with current/max capacities.
        """

        all_moves: Dict[int, List[str]] = defaultdict(list)

        max_t: int = 0

        for drone in sorted(
            self.graph.drones.values(), key=lambda d: d.id
        ):
            if not drone.path:
                continue

            for i in range(1, len(drone.path)):
                turn, loc = drone.path[i]
                _, prev_loc = drone.path[i - 1]

                # Skip entries where drone stays in the same zone (waiting)
                if loc == prev_loc:
                    continue

                move_str = f"{drone.id}-{loc}"
                all_moves[turn].append(move_str)
                max_t = max(max_t, turn)

                # Stop tracking once the drone reaches the end zone
                if loc == self.graph.end_zone.name:
                    break

        for t in range(1, max_t + 1):
            if t in all_moves:
                print(" ".join(all_moves[t]))
