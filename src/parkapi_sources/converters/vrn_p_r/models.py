"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from shapely import GeometryType, Point
from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.helpers import OptionalUnset, UnsetValue
from validataclass.validators import (
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import ParkingSiteRestrictionInput, RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus, ParkAndRideType, ParkingAudience, ParkingSiteType, PurposeType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator, MappedBooleanValidator, TimestampDateTimeValidator


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

    def to_park_and_ride_type(self) -> ParkAndRideType:
        return {
            self.JA: ParkAndRideType.YES,
            self.NEIN: ParkAndRideType.NO,
        }.get(self, ParkAndRideType.NO)


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
    type: VrnParkAndRideType | None = Noneable(EnumValidator(VrnParkAndRideType)), Default(None)
    public_url: str | None = Noneable(UrlValidator(max_length=4096)), Default(None)
    photo_url: str | None = Noneable(UrlValidator(max_length=4096)), Default(None)
    lat: Decimal | None = NumericValidator()
    lon: Decimal | None = NumericValidator()
    address: OptionalUnset[str] = Noneable(StringValidator(min_length=0, max_length=256)), Default(None)
    operator_name: OptionalUnset[str] = Noneable(StringValidator(min_length=0, max_length=256)), Default(None)
    capacity: int = IntegerValidator(min_value=0)
    capacity_charging: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    capacity_family: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    capacity_woman: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    capacity_bus: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    capacity_truck: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    capacity_carsharing: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    capacity_disabled: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    max_height: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    has_realtime_data: OptionalUnset[bool] = (
        Noneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})),
        Default(None),
    )
    vrn_sensor_id: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    realtime_opening_status: VrnParkAndRidePropertiesOpeningStatus | None = (
        Noneable(EnumValidator(VrnParkAndRidePropertiesOpeningStatus)),
        Default(None),
    )
    has_lighting: bool | None = Noneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})), Default(None)
    has_fee: bool | None = Noneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})), Default(None)
    is_covered: bool | None = Noneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False})), Default(None)
    related_location: str | None = Noneable(StringValidator(min_length=0, max_length=256)), Default(None)
    opening_hours: str | None = Noneable(StringValidator(min_length=0, max_length=256)), Default(None)
    park_and_ride_type: VrnParkAndRidePRType | None = (
        Noneable(EnumValidator(VrnParkAndRidePRType)),
        Default(None),
    )
    max_stay: OptionalUnset[int] = Noneable(IntegerValidator(min_value=0)), Default(None)
    fee_description: OptionalUnset[str] = Noneable(StringValidator(max_length=512)), Default(None)
    realtime_free_capacity: OptionalUnset[int] = Noneable(IntegerValidator(min_value=0)), Default(None)
    realtime_occupied: OptionalUnset[int] = Noneable(IntegerValidator(min_value=0)), Default(None)
    realtime_data_updated: OptionalUnset[datetime] = (
        Noneable(TimestampDateTimeValidator(allow_strings=True, divisor=1000)),
        Default(None),
    )


@validataclass
class VrnParkAndRideFeaturesInput:
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])
    properties: VrnParkAndRidePropertiesInput = DataclassValidator(VrnParkAndRidePropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        if 'Mo-So: 24 Stunden' in self.properties.opening_hours or 'Mo-So: Kostenlos' in self.properties.opening_hours:
            opening_hours = '24/7'
        else:
            opening_hours = UnsetValue

        if self.properties.realtime_data_updated is None:
            static_data_updated_at = datetime.now(timezone.utc)
        else:
            static_data_updated_at = self.properties.realtime_data_updated

        parking_site_restrictions: list[ParkingSiteRestrictionInput] = []
        if self.properties.capacity_disabled is not None:
            parking_site_restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.DISABLED,
                    capacity=self.properties.capacity_disabled,
                ),
            )
        if self.properties.capacity_woman is not None:
            parking_site_restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.WOMEN,
                    capacity=self.properties.capacity_woman,
                ),
            )
        if self.properties.capacity_family is not None:
            parking_site_restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.FAMILY,
                )
            )
        if self.properties.capacity_bus is not None:
            parking_site_restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.BUS,
                    capacity=self.properties.capacity_bus,
                ),
            )
        if self.properties.capacity_truck is not None:
            parking_site_restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.TRUCK,
                    capacity=self.properties.capacity_truck,
                ),
            )
        if self.properties.capacity_carsharing is not None:
            parking_site_restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                ),
            )
        if self.properties.capacity_charging is not None:
            parking_site_restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                    capacity=self.properties.capacity_charging,
                ),
            )

        return StaticParkingSiteInput(
            uid=f'{self.properties.original_uid}-{self.properties.vrn_sensor_id}',
            static_data_updated_at=static_data_updated_at,
            opening_hours=opening_hours,
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
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            purpose=PurposeType.CAR,
            photo_url=self.properties.photo_url,
            public_url=self.properties.public_url,
            park_and_ride_type=[self.properties.park_and_ride_type.to_park_and_ride_type()],
            restrictions=parking_site_restrictions,
        )

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        if self.properties.realtime_data_updated is None:
            realtime_data_updated_at = datetime.now(timezone.utc)
        else:
            realtime_data_updated_at = self.properties.realtime_data_updated

        if self.properties.realtime_free_capacity is not None and self.properties.realtime_occupied is not None:
            realtime_capacity = self.properties.realtime_free_capacity + self.properties.realtime_occupied
        else:
            realtime_capacity = UnsetValue

        return RealtimeParkingSiteInput(
            uid=f'{self.properties.original_uid}-{self.properties.vrn_sensor_id}',
            realtime_capacity=realtime_capacity,
            realtime_free_capacity=self.properties.realtime_free_capacity,
            realtime_opening_status=self.properties.realtime_opening_status.to_realtime_opening_status(),
            realtime_data_updated_at=realtime_data_updated_at,
        )
