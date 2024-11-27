"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, time
from decimal import Decimal
from enum import Enum
from typing import Optional

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnythingValidator,
    DateTimeValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    NumericValidator,
    StringValidator,
    TimeFormat,
    TimeValidator,
    UrlValidator,
)

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus, ParkAndRideType, ParkingSiteType, SupervisionType
from parkapi_sources.validators import ExcelNoneable, ReplacingStringValidator, Rfc1123DateTimeValidator

from .validators import NoneableRemoveValueDict, RemoveValueDict


class HeidelbergFacilityType(Enum):
    HANDICAPPED_ACCESSIBLE_PAYING_MASCHINE = 'handicapped accessible paying machine'
    INTERCOM_AT_EXIT = 'Intercom at Exit'
    SECURITY_CAMERA = 'Security Camera'
    ACCESSABLE = 'Accessable'
    HANDICAPPED_BATHROOM = 'Handicapped Bathroom'
    BATHROOM = 'Bathroom'
    STAFF = 'Staff'
    CHANGING_TABLE = 'Changing Table'
    BIKE_PARKING = 'BikeParking'
    ELEVATOR = 'Elevator'
    DEFIBRILLATOR = 'Defibirlator'
    COPY_MASCHINE_OR_SERVICE = 'CopyMachineOrService'


class HeidelbergPaymentMethodType(Enum):
    CASH = 'Cash'
    MONEY_CARD = 'MoneyCard'
    DEBIT_CART = 'DebitCard'
    GOOGLE = 'Google'
    PAY_PAL = 'PayPal'
    LICENCE_PLATE = 'Licence Plate'
    CREDIT_CARD = 'CreditCard'
    INVOICE = 'Invoice'
    COD = 'COD'


class HeidelbergParkingSiteStatus(Enum):
    OPEN = 'Open'
    CLOSED = 'Closed'
    OPEN_DE = 'Offen'
    CLOSED_DE = 'Geschlossen'
    BROKEN = 'Stoerung'
    UNKNOWN = '0'

    def to_opening_status(self) -> OpeningStatus | None:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.OPEN_DE: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
            self.CLOSED_DE: OpeningStatus.CLOSED,
            self.UNKNOWN: OpeningStatus.UNKNOWN,
            self.BROKEN: OpeningStatus.CLOSED,
        }.get(self)


class HeidelbergParkingType(Enum):
    OFFSTREET_PARKING = 'OffStreetParking'


class HeidelbergParkingSubType(Enum):
    GARAGE = 'Parking Garage'
    PARK_AND_RIDE = 'Park and Ride Car Park'


