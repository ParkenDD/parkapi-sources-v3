"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum

from validataclass.dataclasses import DefaultUnset, ValidataclassMixin, validataclass
from validataclass.exceptions import ValidationError
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

from parkapi_sources.converters.base_converter.pull import GeojsonFeatureGeometryInput
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from parkapi_sources.validators import MappedBooleanValidator, ParsedDateValidator, TimestampDateTimeValidator


class VrnParkAndRideType(Enum):
    CAR_PARK = 'Parkhaus'
    OFF_STREET_PARKING_GROUND = 'Parkplatz'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
            self.OFF_STREET_PARKING_GROUND: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)


@validataclass
class VrnParkAndRidePropertiesOpeningHoursInput:
    string: str = StringValidator(min_length=1, max_length=256)
    langIso639: str = StringValidator(min_length=1, max_length=256)


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
    description: OptionalUnset[str] = NoneToUnsetValue(StringValidator(max_length=512)), DefaultUnset
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
    has_realtime_data: OptionalUnset[bool] = NoneToUnsetValue(MappedBooleanValidator(mapping={'ja': True, 'nein': False})), DefaultUnset
    vrn_sensor_id: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    realtime_opening_status: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    created_at: OptionalUnset[date] = NoneToUnsetValue(ParsedDateValidator(date_format='%Y-%m-%d')), DefaultUnset
    static_data_updated_at: OptionalUnset[datetime] = (
        NoneToUnsetValue(TimestampDateTimeValidator(allow_strings=True, divisor=1000)),
        DefaultUnset,
    )
    has_lighting: OptionalUnset[bool] = NoneToUnsetValue(MappedBooleanValidator(mapping={'ja': True, 'nein': False})), DefaultUnset
    has_fee: OptionalUnset[bool] = NoneToUnsetValue(MappedBooleanValidator(mapping={'ja': True, 'nein': False})), DefaultUnset
    is_covered: OptionalUnset[bool] = NoneToUnsetValue(MappedBooleanValidator(mapping={'ja': True, 'nein': False})), DefaultUnset
    related_location: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    opening_hours: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    park_and_ride_type: OptionalUnset[str] = NoneToUnsetValue(StringValidator(min_length=0, max_length=256)), DefaultUnset
    max_stay: OptionalUnset[int] = NoneToUnsetValue(IntegerValidator(min_value=0)), DefaultUnset
    fee_description: OptionalUnset[str] = NoneToUnsetValue(StringValidator(max_length=512)), DefaultUnset


@validataclass
class VrnParkAndRideFeaturesInput:
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)
    properties: VrnParkAndRidePropertiesInput = DataclassValidator(VrnParkAndRidePropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.properties.original_uid),
            group_uid=str(self.properties.vrn_sensor_id),
            name=self.properties.name if self.properties.name != '' else 'Fahrrad-Abstellanlagen',
            type=self.properties.type.to_parking_site_type(),
            description=self.properties.description,
            capacity=self.properties.capacity,
            has_realtime_data=self.properties.has_realtime_data,
            has_lighting=self.properties.has_lighting,
            is_covered=self.properties.is_covered,
            related_location=self.properties.related_location,
            operator_name=self.properties.operator_name,
            max_height=self.properties.max_height,
            has_fee=self.properties.has_fee,
            fee_description=self.properties.fee_description,
            capacity_charging=self.properties.capacity_charging,
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            static_data_updated_at=datetime.now(timezone.utc)
            if self.properties.static_data_updated_at is UnsetValue
            else self.properties.static_data_updated_at,
            purpose=PurposeType.CAR,
            opening_hours='24/7'
            if 'Mo-So: 24 Stunden' in self.properties.opening_hours or 'Mo-So: Kostenlos' in self.properties.opening_hours
            else UnsetValue,
        )


@validataclass
class VrnParkAndRideMultiguideInput:
    Name: str = StringValidator()
    Id: int = IntegerValidator(allow_strings=True)
    Constructed: int = IntegerValidator(allow_strings=True)
    Available: int = IntegerValidator(allow_strings=True)
    Free: int = IntegerValidator(allow_strings=True)
    Occupied: int = IntegerValidator(allow_strings=True)
    Reserved: int = IntegerValidator(allow_strings=True)
    Defect: int = IntegerValidator(allow_strings=True)

    def __post_init__(self):
        if self.Constructed < self.Occupied:
            raise ValidationError(reason='More occupied sites than capacity')

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=str(self.Id),
            realtime_capacity=self.Constructed,
            realtime_free_capacity=self.Free,
            realtime_data_updated_at=datetime.now(timezone.utc),
        )


@validataclass
class VrnParkAndRideSonahInput:
    Name: str = StringValidator()
    LocationID: int = IntegerValidator()
    TotalParking: int = NumericValidator()
    FreeParking: int = NumericValidator()
    OccupiedParking: int = NumericValidator()

    def __post_init__(self):
        if self.TotalParking < self.OccupiedParking:
            raise ValidationError(reason='More occupied sites than capacity')

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=str(self.LocationID),
            realtime_capacity=int(self.TotalParking),
            realtime_free_capacity=int(self.FreeParking),
            realtime_data_updated_at=datetime.now(timezone.utc),
        )
