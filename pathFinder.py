"""
    PathFinder module for drone navigation.
"""

from typing import List, Tuple, Dict, cast
from classes import Zone, ZoneTypes, Graph, Drone
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
        self.shortest_dist: Dict[str, float] = self.__precompute_distances()
        # turn -> {'zones': {name: (current, max)},
        # 'connections': {name: (current, max)}}
        self.tracking: Dict[int, Dict[str, Dict[str, Tuple[int, int]]]] = {}

    def __precompute_distances(self) -> Dict[str, float]:
        dist: Dict[str, float] = {
            z.name: float("inf") for z in self.graph.zones.values()
        }
        dist[
            self.graph.start_zone.name
        ] = float("inf")
        dist[
            self.graph.end_zone.name
        ] = 0.0

        counter = 0
        open_list: List[Tuple[
            float, int, Zone
        ]] = [
            (0, counter, self.graph.end_zone)
        ]

        while open_list:
            item = self.pop_min(open_list)
            distance, _, zone = item

            if zone == self.graph.start_zone:
                break

            for neighbor in zone.target_zone_from_end:
                if neighbor.zone_type == ZoneTypes.BLOCKED:
                    continue

                new_distance = float(distance + zone.g)
                if neighbor.zone_type == ZoneTypes.PRIORITY:
                    new_distance -= 0.5
                
                if new_distance < dist[neighbor.name]:
                    dist[neighbor.name] = new_distance
                    counter += 1
                    open_list.append((
                        new_distance, counter, neighbor
                    ))

        return dist

    def a_star_search(self) -> None:
        drones = self.graph.drones.values()
        turn = 0

        in_transit: Dict[str, Tuple[Zone, int, str]] = {}

        while not all(drone.finished for drone in drones):
            turn += 1

            edge: Tuple[str, str] = ()
            edge_usage: Dict[Tuple[str, str,], int] = defaultdict(int)
            moves: List[Tuple[Drone, Zone, bool, str]] = []

            c_zone_counts: Dict[str, int] = defaultdict(int)
            for drone in drones:
                if drone.finished or drone.id in in_transit:
                    continue
                c_zone_counts[drone.current_zone.name] += 1

            n_zone_counts: Dict[str, int] = defaultdict(
                int, c_zone_counts
            )

            for drone in drones:
                if drone.finished:
                    moves.append((drone, drone.current_zone, False, None))
                    continue

                if drone.id in in_transit:
                    dest, turn_left, conn_name = in_transit[drone.id]
                    turn_left -= 1

                    edge = tuple(
                        conn_name.split("-")
                    )
                    edge_usage[edge] += 1

                    if turn_left == 0:
                        n_zone_counts[dest.name] += 1
                        del in_transit[drone.id]
                        moves.append((drone, dest, False, conn_name))
                    else:
                        in_transit[drone.id] = (
                            dest, turn_left, conn_name
                        )
                        moves.append((drone, None, True, conn_name))

                    continue

                current = drone.current_zone
                best_distance = float("inf")
                best_neighbor = None
                best_edge = ()

                for neighbor in current.target_zone:
                    if neighbor.zone_type == ZoneTypes.BLOCKED:
                        continue

                    edge = (current.name, neighbor.name)

                    connection = self.graph.get_connection(
                        f"{edge[0]}-{edge[1]}"
                    )

                    if edge_usage[edge] >= connection.max_link_capacity:
                        continue

                    if neighbor != self.graph.end_zone:
                        if n_zone_counts[neighbor.name] >= neighbor.max_drones:
                            continue
                    
                    distance = self.shortest_dist.get(
                        neighbor.name, float("inf")
                    )
                    if distance < best_distance:
                        best_distance = distance
                        best_neighbor = neighbor
                        best_edge = edge

                # Apply move
                if best_neighbor:
                    edge_usage[best_edge] += 1
                    n_zone_counts[best_neighbor.name] += 1

                    if current.name != best_neighbor.name:
                        n_zone_counts[current.name] -= 1

                    if best_neighbor.zone_type == ZoneTypes.RESTRICTED:
                        conn_name = f"{best_edge[0]}-{best_edge[1]}"
                        in_transit[drone.id] = (
                            best_neighbor, 1, conn_name
                        )
                        moves.append((drone, best_neighbor, True, conn_name))
                    else:
                        moves.append((drone, best_neighbor, False, None))
                else:
                    moves.append((drone, drone.current_zone, False, None))

            for drone, dest, is_transit, conn in moves:
                drone.current_zone = dest

                if is_transit and conn:
                    drone.path.append((turn, conn))
                elif dest:
                    drone.path.append((turn, dest.name))
                    if dest != self.graph.end_zone:
                        if not self.is_valid_path(dest):
                            raise ValueError("Invalid path")
                    else:
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
        valid = False
        distance = self.shortest_dist.get(
            current_zone.name, float("inf")
        )

        if distance == float("inf"):
            return False

        for neighbor in current_zone.target_zone:
            if neighbor.zone_type != ZoneTypes.BLOCKED:
                valid = True
        return valid

    def pop_min(
            self, open_list: List[
                Tuple[float, int, Zone]
            ]
        ) -> Tuple[
            float, int, Zone
        ]:
            item = min(open_list)
            open_list.remove(item)
            return item


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