@validataclass
class HeidelbergInput:
    acceptedPaymentMethod: HeidelbergPaymentMethodType = RemoveValueDict(
        ListValidator(EnumValidator(HeidelbergPaymentMethodType)),
    )
    addressLocality: str = RemoveValueDict(StringValidator())
    availableSpotNumber: Optional[int] = NoneableRemoveValueDict(IntegerValidator()), Default(None)
    closingHours: time = RemoveValueDict(TimeValidator(time_format=TimeFormat.NO_SECONDS))
    description: str = RemoveValueDict(ReplacingStringValidator(mapping={'\r': '', '\n': ' ', '\xa0': ' '}))
    facilities: list[str] = RemoveValueDict(ListValidator(EnumValidator(HeidelbergFacilityType)))
    familyParkingSpots: int = RemoveValueDict(IntegerValidator())
    googlePlaceId: str = RemoveValueDict(StringValidator())
    handicappedParkingSpots: int = RemoveValueDict(IntegerValidator())
    images: list[str] = RemoveValueDict(ListValidator(UrlValidator()))
    lat: Decimal = RemoveValueDict(NumericValidator())
    lon: Decimal = RemoveValueDict(NumericValidator())
    maximumAllowedHeight: Optional[Decimal] = RemoveValueDict(ExcelNoneable(NumericValidator()))
    maximumAllowedWidth: Optional[Decimal] = RemoveValueDict(ExcelNoneable((NumericValidator())))
    observationDateTime: datetime = RemoveValueDict(DateTimeValidator())
    openingHours: time = RemoveValueDict(TimeValidator(time_format=TimeFormat.NO_SECONDS))
    type: HeidelbergParkingType = EnumValidator(HeidelbergParkingType)
    parking_type: HeidelbergParkingSubType = RemoveValueDict(EnumValidator(HeidelbergParkingSubType))
    postalCode: int = RemoveValueDict(IntegerValidator())  # outsch
    provider: str = RemoveValueDict(StringValidator())
    staticName: str = RemoveValueDict(StringValidator())
    staticParkingSiteId: str = RemoveValueDict(StringValidator())
    staticStatus: HeidelbergParkingSiteStatus = RemoveValueDict(EnumValidator(HeidelbergParkingSiteStatus))
    staticTotalSpotNumber: int = RemoveValueDict(IntegerValidator())
    status: HeidelbergParkingSiteStatus = RemoveValueDict(EnumValidator(HeidelbergParkingSiteStatus))
    streetAddress: str = RemoveValueDict(StringValidator())
    streetAddressDriveway: str = RemoveValueDict(StringValidator())
    streetAddressExit: str = RemoveValueDict(StringValidator())
    totalSpotNumber: int = RemoveValueDict(IntegerValidator())
    website: Optional[str] = RemoveValueDict(ExcelNoneable(UrlValidator()))
    womenParkingSpots: int = RemoveValueDict(IntegerValidator())
    prices: list[dict] = RemoveValueDict(ListValidator(AnythingValidator(allowed_types=[dict])))

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        if self.parking_type == HeidelbergParkingSubType.GARAGE:
            parking_site_type = ParkingSiteType.CAR_PARK
        elif self.type == HeidelbergParkingType.OFFSTREET_PARKING:
            parking_site_type = ParkingSiteType.OFF_STREET_PARKING_GROUND
        else:
            parking_site_type = None

        if self.openingHours == self.closingHours:
            opening_hours = '24/7'
        else:
            opening_hours = f'{self.openingHours.isoformat()[:5]}-{self.closingHours.isoformat()[:5]}'

        supervision_type: Optional[SupervisionType] = None
        if HeidelbergFacilityType.STAFF in self.facilities:
            supervision_type = SupervisionType.ATTENDED
        elif HeidelbergFacilityType.SECURITY_CAMERA in self.facilities:
            supervision_type = SupervisionType.VIDEO

        return StaticParkingSiteInput(
            uid=self.staticParkingSiteId,
            name=self.staticName,
            description=self.description,
            lat=self.lat,
            lon=self.lon,
            address=f'{self.streetAddress}, {self.postalCode} {self.addressLocality}',
            operator_name=self.provider,
            max_height=None if self.maximumAllowedHeight is None else int(self.maximumAllowedHeight * 100),
            max_width=None if self.maximumAllowedWidth is None else int(self.maximumAllowedWidth * 100),
            photo_url=self.images[0] if len(self.images) else None,
            capacity=self.totalSpotNumber,
            capacity_disabled=self.handicappedParkingSpots,
            capacity_woman=self.womenParkingSpots,
            capacity_family=self.familyParkingSpots,
            opening_hours=opening_hours,
            static_data_updated_at=self.observationDateTime,
            type=parking_site_type,
            park_and_ride_type=[ParkAndRideType.YES]
            if self.parking_type == HeidelbergParkingSubType.PARK_AND_RIDE
            else None,
            supervision_type=supervision_type,
            has_realtime_data=self.availableSpotNumber is not None,
            has_fee=len(self.prices) > 0,
        )

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.staticParkingSiteId,
            realtime_capacity=self.totalSpotNumber,
            realtime_capacity_disabled=self.handicappedParkingSpots,
            realtime_capacity_woman=self.womenParkingSpots,
            realtime_capacity_family=self.familyParkingSpots,
            realtime_free_capacity=self.availableSpotNumber,
            # TODO: most likely broken, as there are realtime open parking sites with static status broken / unknown
            realtime_opening_status=self.status.to_opening_status(),
            realtime_data_updated_at=self.observationDateTime,
        )


@validataclass
class HeidelbergRealtimeDataInput:
    parkingupdates: list[dict] = ListValidator(AnythingValidator(allowed_types=dict))
    updated: datetime = Rfc1123DateTimeValidator()
