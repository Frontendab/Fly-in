from .Zone import Zone
from typing import Optional
from pydantic import (
    BaseModel, Field, ConfigDict
)


class ValidateConnection(BaseModel):
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
    def __init__(
        self, zone_a: Zone, zone_b: Zone,
        max_link_capacity: Optional[int] = 0,
        current_flow: Optional[int] = 0
    ) -> None:
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max_link_capacity: int | None = max_link_capacity
        self.current_flow: int = 0

    def initialize_connect(self) -> None:
        self.zone_a.target_zone.append(self.zone_b)
