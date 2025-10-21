"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

import shapely
from shapely import GeometryType
from shapely.geometry.polygon import Polygon
from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, IntegerValidator, StringValidator

from parkapi_sources.models import (
    GeojsonBaseFeatureInput,
    ParkingSpotRestrictionInput,
    StaticParkingSpotInput,
)
from parkapi_sources.models.enums import ParkingAudience, PurposeType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator


@validataclass
class FreiburgDisabledSensorsPropertiesInput:
    fid: int = IntegerValidator(allow_strings=True)
    strasse: str = StringValidator()
    hausnummer: str = StringValidator()
    hinweis: str = StringValidator()


@validataclass
class FreiburgDisabledStaticFeatureInput(GeojsonBaseFeatureInput):
    properties: FreiburgDisabledSensorsPropertiesInput = DataclassValidator(FreiburgDisabledSensorsPropertiesInput)
    geometry: Polygon = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POLYGON])

    def to_static_parking_spot_input(self) -> StaticParkingSpotInput:
        address = self.properties.strasse
        if self.properties.hausnummer:
            address += f' {self.properties.hausnummer}'
        address += ', Freiburg im Breisgau'

        point = shapely.centroid(self.geometry)

        return StaticParkingSpotInput(
            uid=str(self.properties.fid),
            address=address,
            description=None if self.properties.hinweis == '' else self.properties.hinweis,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            lat=round_7d(point.y),
            lon=round_7d(point.x),
            has_realtime_data=False,
            geojson=self.geometry,
            restrictions=[ParkingSpotRestrictionInput(type=ParkingAudience.DISABLED)],
            purpose=PurposeType.CAR,
        )
