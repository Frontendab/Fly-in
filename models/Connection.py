from .Zone import Zone
from pydantic import BaseModel, Field, ConfigDict


class ValidateConnection(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    zone_a: Zone = Field(
        description="First zone to connect it with the second"
    )
    zone_b: Zone = Field(
        description="Second zone to connect it with the first"
    )
    max_link_capacity: int = Field(
        ge=0,
        description="Maximum drones that can traverse this \
            connection simultaneously"
    )
    current_flow: int = Field(
        0, ge=0, description="To track the flow drones"
    )


class Connection:
    def __init__(
        self, zone_a: Zone, zone_b: Zone, max_link_capacity: int,
        current_flow: int
    ) -> None:
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max_link_capacity: int = max_link_capacity
        self.current_flow: int = current_flow
