from typing import Union, Dict, List, Tuple, Any
from pydantic import (
    BaseModel, Field, ConfigDict, field_validator,
    model_validator
)
from pydantic_core import PydanticCustomError
from enum import Enum
from abc import ABC, abstractmethod
from sys import exit, stderr

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from pygame.colordict import THECOLORS # noqa


class ZoneTypes(Enum):
    """
    Enumeration of possible zone types in the system.

    Defines the behavior and cost of different zone types for pathfinding.
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class ValidateZone(BaseModel):
    """
    Pydantic model for validating zone data.

    Ensures that zone parameters are properly validated,
    including name, coordinates, type, color, and capacity.
    """
    name: str = Field(
        min_length=1, description="Name of the zone"
    )
    x: int = Field(
        description="X of zone's coordinate"
    )
    y: int = Field(
        description="Y of zone's coordinate"
    )
    zone_type: ZoneTypes = Field(
        ZoneTypes.NORMAL,
        description="Type of the zone, default normal"
    )
    color: Union[str, tuple, None] = Field(
        None, min_length=3, description="Color of the zone"
    )
    max_drones: int = Field(
        1, ge=1,
        description="Maximum drones that can occupy this zone simultaneously"
    )

    @field_validator('color', mode="after")
    @classmethod
    def initialize_color(cls, color: str | tuple) -> object:
        """
        Validate and convert color field to RGB tuple.

        Args:
            color (str): Color name or RGB tuple.

        Returns:
            tuple | None: RGB tuple if valid color, None otherwise.

        Raises:
            PydanticCustomError: If color name is invalid.
        """
        if isinstance(color, tuple):
            return color

        color_tuple: tuple | str | None = color
        if color:
            color_tuple = THECOLORS.get(color.lower())
            if not color_tuple and color != "rainbow":
                raise PydanticCustomError(
                    "invalid_color",
                    (
                        "Invalid color name. " +
                        "See: https://www.pygame.org/docs/ref/color_list.html"
                    )
                )
        return color_tuple


class Zone:
    """
    Represents a zone in the Fly-in navigation graph.

    A zone has coordinates, type, capacity, and pathfinding attributes
    like cost, heuristic, and parent for A* algorithm.
    """

    def __init__(
        self, name: str, x: int, y: int,
        zone_type: ZoneTypes = ZoneTypes.NORMAL,
        max_drones: int = 1, color: str | tuple | None = None,
    ) -> None:
        """
        Initialize a Zone instance with validation.

        Args:
            name (str): Name of the zone.
            x (int): X-coordinate.
            y (int): Y-coordinate.
            zone_type (Optional[ZoneTypes]): Type of zone. Defaults to NORMAL.
            max_drones (Optional[int]): Maximum drones allowed. Defaults to 1.
            color (Optional[str]): Color name. Defaults to None.
            current_drones (Optional[int]): Current drone count. Defaults to 0.
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: ZoneTypes = zone_type
        self.max_drones: int = max_drones
        self.color: str | tuple | None = color
        self.color_name: str | tuple | None = color
        self.target_zone: List[Zone] = []
        self.target_zone_from_end: List[Zone] = []
        self.contain_zones: int = 0
        self.g: int = self.get_cost(self.zone_type)
        self.h: float = float("inf")
        self.f: float = float("inf")

    def get_cost(self, zone_type: ZoneTypes) -> int:
        """
        Get the movement cost for a given zone type.

        Args:
            zone_type (ZoneTypes): The type of zone.

        Returns:
            int: The cost value (1 for normal/priority, 2 for restricted,
                0 for blocked).
        """
        cost_zones = {
            ZoneTypes.NORMAL: 1,
            ZoneTypes.RESTRICTED: 2,
            ZoneTypes.PRIORITY: 1,
            ZoneTypes.BLOCKED: 0,
        }
        return cost_zones.get(zone_type, 0)


