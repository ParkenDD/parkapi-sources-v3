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
    Noneable,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from .enums import ParkAndRideType, ParkingSiteType
from .parking_restriction_inputs import ParkingRestrictionInput
from .parking_site_inputs import ExternalIdentifierInput, StaticParkingSiteInput
from .parking_spot_inputs import StaticParkingSpotInput


@validataclass
class GeojsonBaseFeaturePropertiesInput(ValidataclassMixin):
    def to_dict(self, *args, static_data_updated_at: datetime | None = None, **kwargs) -> dict:
        result = super().to_dict()

        if static_data_updated_at is not None:
            result['static_data_updated_at'] = static_data_updated_at

        return result


@validataclass
class GeojsonFeaturePropertiesInput(GeojsonBaseFeaturePropertiesInput):
    uid: str = StringValidator(min_length=1, max_length=256)
    name: Optional[str] = StringValidator(min_length=1, max_length=256), Default(None)
    type: Optional[ParkingSiteType] = EnumValidator(ParkingSiteType), Default(None)
    public_url: Optional[str] = UrlValidator(max_length=4096), Default(None)
    address: Optional[str] = StringValidator(max_length=512), Default(None)
    description: Optional[str] = StringValidator(max_length=512), Default(None)
    capacity: Optional[int] = IntegerValidator(), Default(None)
    has_realtime_data: Optional[bool] = BooleanValidator(), Default(None)
    max_height: Optional[int] = Noneable(IntegerValidator()), Default(None)
    max_width: Optional[int] = IntegerValidator(), Default(None)
    park_and_ride_type: Optional[list[ParkAndRideType]] = ListValidator(EnumValidator(ParkAndRideType)), Default(None)
    external_identifiers: Optional[list[ExternalIdentifierInput]] = (
        ListValidator(DataclassValidator(ExternalIdentifierInput)),
        Default(None),
    )


@validataclass
class GeojsonFeaturePropertiesParkingSpotInput(GeojsonBaseFeaturePropertiesInput):
    uid: str = StringValidator(min_length=1, max_length=256)
    name: Optional[str] = StringValidator(min_length=1, max_length=256), Default(None)
    restricted_to: Optional[list[ParkingRestrictionInput]] = (
        ListValidator(DataclassValidator(ParkingRestrictionInput)),
        Default(None),
    )
    has_realtime_data: Optional[bool] = BooleanValidator(), Default(None)


@validataclass
class GeojsonFeatureGeometryInput:
    type: str = AnyOfValidator(allowed_values=['Point'])
    coordinates: list[Decimal] = ListValidator(NumericValidator(), min_length=2, max_length=2)


@validataclass
class GeojsonBaseFeatureInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: GeojsonBaseFeaturePropertiesInput = DataclassValidator(GeojsonBaseFeaturePropertiesInput)
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)

    def to_static_parking_site_input(self, **kwargs) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            **self.properties.to_dict(**kwargs),
        )

    def to_static_parking_spot_input(self, **kwargs) -> StaticParkingSpotInput:
        return StaticParkingSpotInput(
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            **self.properties.to_dict(**kwargs),
        )

    def update_static_parking_site_input(self, static_parking_site: StaticParkingSiteInput) -> None:
        static_parking_site.lat = self.geometry.coordinates[1]
        static_parking_site.lon = self.geometry.coordinates[0]

        for key, value in self.properties.to_dict().items():
            if value is not None:
                setattr(static_parking_site, key, value)


@validataclass
class GeojsonFeatureInput(GeojsonBaseFeatureInput):
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: GeojsonFeaturePropertiesInput = DataclassValidator(GeojsonFeaturePropertiesInput)
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)


@validataclass
class GeojsonFeatureParkingSpotInput(GeojsonBaseFeatureInput):
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: GeojsonFeaturePropertiesParkingSpotInput = DataclassValidator(GeojsonFeaturePropertiesParkingSpotInput)
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)


@validataclass
class GeojsonInput:
    type: str = AnyOfValidator(allowed_values=['FeatureCollection'])
    features: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))
