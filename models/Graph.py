from .Zone import Zone, ZoneTypes, ValidateZone
from .Connection import Connection, ValidateConnection
from typing import Dict, List, Optional
from .Drone import ValidateDrone, Drone


class Graph:
    """Graph: It the class it management the zones
    """
    def __init__(self) -> None:
        """__init__ is use to assign values to the current instance
        """
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, Connection] = {}
        self.start_zone: Zone = Zone("Placeholder", 0, 0)
        self.end_zone: Zone = Zone("Placeholder", 0, 0)
        self.drones: Dict[str, Drone] = {}

    def get_zone(self, zone_name: str) -> Zone | None:
        """get_zone: Is return the zone if is it exit
            and check start/end zones if isn't exit in the hub's zones

        Args:
            zone_name (str): Name the zone you want get it

        Returns:
            Zone | None: Return zone if is it exit otherwise return None
        """
        take_zone: Zone | None = self.zones.get(zone_name)

        if self.start_zone.name == zone_name:
            return self.start_zone
        elif self.end_zone.name == zone_name:
            return self.end_zone

        return take_zone

    def get_connection(self, connection_name: str) -> Connection | None:
        """get_connection: Is return the connection if is it exit

        Args:
            connection_name (str): Name the connection you want get it

        Returns:
            Connection | None: Return connection if is it exit
                otherwise return None
        """
        return self.connections.get(connection_name, None)

    def get_drone(self, id: str) -> Drone | None:
        """get_drone: Is return the drone if is it exit

        Args:
            id (str): id of the drone you want get it

        Returns:
            Drone | None: Return drone if is it exit
                otherwise return None
        """
        return self.drones.get(id, None)

    def create_zone(
        self, name: str, x: int, y: int,
        zone_type: Optional[ZoneTypes] = ZoneTypes.NORMAL,
        max_drones: Optional[int] = 1, color: Optional[str] = "",
    ) -> Zone:
        """create_zone: We use it to create a zone after check
            they information is valid using the custom ValidateZone's class

        Args:
            name (str): Name of the zone
            x (int): the x is the coordinate the zone
            y (int): the y is the coordinate the zone
            zone_type (Optional[ZoneTypes], optional): Zone type of
                the ZoneTypes(Enum). Defaults to ZoneTypes.NORMAL.
            max_drones (Optional[int], optional): max of drones that
                the zone may carry at the same time. Defaults to 1.
            color (Optional[str], optional): The color of
                the current zone.Defaults to "".

        Returns:
            Zone: Return the current zone after pass all steps
                and is created successfully
        """
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
        """create_connection: We use it to create a connection
            between two zones after check they information is valid
            using the custom ValidateConnection's class

        Args:
            zone_a (Zone): the first zone connect with second
            zone_b (Zone): the second zone connect with first
            max_link_capacity (Optional[int], optional): max of drones that
                can go between connection it the same time. Defaults to 1.

        Returns:
            Connection: Return the current connection after pass all steps
                and is created successfully
        """
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
        """create_drone: We use it to create a drone
            after check they information is valid
            using the custom ValidateDrone's class

        Args:
            id (int): id of the current zone
            current_zone (Zone): initialize where is it exit!
            target_zone (List[Zone]): list of the target zones of
                the current zone it can visit them

        Returns:
            Drone: Return the current drone after pass all steps
                and is created successfully
        """
        valid_drone = ValidateDrone(
            id=f"D{id}", current_zone=current_zone,
            target_zone=target_zone, departure_turn=(id * 45)
        )
        drone = Drone(
            valid_drone.id, valid_drone.current_zone,
            valid_drone.target_zone, valid_drone.departure_turn
        )
        return drone
