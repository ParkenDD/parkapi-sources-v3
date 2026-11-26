"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum

from shapely import GeometryType, Point
from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, EnumValidator, IntegerValidator, Noneable, StringValidator

from parkapi_sources.models import (
    GeojsonBaseFeatureInput,
    ParkingAudience,
    ParkingSpotRestrictionInput,
    PurposeType,
    StaticParkingSpotInput,
)
from parkapi_sources.models.enums import ParkingOrientation, ParkingSpotType
from parkapi_sources.util.helper import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator


class KonstanzDisabledParkingSpotTypeInput(Enum):
    OFF_STREET_PARKING_GROUND = 'OFF_STREET_PARKING_GROUND'
    ON_STREET = 'ON_STREET'

    def to_parking_spot_type_input(self) -> ParkingSpotType | None:
        return {
            self.OFF_STREET_PARKING_GROUND: ParkingSpotType.OFF_STREET_PARKING_GROUND,
            self.ON_STREET: ParkingSpotType.ON_STREET,
        }.get(self)


class Orientierung(Enum):
    PARALLEL = 'längs'
    PERPENDICULAR = 'quer'
    DIAGONAL = 'schräg'

    def to_parking_site_orientation_type(self) -> ParkingOrientation | None:
        return {
            self.PARALLEL: ParkingOrientation.PARALLEL,
            self.PERPENDICULAR: ParkingOrientation.PERPENDICULAR,
            self.DIAGONAL: ParkingOrientation.DIAGONAL,
        }.get(self)


@validataclass
class KonstanzDisabledPropertiesInput:
    OBJECTID: int = IntegerValidator()
    Name: str = StringValidator()
    adress: str = StringValidator()
    Stadtteil: str = StringValidator()
    type: KonstanzDisabledParkingSpotTypeInput = EnumValidator(KonstanzDisabledParkingSpotTypeInput)
    Anordnung: Orientierung = EnumValidator(Orientierung)
    description: str | None = Noneable(StringValidator())
    GlobalID: str = StringValidator()


@validataclass
class KonstanzDisabledFeatureInput(GeojsonBaseFeatureInput):
    properties: KonstanzDisabledPropertiesInput = DataclassValidator(KonstanzDisabledPropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])

    def to_static_parking_spot_input(self) -> StaticParkingSpotInput:
        return StaticParkingSpotInput(
            uid=f'{self.properties.GlobalID}',
            name=f'{self.properties.Name} {self.properties.Stadtteil}',
            purpose=PurposeType.CAR,
            address=self.properties.adress,
            description=self.properties.description,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            has_realtime_data=False,
            restrictions=[ParkingSpotRestrictionInput(type=ParkingAudience.DISABLED)],
            type=self.properties.type.to_parking_spot_type_input(),
            orientation=self.properties.Anordnung.to_parking_site_orientation_type(),
        )
