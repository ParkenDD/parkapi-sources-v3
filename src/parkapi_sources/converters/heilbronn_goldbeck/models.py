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
    AnythingValidator,
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
    nativeId: Optional[str] = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    type: HeilbronnGoldbeckCounterTypeInput = DataclassValidator(HeilbronnGoldbeckCounterTypeInput)
    key: Optional[str] = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    name: Optional[str] = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    counterFeatures: Optional[list[str]] = Noneable(ListValidator(StringValidator(max_length=256))), Default([])
    maxPlaces: int = IntegerValidator(min_value=0, allow_strings=True)
    occupiedPlaces: int = IntegerValidator(min_value=0, allow_strings=True)
    freePlaces: int = IntegerValidator(allow_strings=True)
    status: Optional[CounterStatus] = Noneable(EnumValidator(CounterStatus)), Default(None)

    def is_total_counter(self) -> bool:
        return self.type.type.value == 'TOTAL' and (
            self.type.reservationStatus.value == 'UNKNOWN' or self.type.reservationStatus.value == 'NO_RESERVATIONS'
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
            return RealtimeParkingSiteInput(
                uid=str(self.facilityId),
                realtime_capacity=total_counter.maxPlaces,
                realtime_free_capacity=total_counter.maxPlaces - total_counter.occupiedPlaces
                if total_counter.freePlaces < 0 and total_counter.occupiedPlaces
                else total_counter.freePlaces,
                realtime_data_updated_at=self.valuesFrom,
            )
        return None


@validataclass
class HeilbronnGoldbeckPositionInput:
    longitude: Decimal = NumericValidator()
    latitude: Decimal = NumericValidator()


@validataclass
class HeilbronnGoldbeckPostalAddressInput:
    name: Optional[str] = Noneable(StringValidator(max_length=512)), Default(None)
    street1: Optional[str] = Noneable(StringValidator(max_length=512)), Default(None)
    street2: Optional[str] = Noneable(StringValidator(max_length=512)), Default(None)
    city: Optional[str] = Noneable(StringValidator(max_length=512)), Default(None)
    cityId: Optional[int] = Noneable(IntegerValidator(min_value=0)), Default(None)
    zip: Optional[str] = Noneable(StringValidator(max_length=32)), Default(None)
    isoCountryCode: Optional[str] = Noneable(StringValidator(max_length=4)), Default(None)

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
    type: Optional[str] = Noneable(StringValidator(max_length=256)), Default(None)
    key: Optional[str] = Noneable(StringValidator(max_length=256)), Default(None)
    priority: Optional[int] = Noneable(IntegerValidator()), Default(None)
    timeDefinitions: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict])), Default([])
    lastUpdatedAt: Optional[datetime] = (
        Noneable(
            DateTimeValidator(
                local_timezone=timezone.utc,
                target_timezone=timezone.utc,
            )
        ),
        Default(None),
    )
    plainTextValue: Optional[str] = Noneable(StringValidator(max_length=4096, unsafe=True)), Default(None)


@validataclass
class HeilbronnGoldbeckTariffInput:
    id: Optional[int] = Noneable(IntegerValidator(min_value=0)), Default(None)
    key: Optional[str] = Noneable(StringValidator(max_length=256)), Default(None)
    name: Optional[str] = Noneable(StringValidator(max_length=256)), Default(None)
    isActive: Optional[bool] = Noneable(BooleanValidator()), Default(None)
    tariffItems: Optional[list[HeilbronnGoldbeckTariffItemInput]] = (
        Noneable(ListValidator(DataclassValidator(HeilbronnGoldbeckTariffItemInput))),
        Default([]),
    )

    def get_fee_description(self) -> Optional[str]:
        for tariff_item in self.tariffItems:
            if tariff_item.plainTextValue:
                return tariff_item.plainTextValue
        return None


@validataclass
class HeilbronnGoldbeckFacilitiesInput:
    id: int = IntegerValidator(min_value=0, allow_strings=True), Default(None)
    key: Optional[str] = Noneable(StringValidator(min_length=1, max_length=256))
    parentId: Optional[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    status: Optional[FacilityStatus] = Noneable((EnumValidator(FacilityStatus))), Default(None)
    active: Optional[bool] = Noneable(BooleanValidator()), Default(None)
    lastUpdatedAt: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )
    name: str = StringValidator(min_length=1, max_length=256, unsafe=True)
    definitionId: Optional[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    tenantId: Optional[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    position: HeilbronnGoldbeckPositionInput = DataclassValidator(HeilbronnGoldbeckPositionInput)
    postalAddress: Optional[HeilbronnGoldbeckPostalAddressInput] = (
        Noneable(DataclassValidator(HeilbronnGoldbeckPostalAddressInput)),
        Default(None),
    )
    tariffs: Optional[list[HeilbronnGoldbeckTariffInput]] = (
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
                fee_description = tariff.get_fee_description()
                if fee_description:
                    has_fee = True
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
            static_data_updated_at=self.lastUpdatedAt,
        )
