"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from datetime import datetime, timezone
from decimal import Decimal

import shapely
from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, IntegerValidator, StringValidator

from parkapi_sources.models import (
    GeojsonBaseFeatureInput,
    GeojsonFeatureGeometryPolygonInput,
    ParkingRestrictionInput,
    StaticParkingSpotInput,
)
from parkapi_sources.models.enums import ParkingAudience, PurposeType
from parkapi_sources.models.parking_spot_inputs import GeojsonPolygonInput
from parkapi_sources.util import round_7d


@validataclass
class FreiburgDisabledSensorsPropertiesInput:
    fid: int = IntegerValidator(allow_strings=True)
    strasse: str = StringValidator()
    hausnummer: str = StringValidator()
    hinweis: str = StringValidator()


@validataclass
class FreiburgDisabledStaticFeatureInput(GeojsonBaseFeatureInput):
    properties: FreiburgDisabledSensorsPropertiesInput = DataclassValidator(FreiburgDisabledSensorsPropertiesInput)
    geometry: GeojsonFeatureGeometryPolygonInput = DataclassValidator(GeojsonFeatureGeometryPolygonInput)

    def to_static_parking_spot_input(self) -> StaticParkingSpotInput:
        address = self.properties.strasse
        if self.properties.hausnummer:
            address += f' {self.properties.hausnummer}'
        address += ', Freiburg im Breisgau'

        geojson = GeojsonPolygonInput(
            type='Polygon',
            coordinates=self.geometry.coordinates,
        )

        polygon = shapely.from_geojson(json.dumps(self.geometry.to_dict()))
        point = shapely.centroid(polygon)

        return StaticParkingSpotInput(
            uid=str(self.properties.fid),
            address=address,
            description=None if self.properties.hinweis == '' else self.properties.hinweis,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            lat=round_7d(Decimal(point.y)),
            lon=round_7d(Decimal(point.x)),
            has_realtime_data=False,
            geojson=geojson,
            restricted_to=[ParkingRestrictionInput(type=ParkingAudience.DISABLED)],
            purpose=PurposeType.CAR,
        )
