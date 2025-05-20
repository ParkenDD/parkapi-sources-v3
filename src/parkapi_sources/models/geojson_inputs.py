"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.validators import (
    AnyOfValidator,
    AnythingValidator,
    BooleanValidator,
    DataclassValidator,
    EnumValidator,
    FloatValidator,
    IntegerValidator,
    ListValidator,
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
    name: str | None = StringValidator(min_length=1, max_length=256), Default(None)
    type: ParkingSiteType | None = EnumValidator(ParkingSiteType), Default(None)
    public_url: str | None = UrlValidator(max_length=4096), Default(None)
    address: str | None = StringValidator(max_length=512), Default(None)
    description: str | None = StringValidator(max_length=512), Default(None)
    capacity: int | None = IntegerValidator(), Default(None)
    has_realtime_data: bool | None = BooleanValidator(), Default(None)
    max_height: int | None = IntegerValidator(), Default(None)
    max_width: int | None = IntegerValidator(), Default(None)
    park_and_ride_type: list[ParkAndRideType] | None = ListValidator(EnumValidator(ParkAndRideType)), Default(None)
    external_identifiers: list[ExternalIdentifierInput] | None = (
        ListValidator(DataclassValidator(ExternalIdentifierInput)),
        Default(None),
    )


@validataclass
class GeojsonFeaturePropertiesParkingSpotInput(GeojsonBaseFeaturePropertiesInput):
    uid: str = StringValidator(min_length=1, max_length=256)
    name: str | None = StringValidator(min_length=1, max_length=256), Default(None)
    restricted_to: list[ParkingRestrictionInput] | None = (
        ListValidator(DataclassValidator(ParkingRestrictionInput)),
        Default(None),
    )
    has_realtime_data: bool | None = BooleanValidator(), Default(None)


@validataclass
class GeojsonFeatureGeometryPointInput:
    type: str = AnyOfValidator(allowed_values=['Point'])
    coordinates: list[Decimal] = ListValidator(NumericValidator(), min_length=2, max_length=2)


@validataclass
class GeojsonFeatureGeometryPolygonInput(ValidataclassMixin):
    type: str = AnyOfValidator(allowed_values=['Polygon'])
    coordinates: list[list[list[float]]] = ListValidator(
        ListValidator(
            ListValidator(
                FloatValidator(),
                min_length=2,
                max_length=2,
            ),
            min_length=1,
        ),
        min_length=1,
        max_length=1,
    )


@validataclass
class GeojsonBaseFeatureInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: GeojsonBaseFeaturePropertiesInput = DataclassValidator(GeojsonBaseFeaturePropertiesInput)
    geometry: GeojsonFeatureGeometryPointInput = DataclassValidator(GeojsonFeatureGeometryPointInput)

    def to_static_parking_site_input(self, **kwargs) -> StaticParkingSiteInput:
        # Maintain child objects by not using to_dict()
        input_data: dict[str, Any] = {key: getattr(self.properties, key) for key in self.properties.to_dict().keys()}
        input_data.update(kwargs)

        return StaticParkingSiteInput(
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            **input_data,
        )

    def to_static_parking_spot_input(self, **kwargs) -> StaticParkingSpotInput:
        # Maintain child objects by not using to_dict()
        input_data: dict[str, Any] = {key: getattr(self.properties, key) for key in self.properties.to_dict().keys()}
        input_data.update(kwargs)

        return StaticParkingSpotInput(
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            **input_data,
        )

    def update_static_parking_site_input(self, static_parking_site: StaticParkingSiteInput) -> None:
        static_parking_site.lat = self.geometry.coordinates[1]
        static_parking_site.lon = self.geometry.coordinates[0]

        for key in self.properties.to_dict().keys():
            value = getattr(self.properties, key)
            if value is None:
                continue

            setattr(static_parking_site, key, value)


@validataclass
class GeojsonFeatureInput(GeojsonBaseFeatureInput):
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: GeojsonFeaturePropertiesInput = DataclassValidator(GeojsonFeaturePropertiesInput)
    geometry: GeojsonFeatureGeometryPointInput = DataclassValidator(GeojsonFeatureGeometryPointInput)


@validataclass
class GeojsonFeatureParkingSpotInput(GeojsonBaseFeatureInput):
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: GeojsonFeaturePropertiesParkingSpotInput = DataclassValidator(GeojsonFeaturePropertiesParkingSpotInput)
    geometry: GeojsonFeatureGeometryPointInput = DataclassValidator(GeojsonFeatureGeometryPointInput)


@validataclass
class GeojsonInput:
    type: str = AnyOfValidator(allowed_values=['FeatureCollection'])
    features: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))
