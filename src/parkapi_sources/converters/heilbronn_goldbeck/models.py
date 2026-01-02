"""
Copyright 202 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from zoneinfo import ZoneInfo

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    BooleanValidator,
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    NumericValidator,
    StringValidator,
)

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType


class CounterType(Enum):
    SHORT_TERM_PARKER = 'SHORT_TERM_PARKER'
    CONTRACT_PARKER = 'CONTRACT_PARKER'
    PREPAID_PARKER = 'PREPAID_PARKER'
    FIXED_PERIOD_PARKER = 'FIXED_PERIOD_PARKER'
    POSTPAID_PARKER = 'POSTPAID_PARKER'
    TOTAL = 'TOTAL'
    AREA = 'AREA'
    OTHER = 'OTHER'


class ReservationStatus(Enum):
    ONLY_RESERVATIONS = 'ONLY_RESERVATIONS'
    NO_RESERVATIONS = 'NO_RESERVATIONS'
    UNKNOWN = 'UNKNOWN'


class CounterStatus(Enum):
    UNKNOWN = 'UNKNOWN'
    FREE = 'FREE'
    ALMOST_FULL = 'ALMOST_FULL'
    FULL = 'FULL'


class FacilityStatus(Enum):
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    DELETED = 'DELETED'


@validataclass
class HeilbronnGoldbeckCounterTypeInput:
    type: CounterType = EnumValidator(CounterType)
    reservationStatus: ReservationStatus = EnumValidator(ReservationStatus)


@validataclass
class HeilbronnGoldbeckCounterInput:
    nativeId: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    type: HeilbronnGoldbeckCounterTypeInput = DataclassValidator(HeilbronnGoldbeckCounterTypeInput)
    maxPlaces: int | None = IntegerValidator(min_value=0, allow_strings=True), Default(None)
    occupiedPlaces: int | None = IntegerValidator(min_value=0, allow_strings=True), Default(None)
    freePlaces: int | None = IntegerValidator(allow_strings=True), Default(None)
    status: CounterStatus | None = Noneable(EnumValidator(CounterStatus)), Default(None)

    def is_total_counter(self) -> bool:
        return (
            self.type.type is CounterType.TOTAL
            and self.type.reservationStatus
            in {
                ReservationStatus.UNKNOWN,
                ReservationStatus.NO_RESERVATIONS,
            }
            and self.maxPlaces is not None
        )


@validataclass
class HeilbronnGoldbeckOccupanciesInput:
    facilityId: int = IntegerValidator(min_value=0, allow_strings=True)
    counters: list[HeilbronnGoldbeckCounterInput] = ListValidator(DataclassValidator(HeilbronnGoldbeckCounterInput))
    valuesFrom: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )

    def get_total_counter(self) -> Optional[HeilbronnGoldbeckCounterInput]:
        for counter in self.counters:
            if counter.is_total_counter():
                return counter
        return None

    def to_realtime_parking_site_input(self) -> Optional[RealtimeParkingSiteInput]:
        total_counter = self.get_total_counter()
        if total_counter:
            if total_counter.freePlaces < 0 and total_counter.occupiedPlaces:
                realtime_free_capacity = total_counter.maxPlaces - total_counter.occupiedPlaces
            else:
                realtime_free_capacity = total_counter.freePlaces

            return RealtimeParkingSiteInput(
                uid=str(self.facilityId),
                realtime_capacity=total_counter.maxPlaces,
                realtime_free_capacity=realtime_free_capacity,
                realtime_data_updated_at=self.valuesFrom,
            )
        return None


@validataclass
class HeilbronnGoldbeckPositionInput:
    longitude: Decimal = NumericValidator()
    latitude: Decimal = NumericValidator()


@validataclass
class HeilbronnGoldbeckPostalAddressInput:
    name: str | None = Noneable(StringValidator(max_length=512)), Default(None)
    street1: str | None = Noneable(StringValidator(max_length=512)), Default(None)
    street2: str | None = Noneable(StringValidator(max_length=512)), Default(None)
    city: str | None = Noneable(StringValidator(max_length=512)), Default(None)
    zip: str | None = Noneable(StringValidator(max_length=32)), Default(None)

    def to_address(self) -> Optional[str]:
        parts: list[str] = []
        street_parts = [part for part in [self.street1, self.street2] if part]
        if street_parts:
            parts.append(' '.join(street_parts))

        city_parts = [part for part in [self.zip, self.city] if part]
        if city_parts:
            parts.append(' '.join(city_parts))

        if not parts:
            return None

        return ', '.join(parts)


@validataclass
class HeilbronnGoldbeckTariffItemInput:
    key: str | None = Noneable(StringValidator(max_length=256)), Default(None)
    plainTextValue: str | None = Noneable(StringValidator(max_length=4096)), Default(None)


@validataclass
class HeilbronnGoldbeckTariffInput:
    id: int | None = Noneable(IntegerValidator(min_value=0)), Default(None)
    isActive: bool | None = Noneable(BooleanValidator()), Default(None)
    tariffItems: list[HeilbronnGoldbeckTariffItemInput] = (
        ListValidator(DataclassValidator(HeilbronnGoldbeckTariffItemInput)),
        Default([]),
    )

    def has_tariff_input(self) -> Optional[bool]:
        if self.isActive:
            return self.isActive
        return False

    def get_fee_description(self) -> Optional[str]:
        for tariff_item in self.tariffItems:
            if tariff_item.plainTextValue:
                return tariff_item.plainTextValue
        return None


@validataclass
class HeilbronnGoldbeckFacilitiesInput:
    id: int = IntegerValidator(min_value=0, allow_strings=True)
    status: Optional[FacilityStatus] = Noneable((EnumValidator(FacilityStatus))), Default(None)
    lastUpdatedAt: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )
    name: str = StringValidator(min_length=1, max_length=256, unsafe=True)
    position: HeilbronnGoldbeckPositionInput = DataclassValidator(HeilbronnGoldbeckPositionInput)
    postalAddress: Optional[HeilbronnGoldbeckPostalAddressInput] = (
        Noneable(DataclassValidator(HeilbronnGoldbeckPostalAddressInput)),
        Default(None),
    )
    tariffs: list[HeilbronnGoldbeckTariffInput] = (
        Noneable(ListValidator(DataclassValidator(HeilbronnGoldbeckTariffInput))),
        Default([]),
    )

    def to_static_parking_site_input(
        self,
        heilbronn_goldbeck_occupancies_input: HeilbronnGoldbeckOccupanciesInput,
    ) -> StaticParkingSiteInput:
        total_counter = heilbronn_goldbeck_occupancies_input.get_total_counter()
        fee_description = None
        has_fee = False
        if self.tariffs:
            for tariff in self.tariffs:
                if tariff.has_tariff_input():
                    has_fee = tariff.has_tariff_input()
                    fee_description = tariff.get_fee_description()
                    break

        return StaticParkingSiteInput(
            uid=str(self.id),
            name=self.name,
            lat=self.position.latitude,
            lon=self.position.longitude,
            purpose=PurposeType.CAR,
            address=self.postalAddress.to_address(),
            capacity=total_counter.maxPlaces,
            has_fee=has_fee,
            type=ParkingSiteType.CAR_PARK,
            has_realtime_data=True,
            fee_description=fee_description,
            static_data_updated_at=self.lastUpdatedAt,
        )
