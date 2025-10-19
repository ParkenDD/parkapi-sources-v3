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
    Noneable,
    NumericValidator,
    StringValidator,
    TimeFormat,
    TimeValidator,
    UrlValidator,
)

from parkapi_sources.models import ParkingSiteRestrictionInput, RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import (
    OpeningStatus,
    ParkAndRideType,
    ParkingAudience,
    ParkingSiteType,
    SupervisionType,
)
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
    id: str = StringValidator()
    acceptedPaymentMethod: Optional[list[HeidelbergPaymentMethodType]] = (
        Noneable(
            RemoveValueDict(ListValidator(EnumValidator(HeidelbergPaymentMethodType))),
        ),
        Default(None),
    )
    addressLocality: Optional[str] = Noneable(RemoveValueDict(StringValidator())), Default(None)
    availableSpotNumber: Optional[int] = NoneableRemoveValueDict(IntegerValidator(min_value=0)), Default(None)
    closingHours: Optional[time] = (
        Noneable(RemoveValueDict(TimeValidator(time_format=TimeFormat.NO_SECONDS))),
        Default(None),
    )
    description: Optional[str] = (
        Noneable(RemoveValueDict(ReplacingStringValidator(mapping={'\r': '', '\n': ' ', '\xa0': ' '}))),
        Default(None),
    )
    facilities: Optional[list[str]] = (
        Noneable(RemoveValueDict(ListValidator(EnumValidator(HeidelbergFacilityType)))),
        Default(None),
    )
    familyParkingSpots: Optional[int] = Noneable(RemoveValueDict(IntegerValidator())), Default(None)
    googlePlaceId: Optional[str] = Noneable(RemoveValueDict(StringValidator())), Default(None)
    handicappedParkingSpots: Optional[int] = Noneable(RemoveValueDict(IntegerValidator())), Default(None)
    images: Optional[list[str]] = Noneable(RemoveValueDict(ListValidator(UrlValidator()))), Default(None)
    lat: Decimal = RemoveValueDict(NumericValidator())
    lon: Decimal = RemoveValueDict(NumericValidator())
    maximumAllowedHeight: Optional[Decimal] = (
        Noneable(RemoveValueDict(ExcelNoneable(NumericValidator()))),
        Default(None),
    )
    maximumAllowedWidth: Optional[Decimal] = (
        Noneable(RemoveValueDict(ExcelNoneable((NumericValidator())))),
        Default(None),
    )
    observationDateTime: datetime = RemoveValueDict(DateTimeValidator())
    openingHours: Optional[time] = (
        Noneable(RemoveValueDict(TimeValidator(time_format=TimeFormat.NO_SECONDS))),
        Default(None),
    )
    type: HeidelbergParkingType = EnumValidator(HeidelbergParkingType)
    parking_type: HeidelbergParkingSubType = RemoveValueDict(EnumValidator(HeidelbergParkingSubType))
    postalCode: Optional[int] = Noneable(RemoveValueDict(IntegerValidator())), Default(None)  # outsch
    provider: Optional[str] = Noneable(RemoveValueDict(StringValidator())), Default(None)
    staticName: str = RemoveValueDict(StringValidator())
    staticParkingSiteId: Optional[str] = Noneable(RemoveValueDict(StringValidator())), Default(None)
    staticStatus: Optional[HeidelbergParkingSiteStatus] = (
        Noneable(RemoveValueDict(EnumValidator(HeidelbergParkingSiteStatus))),
        Default(None),
    )
    staticTotalSpotNumber: Optional[int] = Noneable(RemoveValueDict(IntegerValidator())), Default(None)
    status: HeidelbergParkingSiteStatus = RemoveValueDict(EnumValidator(HeidelbergParkingSiteStatus))
    streetAddress: Optional[str] = Noneable(RemoveValueDict(StringValidator())), Default(None)
    streetAddressDriveway: Optional[str] = Noneable(RemoveValueDict(StringValidator())), Default(None)
    streetAddressExit: Optional[str] = Noneable(RemoveValueDict(StringValidator())), Default(None)
    totalSpotNumber: int = RemoveValueDict(IntegerValidator())
    website: Optional[str] = Noneable(RemoveValueDict(ExcelNoneable(UrlValidator()))), Default(None)
    womenParkingSpots: Optional[int] = Noneable(RemoveValueDict(IntegerValidator())), Default(None)
    prices: Optional[list[dict]] = (
        Noneable(RemoveValueDict(ListValidator(AnythingValidator(allowed_types=[dict])))),
        Default(None),
    )

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

        if self.streetAddress and self.postalCode and self.addressLocality:
            address = f'{self.streetAddress}, {self.postalCode} {self.addressLocality}'
        elif self.streetAddress:
            address = f'{self.streetAddress}, Heidelberg'
        else:
            address = None

        static_parking_site_input = StaticParkingSiteInput(
            uid=self.id,
            name=self.staticName,
            description=self.description,
            lat=self.lat,
            lon=self.lon,
            address=address,
            operator_name=self.provider,
            max_height=None if self.maximumAllowedHeight is None else int(self.maximumAllowedHeight * 100),
            max_width=None if self.maximumAllowedWidth is None else int(self.maximumAllowedWidth * 100),
            photo_url=self.images[0] if len(self.images) else None,
            capacity=self.totalSpotNumber,
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

        restrictions: list[ParkingSiteRestrictionInput] = []
        if self.handicappedParkingSpots is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.DISABLED,
                    capacity=self.handicappedParkingSpots,
                ),
            )
        if self.womenParkingSpots is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.WOMEN,
                    capacity=self.womenParkingSpots,
                ),
            )
        if self.familyParkingSpots is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.FAMILY,
                    capacity=self.familyParkingSpots,
                )
            )
        if len(restrictions):
            static_parking_site_input.restrictions = restrictions

        return static_parking_site_input

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        realtime_parking_site_input = RealtimeParkingSiteInput(
            uid=self.id,
            realtime_capacity=self.totalSpotNumber,
            realtime_free_capacity=self.availableSpotNumber,
            # TODO: most likely broken, as there are realtime open parking sites with static status broken / unknown
            realtime_opening_status=self.status.to_opening_status(),
            realtime_data_updated_at=self.observationDateTime,
        )

        restrictions: list[ParkingSiteRestrictionInput] = []
        if self.handicappedParkingSpots is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.DISABLED,
                    realtime_capacity=self.handicappedParkingSpots,
                ),
            )
        if self.womenParkingSpots is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.WOMEN,
                    realtime_capacity=self.womenParkingSpots,
                ),
            )
        if self.familyParkingSpots is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.FAMILY,
                    realtime_capacity=self.familyParkingSpots,
                )
            )
        if len(restrictions):
            realtime_parking_site_input.restrictions = restrictions

        return realtime_parking_site_input


@validataclass
class HeidelbergRealtimeDataInput:
    parkingupdates: list[dict] = ListValidator(AnythingValidator(allowed_types=dict))
    updated: datetime = Rfc1123DateTimeValidator()
