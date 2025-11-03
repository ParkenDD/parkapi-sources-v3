"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Optional

from shapely import GeometryType, Point
from validataclass.dataclasses import validataclass
from validataclass.validators import (
    DataclassValidator,
    FloatValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import ParkingSiteRestrictionInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingAudience, ParkingSiteType, PurposeType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator, MappedBooleanValidator


@validataclass
class FreiburgVAGBikePropertiesInput:
    fid: int = IntegerValidator(allow_strings=True)
    original_uid: int = IntegerValidator(allow_strings=True)
    name: str = StringValidator()
    purpose: str = StringValidator()
    type: str = StringValidator()
    operator_name: Optional[str] = Noneable(StringValidator())
    lon: float = FloatValidator()
    lat: float = FloatValidator()
    capacity: int = IntegerValidator(min_value=0, allow_strings=True)
    capacity_charging: Optional[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True))
    capacity_cargobike: Optional[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True))
    max_heighth: Optional[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True))
    max_width: Optional[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True))
    is_covered: Optional[bool] = Noneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False}))
    related_location: Optional[str] = Noneable(StringValidator())
    has_realtime_data: Optional[bool] = Noneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False}))
    has_fee: Optional[bool] = Noneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False}))
    fee_description: Optional[str] = Noneable(StringValidator())
    durchg_geoeffnet: Optional[bool] = Noneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False}))
    public_url: Optional[str] = Noneable(UrlValidator())

    def to_static_parking_site_input(self, geometry: Point) -> StaticParkingSiteInput:
        parking_site_restrictions: list[ParkingSiteRestrictionInput] = []
        if self.capacity_charging is not None:
            parking_site_restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                    capacity=self.capacity_charging,
                ),
            )

        return StaticParkingSiteInput(
            uid=str(self.original_uid),
            lat=round_7d(geometry.y),
            lon=round_7d(geometry.x),
            name=self.name,
            operator_name=self.operator_name,
            capacity=self.capacity,
            type=ParkingSiteType.LOCKERS,
            purpose=PurposeType.BIKE if self.purpose.lower() == 'bike' else PurposeType.ITEM,
            related_location=self.related_location,
            public_url=self.public_url,
            max_height=self.max_heighth,
            max_width=self.max_width,
            is_covered=self.is_covered,
            has_fee=self.has_fee,
            fee_description=self.fee_description,
            restrictions=parking_site_restrictions,
            has_realtime_data=self.has_realtime_data if self.has_realtime_data is not None else False,
            opening_hours='24/7' if self.durchg_geoeffnet else None,
            static_data_updated_at=datetime.now(tz=timezone.utc),
        )


@validataclass
class FreiburgVAGBikeFeatureInput:
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])
    properties: FreiburgVAGBikePropertiesInput = DataclassValidator(FreiburgVAGBikePropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        return self.properties.to_static_parking_site_input(self.geometry)
