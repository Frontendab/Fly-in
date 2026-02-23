from .Zone import Zone, ZoneTypes, ValidateZone
from .Connection import Connection, ValidateConnection
from typing import Dict, List, Optional


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, List[Connection]] = {}
        self.start_zone: Zone = {}
        self.end_zone: Zone = {}

    def get_zone(self, zone_name: str) -> Zone:
        take_zone = self.zones.get(zone_name, None)
        if not take_zone:
            if self.start_zone.name == zone_name:
                take_zone = self.start_zone
            elif self.end_zone.name == zone_name:
                take_zone = self.end_zone
        return take_zone

    def get_connection(self, connection_name: str) -> List[Connection]:
        return self.connections.get(connection_name, None)

    def create_zone(
        self, name: str, x: int, y: int,
        zone_type: Optional[ZoneTypes] = ZoneTypes.NORMAL,
        max_drones: Optional[int] = 1, color: Optional[str] = "",
        current_drones: Optional[int] = 0
    ) -> Zone:
        valid_zone = ValidateZone(
            name=name, x=x, y=y, zone_type=zone_type, max_drones=max_drones,
            color=color, current_drones=current_drones
        )
        zone = Zone(
            valid_zone.name, valid_zone.x, valid_zone.y, valid_zone.zone_type,
            valid_zone.max_drones, valid_zone.color,
            valid_zone.current_drones
        )
        return zone

    def create_connection(
        self, zone_a: Zone, zone_b: Zone, max_link_capacity: Optional[int] = 1,
    ) -> Connection:
        valid_connection = ValidateConnection(
            zone_a=zone_a, zone_b=zone_b, max_link_capacity=max_link_capacity,
        )
        connection = Connection(
            valid_connection.zone_a, valid_connection.zone_b,
            valid_connection.max_link_capacity
        )
        return connection
