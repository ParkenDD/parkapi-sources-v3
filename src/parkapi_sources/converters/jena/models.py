"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum

from shapely import GeometryType, Point
from validataclass.dataclasses import validataclass
from validataclass.validators import AnythingValidator, DataclassValidator, IntegerValidator, StringValidator

from parkapi_sources.models import GeojsonBaseFeatureInput, ParkingSiteRestrictionInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingAudience, ParkingSiteType, PurposeType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator


class JenaArt(Enum):
    PARKPLATZ = 'Parkplatz'
    PARKHAUS = 'Parkhaus'
    ROLLSTUHLFAHRERPARKPLATZ = 'Rollstuhlfahrerparkplatz (Anzahl Stellplätze)'
    BUSPARKPLATZ = 'Busparkplatz'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.PARKPLATZ: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.PARKHAUS: ParkingSiteType.CAR_PARK,
            self.ROLLSTUHLFAHRERPARKPLATZ: ParkingSiteType.ON_STREET,
            self.BUSPARKPLATZ: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }[self]

    def to_restriction(self) -> ParkingSiteRestrictionInput | None:
        return {
            self.ROLLSTUHLFAHRERPARKPLATZ: ParkingSiteRestrictionInput(type=ParkingAudience.DISABLED),
            self.BUSPARKPLATZ: ParkingSiteRestrictionInput(type=ParkingAudience.BUS),
        }.get(self)


@validataclass
class JenaPropertiesInput:
    id: int = IntegerValidator()
    gid: int = IntegerValidator()
    name: str = StringValidator()
    art: str = StringValidator()
    the_geom: dict = AnythingValidator(allowed_types=[dict])


@validataclass
class JenaFeatureInput(GeojsonBaseFeatureInput):
    properties: JenaPropertiesInput = DataclassValidator(JenaPropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        art = JenaArt(self.properties.art)
        restrictions: list[ParkingSiteRestrictionInput] = []
        restriction = art.to_restriction()
        if restriction is not None:
            restrictions.append(restriction)

        return StaticParkingSiteInput(
            uid=str(self.properties.id),
            name=self.properties.name,
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            type=art.to_parking_site_type(),
            capacity=0,
            restrictions=restrictions,
            purpose=PurposeType.CAR,
            has_realtime_data=False,
            static_data_updated_at=datetime.now(tz=timezone.utc),
        )
