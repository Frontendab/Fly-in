from .Zone import Zone, ZoneTypes
from .Connection import Connection
from typing import Dict, List, Optional


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, List[Connection]] = {}

    def get_zone(self, zone_name: str) -> Zone:
        return self.zones.get(zone_name, None)

    def get_connection(self, connection_name: str) -> List[Connection]:
        return self.connections.get(connection_name, None)

    def create_zone(
        self, name: str, x: int, y: int,
        zone_type: Optional[ZoneTypes] = ZoneTypes.NORMAL,
        max_drones: Optional[int] = 0, color: Optional[str] = "",
        current_drones: Optional[int] = 0
    ) -> Zone:
        zone = Zone(
            name, x, y, zone_type, max_drones, color,
            current_drones
        )
        self.zones[name] = zone
        return zone

    def create_connection(
        self, zone_a: Zone, zone_b: Zone, max_link_capacity: int,
        current_flow: Optional[int] = 0
    ) -> Connection:
        connection = Connection(
            zone_a, zone_b, max_link_capacity, current_flow
        )
        self.connections[f"{zone_a.name}-{zone_b.name}"].append(connection)
        return connection
