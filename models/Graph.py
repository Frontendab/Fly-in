from .Zone import Zone, ZoneTypes, ValidateZone
from .Connection import Connection, ValidateConnection
from typing import Dict, List, Optional
from .Drone import ValidateDrone, Drone


class Graph:
    def __init__(self) -> None:
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, Connection] = {}
        self.start_zone: Zone = Zone("Placeholder", 0, 0)
        self.end_zone: Zone = Zone("Placeholder", 0, 0)
        self.drones: Dict[str, Drone] = {}

    def get_zone(self, zone_name: str) -> Zone | None:
        take_zone: Zone | None = self.zones.get(zone_name)

        if self.start_zone.name == zone_name:
            return self.start_zone
        elif self.end_zone.name == zone_name:
            return self.end_zone

        return take_zone

    def get_connection(self, connection_name: str) -> Connection | None:
        return self.connections.get(connection_name, None)

    def get_drone(self, id: str) -> Drone | None:
        return self.drones.get(id, None)

    def create_zone(
        self, name: str, x: int, y: int,
        zone_type: Optional[ZoneTypes] = ZoneTypes.NORMAL,
        max_drones: Optional[int] = 1, color: Optional[str] = "",
        current_drones: Optional[int] = 0
    ) -> Zone:
        valid_zone = ValidateZone(
            name=name, x=x, y=y, zone_type=zone_type, max_drones=max_drones,
            color=color
        )
        zone = Zone(
            valid_zone.name, valid_zone.x, valid_zone.y, valid_zone.zone_type,
            valid_zone.max_drones, valid_zone.color,
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

    def create_drone(
        self, id: int, current_zone: Zone, target_zone: List[Zone],
    ) -> Drone:
        valid_drone = ValidateDrone(
            id=f"D{id}", current_zone=current_zone,
            target_zone=target_zone, departure_turn=(id * 45)
        )
        drone = Drone(
            valid_drone.id, valid_drone.current_zone,
            valid_drone.target_zone, valid_drone.departure_turn
        )
        return drone
