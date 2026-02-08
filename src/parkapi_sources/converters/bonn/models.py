"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum

from shapely import GeometryType, Point
from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, IntegerValidator, Noneable, StringValidator

from parkapi_sources.models import GeojsonBaseFeatureInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator, ReplacingStringValidator


class BonnArt(Enum):
    AUTOPARKPLATZ = 1
    BUSPARKPLATZ = 2
    MOTORRADPARKPLATZ = 3
    WOHNMOBIL = 4

    def to_parking_site_type(self) -> ParkingSiteType:
        return ParkingSiteType.OFF_STREET_PARKING_GROUND


@validataclass
class BonnPropertiesInput:
    parkplatz_id: int = IntegerValidator()
    bezeichnung: str | None = Noneable(ReplacingStringValidator(mapping={'\n': ' ', '\r': ''}))
    art: BonnArt = IntegerValidator()
    inhalt: str = StringValidator()

    def __post_init__(self):
        self.art = BonnArt(self.art)


@validataclass
class BonnFeatureInput(GeojsonBaseFeatureInput):
    properties: BonnPropertiesInput = DataclassValidator(BonnPropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.properties.parkplatz_id),
            name=self.properties.bezeichnung or self.properties.inhalt,
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            type=self.properties.art.to_parking_site_type(),
            capacity=0,
            description=self.properties.inhalt,
            purpose=PurposeType.CAR,
            has_realtime_data=False,
            static_data_updated_at=datetime.now(tz=timezone.utc),
        )
