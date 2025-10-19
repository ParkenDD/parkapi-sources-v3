"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from typing import Any

from shapely import GeometryType, Point
from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.validators import (
    AnyOfValidator,
    AnythingValidator,
    BooleanValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.util import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator

from .enums import ParkAndRideType, ParkingSiteType
from .parking_site_inputs import StaticParkingSiteInput
from .parking_spot_inputs import StaticParkingSpotInput
from .shared_inputs import ExternalIdentifierInput, ParkingRestrictionInput


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
    restrictions: list[ParkingRestrictionInput] | None = (
        ListValidator(DataclassValidator(ParkingRestrictionInput)),
        Default(None),
    )
    has_realtime_data: bool | None = BooleanValidator(), Default(None)


@validataclass
class GeojsonBaseFeatureInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: GeojsonBaseFeaturePropertiesInput = DataclassValidator(GeojsonBaseFeaturePropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])

    def to_static_parking_site_input(self, **kwargs) -> StaticParkingSiteInput:
        # Maintain child objects by not using to_dict()
        input_data: dict[str, Any] = {key: getattr(self.properties, key) for key in self.properties.to_dict().keys()}
        input_data.update(kwargs)

        return StaticParkingSiteInput(
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            **input_data,
        )

    def to_static_parking_spot_input(self, **kwargs) -> StaticParkingSpotInput:
        # Maintain child objects by not using to_dict()
        input_data: dict[str, Any] = {key: getattr(self.properties, key) for key in self.properties.to_dict().keys()}
        input_data.update(kwargs)

        return StaticParkingSpotInput(
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            **input_data,
        )

    def update_static_parking_site_input(self, static_parking_site: StaticParkingSiteInput) -> None:
        static_parking_site.lat = round_7d(self.geometry.y)
        static_parking_site.lon = round_7d(self.geometry.x)

        for key in self.properties.to_dict().keys():
            value = getattr(self.properties, key)
            if value is None:
                continue

            setattr(static_parking_site, key, value)


@validataclass
class GeojsonFeatureInput(GeojsonBaseFeatureInput):
    properties: GeojsonFeaturePropertiesInput = DataclassValidator(GeojsonFeaturePropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])


@validataclass
class GeojsonFeatureParkingSpotInput(GeojsonBaseFeatureInput):
    properties: GeojsonFeaturePropertiesParkingSpotInput = DataclassValidator(GeojsonFeaturePropertiesParkingSpotInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])


@validataclass
class GeojsonInput:
    type: str = AnyOfValidator(allowed_values=['FeatureCollection'])
    features: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))
