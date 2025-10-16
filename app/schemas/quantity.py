from pydantic import BaseModel, Field

from schemas.load_field_description import field_description

fd = field_description["Quantity"]


class Quantity(BaseModel):
    """
    An amount in a given unit.
    """

    amount: float = Field(description=fd["amount"])
    units: str = Field(description=fd["units"])
