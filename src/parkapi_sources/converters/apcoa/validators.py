"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional
from zoneinfo import ZoneInfo

from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import (
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models.enums import ParkingSiteType
from parkapi_sources.validators import SpacedDateTimeValidator


class ApcoaParkingSpaceType:
    WOMEN_SPACES = 'Women Spaces'
    FAMILY_SPACES = 'Family Spaces'
    CARSHARING_SPACES = 'Carsharing Spaces'
    DISABLED_SPACES = 'Disabled Spaces'
    EV_CHARGING_BAYS = 'EV Charging Bays'
    EV_CHARGING = 'EV Charging'
    TOTAL_SPACES = 'Total Spaces'
    ELECTRIC_CAR_CHARGING_SPACES = 'Electric Car Charging Spaces'
    ELECTRIC_CAR_FAST_CHARGING_SPACES = 'Electric Car Fast Charging Spaces'
    BUS_OR_COACHES_SPACES = 'Bus/Coaches Spaces'
    CAR_RENTAL_AND_SHARING = 'Car rental & sharing (weekdays from 8am to 8pm)'
    PICKUP_AND_DROPOFF = 'PickUp&DropOff (weekdays from 8pm to 8am)'


class ApcoaCarparkType(Enum):
    MLCP = 'MLCP'
    OFF_STREET_OPEN = 'Off-street open'
    OFF_STREET_UNDERGROUND = 'Off-street underground'
    ON_STREET = 'On-street'
    OPEN_SURFACE = 'Open Surface'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        # TODO: find out more details about this enumeration for a proper mapping
        return {
            self.MLCP: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_OPEN: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_UNDERGROUND: ParkingSiteType.UNDERGROUND,
            self.ON_STREET: ParkingSiteType.ON_STREET,
            self.OPEN_SURFACE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self, ParkingSiteType.OTHER)


class ApcoaNavigationLocationType:
    DEFAULT = 'default'
    CAR_ENTRY = 'CarEntry'


class ApcoaOpeningHoursWeekdays(Enum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'

    def to_osm_opening_day_format(self) -> str:
        return {
            self.MONDAY: 'Mo',
            self.TUESDAY: 'Tu',
            self.WEDNESDAY: 'We',
            self.THURSDAY: 'Th',
            self.FRIDAY: 'Fr',
            self.SATURDAY: 'Sa',
            self.SUNDAY: 'Su',
        }.get(self, None)


@validataclass
class ApcoaCarparkTypeNameInput:
    Name: ApcoaCarparkType = EnumValidator(ApcoaCarparkType)


@validataclass
class ApcoaLocationGeocoordinatesInput:
    Longitude: Decimal = NumericValidator()
    Latitude: Decimal = NumericValidator()


@validataclass
class ApcoaNavigationLocationsInput:
    GeoCoordinates: ApcoaLocationGeocoordinatesInput = DataclassValidator(ApcoaLocationGeocoordinatesInput)
    LocationType: Optional[str] = Noneable(StringValidator())


@validataclass
class ApcoaAdressInput:
    Street: Optional[str] = Noneable(StringValidator())
    Zip: Optional[str] = Noneable(StringValidator())
    City: Optional[str] = Noneable(StringValidator())
    Region: Optional[str] = Noneable(StringValidator())


@validataclass
class ApcoaParkingSpaceInput:
    Type: str = StringValidator()
    Count: int = IntegerValidator(allow_strings=True, min_value=0)


@validataclass
class ApcoaOpeningHoursInput:
    Weekday: ApcoaOpeningHoursWeekdays = EnumValidator(ApcoaOpeningHoursWeekdays)
    OpeningTimes: str = StringValidator()


@validataclass
class ApcoaCarparkPhotoURLInput:
    CarparkPhotoURL1: Optional[str] = Noneable(UrlValidator())
    CarparkPhotoURL2: Optional[str] = Noneable(UrlValidator())
    CarparkPhotoURL3: Optional[str] = Noneable(UrlValidator())
    CarparkPhotoURL4: Optional[str] = Noneable(UrlValidator())


@validataclass
class ApcoaIndicativeTariffInput:
    MinPrefix: Optional[str] = Noneable(StringValidator())
    MinValue: Optional[Decimal] = Noneable(NumericValidator())
    MinSuffix: Optional[str] = Noneable(StringValidator())
    MaxPrefix: Optional[str] = Noneable(StringValidator())
    MaxValue: Optional[Decimal] = Noneable(NumericValidator())
    MaxSuffix: Optional[str] = Noneable(StringValidator())
    Currency: Optional[str] = Noneable(StringValidator())
    CurrencyCode: Optional[str] = Noneable(StringValidator())
    TaxRate: Optional[Decimal] = Noneable(NumericValidator())


@validataclass
class ApcoaParkingSiteInput:
    CarParkId: int = IntegerValidator(allow_strings=True)
    CarparkLongName: Optional[str] = Noneable(StringValidator())
    CarparkShortName: Optional[str] = Noneable(StringValidator())
    CarParkWebsiteURL: Optional[str] = Noneable(UrlValidator())
    CarParkPhotoURLs: Optional[ApcoaCarparkPhotoURLInput] = Noneable(DataclassValidator(ApcoaCarparkPhotoURLInput))
    CarparkType: ApcoaCarparkTypeNameInput = DataclassValidator(ApcoaCarparkTypeNameInput)
    Address: ApcoaAdressInput = DataclassValidator(ApcoaAdressInput)
    NavigationLocations: list[ApcoaNavigationLocationsInput] = ListValidator(DataclassValidator(ApcoaNavigationLocationsInput))
    Spaces: list[ApcoaParkingSpaceInput] = ListValidator(DataclassValidator(ApcoaParkingSpaceInput))
    OpeningHours: list[ApcoaOpeningHoursInput] = ListValidator(DataclassValidator(ApcoaOpeningHoursInput))
    LastModifiedDateTime: datetime = SpacedDateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    IndicativeTariff: Optional[ApcoaIndicativeTariffInput] = Noneable(DataclassValidator(ApcoaIndicativeTariffInput))

    # TODO: ignored multiple attributes which do not matter so far

    def __post_init__(self):
        for capacity in self.Spaces:
            if capacity.Type == ApcoaParkingSpaceType.TOTAL_SPACES:
                return
        # If no capacity with type PARKING was found, we miss the capacity and therefore throw a validation error
        raise ValidationError(reason='Missing parking spaces capacity')

    def get_osm_opening_hours(self) -> str:
        apcoa_opening_times: dict = defaultdict(list)
        for opening_hours_input in self.OpeningHours:
            opening_time = opening_hours_input.OpeningTimes.replace(' ', '')
            if opening_hours_input.OpeningTimes == '00:00 - 00:00':
                apcoa_opening_times['24/7'].append(opening_time)
            if opening_hours_input.Weekday in list(ApcoaOpeningHoursWeekdays)[:5]:
                apcoa_opening_times['Mo-Fr'].append(opening_time)
            elif opening_hours_input.Weekday in list(ApcoaOpeningHoursWeekdays):
                apcoa_opening_times[opening_hours_input.Weekday.to_osm_opening_day_format()].append(opening_time)

        osm_opening_hours = ';'.join(
            [
                f'{osm_opening_day} {",".join(set(opening_hours))}'
                for osm_opening_day, opening_hours in apcoa_opening_times.items()
                if osm_opening_day != '24/7' and 'closed' not in opening_hours
            ]
        )
        if len(apcoa_opening_times['24/7']) == 7:
            osm_opening_hours = '24/7'
        return osm_opening_hours
