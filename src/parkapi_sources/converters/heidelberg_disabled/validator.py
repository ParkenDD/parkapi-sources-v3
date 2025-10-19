"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from datetime import datetime

from shapely import GeometryType, Point
from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnyOfValidator,
    DataclassValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import ParkingSpotRestrictionInput, StaticParkingSpotInput
from parkapi_sources.models.enums import ParkingAudience, ParkingSpotType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator


@validataclass
class HeidelbergDisabledPropertiesInput:
    BEZEICHNUN: str = StringValidator()
    BETREIBER: str | None = Noneable(StringValidator())
    BESCHREIBU: str | None = Noneable(StringValidator())
    BESCHRIFTU: str | None = Noneable(StringValidator())
    Notiz: str | None = Noneable(StringValidator()), Default(None)


@validataclass
class HeidelbergDisabledParkingSpotInput:
    id: str = StringValidator()
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: HeidelbergDisabledPropertiesInput = DataclassValidator(HeidelbergDisabledPropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])

    def to_static_parking_site(self, static_data_updated_at: datetime) -> StaticParkingSpotInput | None:
        # If Baustelle is in Notiz, the spot is not available
        if self.properties.Notiz and 'Baustelle' in self.properties.Notiz:
            return None

        # Remove texts in brackets from name to get the address
        address = re.sub(r'\(.*?\)', '', self.properties.BEZEICHNUN).strip()

        descriptions: list[str] = [
            self.properties.BESCHREIBU,
            self.properties.BESCHRIFTU,
            self.properties.Notiz,
        ]

        return StaticParkingSpotInput(
            uid=self.id,
            name=self.properties.BESCHRIFTU or None,
            operator_name=self.properties.BETREIBER,
            address=f'{address}, Heidelberg' if address else None,
            static_data_updated_at=static_data_updated_at,
            type=ParkingSpotType.ON_STREET,
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            description=', '.join(description for description in descriptions if description) or None,
            has_realtime_data=False,
            restrictions=[ParkingSpotRestrictionInput(type=ParkingAudience.DISABLED)],
        )
