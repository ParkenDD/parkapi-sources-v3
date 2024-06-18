"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.validators import (
    AnyOfValidator,
    AnythingValidator,
    BooleanValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType


@validataclass
class GeojsonFeaturePropertiesInput(ValidataclassMixin):
    uid: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(min_length=1, max_length=256)
    type: Optional[ParkingSiteType] = EnumValidator(ParkingSiteType), Default(None)
    public_url: Optional[str] = UrlValidator(max_length=4096), Default(None)
    address: str = StringValidator(max_length=512)
    description: Optional[str] = StringValidator(max_length=512), Default(None)
    capacity: int = IntegerValidator()
    has_realtime_data: bool = BooleanValidator()


@validataclass
class GeojsonFeatureGeometryInput:
    type: str = AnyOfValidator(allowed_values=['Point'])
    coordinates: list[Decimal] = ListValidator(NumericValidator(), min_length=2, max_length=2)


@validataclass
class GeojsonFeatureInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: GeojsonFeaturePropertiesInput = DataclassValidator(GeojsonFeaturePropertiesInput)
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)

    def to_static_parking_site_input(self, static_data_updated_at: datetime) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            static_data_updated_at=static_data_updated_at,
            **self.properties.to_dict(),
        )


@validataclass
class GeojsonInput:
    type: str = AnyOfValidator(allowed_values=['FeatureCollection'])
    features: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))