class ValidateConnection(BaseModel):
    """
    Pydantic model for validating connection data between two zones.

    This model ensures that connection parameters are properly validated,
    including zone references and maximum link capacity.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    zone_a: Zone = Field(
        description="First zone to connect it with the second"
    )
    zone_b: Zone = Field(
        description="Second zone to connect it with the first"
    )
    max_link_capacity: int = Field(
        1, ge=1,
        description="Maximum drones that can traverse this \
            connection simultaneously"
    )


class Connection:
    """
    Represents a connection between two zones in the system.

    A connection defines a link between zone_a and zone_b with a maximum
    capacity for drones and tracks the current flow of drones through it.
    """

    def __init__(
        self, zone_a: Zone, zone_b: Zone,
        max_link_capacity: int = 1,
    ) -> None:
        """
        Initialize a Connection instance.

        Args:
            zone_a (Zone): The first zone in the connection.
            zone_b (Zone): The second zone in the connection.
            max_link_capacity (Optional[int]): Maximum number of drones
                that can traverse this connection simultaneously.
                Defaults to 0.
        """
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max_link_capacity: int = max_link_capacity

    def initialize_connect(self) -> None:
        """
        Initialize the connection by adding zone_b to zone_a's target zones.

        This method sets up the directional link from zone_a to zone_b,
        allowing navigation in that direction.
        """
        self.zone_b.target_zone_from_end.append(self.zone_a)
        self.zone_a.target_zone.append(self.zone_b)


class ValidateDrone(BaseModel):
    """
    Pydantic model for validating drone data.

    This model ensures that drone parameters are properly validated,
    including ID format, current zone, and target zones.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(
        description="ID of the drone"
    )
    current_zone: Zone = Field(
        description="Current zone of the drone"
    )
    target_zone: List[Zone] = Field(
        description="Target zone of the drone"
    )

    @model_validator(mode="after")
    def check_valid_id(self) -> Any:
        """
        Validate that the drone ID starts with 'D'.

        Raises:
            PydanticCustomError: If the ID does not start with 'D'.
        """
        if not self.id.startswith("D"):
            raise PydanticCustomError(
                "invalid_id",
                (
                    "Invalid ID's drone. " +
                    "ID must start with 'D'."
                )
            )

        return self


class Drone:
    """
    Represents a drone in the Fly-in system.

    A drone has an ID, current position in a zone, target zone,
    and tracks its path and movement.
    """

    def __init__(
        self, id: str, current_zone: Zone, target_zone: List[Zone]
    ) -> None:
        """
        Initialize a Drone instance.

        Args:
            id (str): Unique identifier for the drone.
            current_zone (Zone): The zone where the drone is currently located.
            target_zone (Zone): The target zone the drone is heading to.
        """
        self.id: str = id
        self.current_zone: Zone = current_zone
        self.target_zone: List[Zone] = target_zone
        self.current_x: float = current_zone.x
        self.current_y: float = current_zone.y
        self.target_index = 0
        self.path: List[Tuple[int, str]] = [(0, current_zone.name)]
        self.finished: bool = False


