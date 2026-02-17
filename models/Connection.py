from pydantic import BaseModel, Field
from . import Zone


class ValidateConnection(BaseModel):
    zone_a: Zone = Field(
        description="First zone to connect it with the second"
    ),
    zone_b: Zone = Field(
        description="Second zone to connect it with the first"
    ),
    max_link_capacity: int = Field(
        ge=0,
        description="Maximum drones that can traverse this \
            connection simultaneously"
    ),
    current_flow: int = Field(
        ge=0, description="To track the flow drones"
    )


class Connection:
    def __init__(
        self, zone_a: Zone, zone_b: Zone, max_link_capacity: int,
        current_flow: int
    ) -> None:
        valid_connection = ValidateConnection(
            zone_a, zone_b, max_link_capacity,
            current_flow
        )
        self.zone_a: Zone = valid_connection.zone_a
        self.zone_b: Zone = valid_connection.zone_b
        self.max_link_capacity: int = valid_connection.max_link_capacity
        self.current_flow: int = valid_connection.current_flow
