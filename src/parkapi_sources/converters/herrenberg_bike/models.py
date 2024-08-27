"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime, time, timezone
from enum import Enum
from typing import Optional

from validataclass.dataclasses import Default, DefaultUnset, validataclass
from validataclass.helpers import OptionalUnset, UnsetValue
from validataclass.validators import (
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    NoneToUnsetValue,
    StringValidator,
)

from parkapi_sources.converters.base_converter.pull import GeojsonFeatureGeometryInput
from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from parkapi_sources.validators import MappedBooleanValidator, ParsedDateValidator


class HerrenbergBikeType(Enum):
    STANDS = 'Bügel'
    LEANING_STANDS = 'Anlehnbügel'
    WALL_LOOPS = 'Reine Vorderradhalterung'
    STANGE = 'Stange'
    STAND_AND_WALL_LOOPS = 'Bügel + Vorderradhalterung'
    LOCKERS = 'Nische zum Abstellen'
    WOOD_CONSTRUCTION = 'Holzkonstruktion'
    LEAN_AND_STICK = 'lean_and_stick'
    LOCKBOX = 'Fahrradboxen'

    def to_parking_site_type(self) -> ParkingSiteType:
        if self in [HerrenbergBikeType.STANGE, HerrenbergBikeType.WOOD_CONSTRUCTION, HerrenbergBikeType.LEAN_AND_STICK]:
            return ParkingSiteType.OTHER
        if self == HerrenbergBikeType.STAND_AND_WALL_LOOPS:
            return ParkingSiteType.WALL_LOOPS
        if self == HerrenbergBikeType.LEANING_STANDS:
            return ParkingSiteType.STANDS
        return ParkingSiteType[self.name]


@validataclass
class HerrenbergBikePropertiesInput:
    id: int = IntegerValidator()
    location: str = StringValidator(min_length=0)
    count: int = IntegerValidator(min_value=0)
    count_chargers: int = IntegerValidator(min_value=0)
    has_lighting: Optional[bool] = Noneable(MappedBooleanValidator(mapping={'true': True, 'false': False})), Default(None)
    type: OptionalUnset[HerrenbergBikeType] = NoneToUnsetValue(EnumValidator(HerrenbergBikeType)), DefaultUnset
    access_type: Optional[str] = Noneable(StringValidator())
    date_survey: OptionalUnset[date] = NoneToUnsetValue(ParsedDateValidator(date_format='%Y-%m-%d')), DefaultUnset


@validataclass
class HerrenbergBikeFeatureInput:
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)
    properties: HerrenbergBikePropertiesInput = DataclassValidator(HerrenbergBikePropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.properties.id),
            name=self.properties.location if self.properties.location != '' else 'Fahrrad-Abstellanlagen',
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            capacity=self.properties.count,
            capacity_charging=self.properties.count_chargers,
            static_data_updated_at=datetime.now(timezone.utc)
            if self.properties.date_survey is UnsetValue
            else datetime.combine(self.properties.date_survey, time(), tzinfo=timezone.utc),
            type=ParkingSiteType.GENERIC_BIKE if self.properties.type is UnsetValue else self.properties.type.to_parking_site_type(),
            purpose=PurposeType.BIKE,
            has_lighting=self.properties.has_lighting,
        )
