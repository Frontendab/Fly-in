from .Zone import Zone
from typing import Optional
from pydantic import (
    BaseModel, Field, ConfigDict
)


class ValidateConnection(BaseModel):
    """ValidateConnection is class to check if
        the Connection information is valid or not with raise errors

    Args:
        BaseModel: It inherits from BaseModel's pydantic to be
            validator's class
    """

    # ? INFO: We use model_config to create
    # ? Custom type hint(in this case: Zone) with ValidateConnection's class
    model_config = ConfigDict(arbitrary_types_allowed=True)
    zone_a: Zone = Field(
        description="First zone to connect it with the second"
    )
    zone_b: Zone = Field(
        description="Second zone to connect it with the first"
    )
    max_link_capacity: Optional[int] = Field(
        1, ge=0,
        description="Maximum drones that can traverse this \
            connection simultaneously"
    )


class Connection:
    def __init__(
        self, zone_a: Zone, zone_b: Zone,
        max_link_capacity: Optional[int] = 1,
    ) -> None:
        """__init__ is use to assign values to the current instance

        Args:
            zone_a (Zone): is the first zone
            zone_b (Zone): is the second zone
            max_link_capacity (Optional[int], optional): max of drones that
                can go between connection it the same time. Defaults to 1.
        """
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max_link_capacity: int | None = max_link_capacity

    def initialize_connect(self) -> None:
        """initialize_connect is used to assign the zone_b
            as target of the zone_a to connect with each other
        """
        self.zone_a.target_zone.append(self.zone_b)
