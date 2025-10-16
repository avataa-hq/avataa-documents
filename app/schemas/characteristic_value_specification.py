from pydantic import BaseModel, Field, AnyUrl, types

from schemas.load_field_description import field_description
from schemas.range_interval import RangeInterval
from schemas.time_period import TimePeriod

fd = field_description["CharacteristicValueSpecification"]


class CharacteristicValueSpecification(BaseModel):
    """
    Specification of a value (number or text or an object) that can be assigned to a Characteristic.
    """

    base_type: str | None = Field(
        default=None, alias="@baseType", description=fd["@baseType"]
    )
    schema_location: AnyUrl | None = Field(
        default=None, alias="@schemaLocation", description=fd["@schemaLocation"]
    )
    type: str | None = Field(
        default=None, alias="@type", description=fd["@type"]
    )
    is_default: bool | None = Field(
        default=None, alias="isDefault", description=fd["isDefault"]
    )
    range_interval: RangeInterval | None = Field(
        default=None, alias="rangeInterval", description=fd["rangeInterval"]
    )
    regex: str | None = Field(default=None, description=fd["regex"])
    unit_of_measure: str | None = Field(
        default=None, alias="unitOfMeasure", description=fd["unitOfMeasure"]
    )
    valid_for: TimePeriod | None = Field(
        default=None, alias="validFor", description=fd["validFor"]
    )
    value: types.Any | None = Field(default=None, description=fd["value"])
    value_from: int | None = Field(
        default=None, alias="valueFrom", description=fd["valueFrom"]
    )
    value_to: int | None = Field(
        default=None, alias="valueTo", description=fd["valueTo"]
    )
    value_type: str | None = Field(
        default=None, alias="valueType", description=fd["valueType"]
    )
