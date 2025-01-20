"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from validataclass.dataclasses import DefaultUnset, ValidataclassMixin, validataclass
from validataclass.helpers import OptionalUnset, UnsetValue
from validataclass.validators import (
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    NoneToUnsetValue,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus, ParkAndRideType, ParkingSiteType, PurposeType
from parkapi_sources.models.geojson_inputs import GeojsonFeatureGeometryInput
from parkapi_sources.validators import MappedBooleanValidator, TimestampDateTimeValidator


class VrnParkAndRideType(Enum):
    CAR_PARK = 'Parkhaus'
    OFF_STREET_PARKING_GROUND = 'Parkplatz'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
            self.OFF_STREET_PARKING_GROUND: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)


class VrnParkAndRidePRType(Enum):
    JA = 'ja'
    NEIN = 'nein'

    def to_park_and_ride_type(self) -> ParkingSiteType:
        return {
            self.JA: ParkAndRideType.YES,
            self.NEIN: ParkAndRideType.NO,
        }.get(self)


@validataclass
class VrnParkAndRidePropertiesOpeningHoursInput:
    string: str = StringValidator(min_length=1, max_length=256)
    langIso639: str = StringValidator(min_length=1, max_length=256)


class VrnParkAndRidePropertiesOpeningStatus(Enum):
    UNKNOWN = 'unbekannt'

    def to_realtime_opening_status(self) -> OpeningStatus | None:
        return {
            self.UNKNOWN: OpeningStatus.UNKNOWN,
        }.get(self)


@validataclass
class VrnParkAndRidePropertiesInput(ValidataclassMixin):
    original_uid: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(min_length=0, max_length=256)
    type: OptionalUnset[VrnParkAndRideType] = NoneToUnsetValue(EnumValidator(VrnParkAndRideType)), DefaultUnset
    public_url: OptionalUnset[str] = NoneToUnsetValue(UrlValidator(max_length=4096)), DefaultUnset
    photo_url: OptionalUnset[str] = NoneToUnsetValue(UrlValidator(max_length=4096)), DefaultUnset
    lat: OptionalUnset[Decimal] = NumericValidator()
    lon: OptionalUnset[Decimal] = NumericValidator()
    address: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    operator_name: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    capacity: int = IntegerValidator(min_value=0)
    capacity_charging: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    capacity_family: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    capacity_woman: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    capacity_bus: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    capacity_truck: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    capacity_carsharing: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    capacity_disabled: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    max_height: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    has_realtime_data: OptionalUnset[bool] = (
        NoneToUnsetValue(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        DefaultUnset,
    )
    vrn_sensor_id: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    realtime_opening_status: OptionalUnset[VrnParkAndRidePropertiesOpeningStatus] = (
        NoneToUnsetValue(EnumValidator(VrnParkAndRidePropertiesOpeningStatus)),
        DefaultUnset,
    )
    has_lighting: OptionalUnset[bool] = (
        NoneToUnsetValue(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        DefaultUnset,
    )
    has_fee: OptionalUnset[bool] = (
        NoneToUnsetValue(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        DefaultUnset,
    )
    is_covered: OptionalUnset[bool] = (
        NoneToUnsetValue(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        DefaultUnset,
    )
    related_location: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    opening_hours: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    park_and_ride_type: OptionalUnset[VrnParkAndRidePRType] = (
        NoneToUnsetValue(EnumValidator(VrnParkAndRidePRType)),
        DefaultUnset,
    )
    max_stay: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    fee_description: OptionalUnset[str] = NoneToUnsetValue(StringValidator(max_length=512)), DefaultUnset
    realtime_free_capacity: int = IntegerValidator(min_value=0)
    realtime_occupied: int = IntegerValidator(min_value=0)
    reatime_data_updated: OptionalUnset[datetime] = (
        NoneToUnsetValue(TimestampDateTimeValidator(allow_strings=True, divisor=1000)),
        DefaultUnset,
    )


@validataclass
class VrnParkAndRideFeaturesInput:
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)
    properties: VrnParkAndRidePropertiesInput = DataclassValidator(VrnParkAndRidePropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.properties.vrn_sensor_id),
            group_uid=f'{self.properties.original_uid}-{self.properties.vrn_sensor_id}',
            name=self.properties.name if self.properties.name != '' else 'P+R Parkplätze',
            type=self.properties.type.to_parking_site_type(),
            capacity=self.properties.capacity,
            has_realtime_data=self.properties.has_realtime_data,
            has_lighting=self.properties.has_lighting,
            is_covered=self.properties.is_covered,
            related_location=self.properties.related_location,
            operator_name=self.properties.operator_name,
            max_height=self.properties.max_height,
            max_stay=self.properties.max_stay,
            has_fee=self.properties.has_fee,
            fee_description=self.properties.fee_description,
            capacity_charging=self.properties.capacity_charging,
            capacity_carsharing=self.properties.capacity_carsharing,
            capacity_disabled=self.properties.capacity_disabled,
            capacity_woman=self.properties.capacity_woman,
            capacity_family=self.properties.capacity_family,
            capacity_truck=self.properties.capacity_truck,
            capacity_bus=self.properties.capacity_bus,
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            static_data_updated_at=datetime.now(timezone.utc)
            if self.properties.reatime_data_updated is UnsetValue
            else self.properties.reatime_data_updated,
            purpose=PurposeType.CAR,
            opening_hours='24/7'
            if 'Mo-So: 24 Stunden' in self.properties.opening_hours
            or 'Mo-So: Kostenlos' in self.properties.opening_hours
            else UnsetValue,
            photo_url=self.properties.photo_url,
            public_url=self.properties.public_url,
            park_and_ride_type=[self.properties.park_and_ride_type.to_park_and_ride_type()],
        )

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=str(self.properties.vrn_sensor_id),
            realtime_capacity=self.properties.realtime_free_capacity + self.properties.realtime_occupied,
            realtime_free_capacity=self.properties.realtime_free_capacity,
            realtime_opening_status=self.properties.realtime_opening_status.to_realtime_opening_status(),
            realtime_data_updated_at=datetime.now(timezone.utc)
            if self.properties.reatime_data_updated is UnsetValue
            else self.properties.reatime_data_updated,
        )