class Graph:
    """
    Represents the graph structure of the Fly-in system.

    The graph contains zones, connections between zones, and drones,
    along with start and end zones for pathfinding.
    """

    def __init__(self) -> None:
        """
        Initialize a Graph instance.

        Sets up empty dictionaries for zones, connections, and drones,
        and initializes start and end zones.
        """
        self.zones: Dict[str, Zone] = {}
        self.connections: Dict[str, Connection] = {}
        self.start_zone: Zone = Zone(name="placeholder", x=0, y=0)
        self.end_zone: Zone = Zone(name="placeholder", x=0, y=0)
        self.drones: Dict[str, Drone] = {}

    def get_zone(self, zone_name: str) -> Zone | None:
        """
        Retrieve a zone by name.

        Checks regular zones first, then start and end zones.

        Args:
            zone_name (str): The name of the zone to retrieve.

        Returns:
            Zone: The zone object if found, None otherwise.
        """
        take_zone = self.zones.get(zone_name, None)
        if not take_zone:
            if self.start_zone.name == zone_name:
                take_zone = self.start_zone
            elif self.end_zone.name == zone_name:
                take_zone = self.end_zone
        return take_zone

    def get_connection(self, connection_name: str) -> Connection | None:
        """
        Retrieve a connection by name.

        Args:
            connection_name (str): The name of the connection to retrieve.

        Returns:
            Connection: The connection object if found, None otherwise.
        """
        return self.connections.get(connection_name, None)

    def get_drone(self, id: str) -> Drone | None:
        """
        Retrieve a drone by ID.

        Args:
            id (str): The ID of the drone to retrieve.

        Returns:
            Drone: The drone object if found, None otherwise.
        """
        return self.drones.get(id, None)

    def create_zone(
        self, name: str, x: int, y: int,
        zone_type: ZoneTypes = ZoneTypes.NORMAL,
        max_drones: int = 1, color: str | tuple | None = None,
    ) -> Zone:
        """
        Create a new zone with validation.

        Args:
            name (str): Name of the zone.
            x (int): X-coordinate of the zone.
            y (int): Y-coordinate of the zone.
            zone_type (Optional[ZoneTypes]): Type of the zone.
                Defaults to NORMAL.
            max_drones (Optional[int]): Maximum number of drones allowed.
                Defaults to 1.
            color (Optional[str]): Color for visualization. Defaults to "".

        Returns:
            Zone: The created Zone object.
        """
        valid_zone = ValidateZone(
            name=name, x=x, y=y, zone_type=zone_type, max_drones=max_drones,
            color=color
        )
        zone = Zone(
            valid_zone.name, valid_zone.x, valid_zone.y, valid_zone.zone_type,
            valid_zone.max_drones, valid_zone.color,
        )
        zone.color_name = color
        return zone

    def create_connection(
        self, zone_a: Zone, zone_b: Zone, max_link_capacity: int = 1,
    ) -> Connection:
        """
        Create a new connection between two zones with validation.

        Args:
            zone_a (Zone): The first zone in the connection.
            zone_b (Zone): The second zone in the connection.
            max_link_capacity (Optional[int]): Maximum capacity of
                the connection. Defaults to 1.

        Returns:
            Connection: The created Connection object.
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
        """
        Create a new drone with validation.

        Args:
            id (int): Numeric ID for the drone (will be prefixed with 'D').
            current_zone (Zone): The current zone of the drone.
            target_zone (List[Zone]): List of target zones for the drone.

        Returns:
            Drone: The created Drone object.
        """
        valid_drone = ValidateDrone(
            id=f"D{id}", current_zone=current_zone,
            target_zone=target_zone
        )
        drone = Drone(
            valid_drone.id, valid_drone.current_zone,
            valid_drone.target_zone
        )
        return drone


class Error(ABC):
    """
    Abstract base class for error handling.

    This class provides a template for formatting and displaying errors.
    Subclasses must implement the format_errors and display_errors methods.
    """

    def __init__(self, errors: list) -> None:
        """
        Initialize an Error instance.

        Args:
            errors (list): List of error data to be processed.
        """
        self.errors: list = errors

    @abstractmethod
    def format_errors(self) -> List[Dict[str, Any]]:
        """
        Format the errors into a standardized structure.

        Returns:
            List[Dict[str, Any]]: List of formatted error dictionaries.
        """
        pass

    @abstractmethod
    def display_errors(self, errors: List[Dict[str, Any]]) -> None:
        """
        Display the formatted errors to the user.

        Args:
            errors (List[Dict[str, Any]]): List of formatted
                error dictionaries.
        """
        pass


class PydanticError(Error):
    """
    Concrete implementation for handling Pydantic validation errors.

    This class formats and displays errors from Pydantic model validation.
    """

    def format_errors(self) -> List[Dict[str, Any]]:
        """
        Format Pydantic validation errors into a standardized structure.

        Extracts message, field, and input from each error
        and cleans up the message.

        Returns:
            List[Dict[str, Any]]: List of formatted error dictionaries
                with keys 'msg', 'field', 'input'.
        """
        response: List[Dict[str, Any]] = []
        for error in self.errors:

            msg = error.get('msg', 'Empty!')
            type = error.get('type', 'Empty!')
            field = error.get('loc', 'Empty!')
            user_input = (
                error.get('input', "Empty!")
                if error.get('input', "Empty!") else "Empty!"
            )
            if "Value error," in msg:
                msg = msg.split("Value error,")[1].strip()

            response.append({
                "type": type,
                "msg": msg,
                "field": field,
                "input": user_input,
            })
        return response

    def display_errors(self, errors: List[Dict[str, Any]]) -> None:
        """
        Display the formatted Pydantic errors and exit the program.

        Prints each error with field, input, and message,
        then exits with code 1.

        Args:
            errors (List[Dict[str, Any]]): List of formatted
                error dictionaries.
        """
        for error in errors:
            if error.get("type") == "invalid_id":
                print(f"[ERROR]: {error.get('msg')}", file=stderr)
            else:
                print(
                    f"Field: {error.get('field')}, input: " +
                    f"{error.get('input')}" +
                    f",  error: {error.get('msg')}", file=stderr
                )
        exit(1)
