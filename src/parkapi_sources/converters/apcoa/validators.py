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
    AnythingValidator,
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


class ApcoaParkingSpaceType(Enum):
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
    URBAN_HUBS = 'Urban Hubs reserved'


class ApcoaCarparkType(Enum):
    MLCP = 'MLCP'
    OFF_STREET_OPEN = 'Off-street open'
    OFF_STREET_UNDERGROUND = 'Off-street underground'
    ON_STREET = 'On-street'
    OPEN_SURFACE = 'Open Surface'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        # TODO: find out more details about this enumeration for a proper mapping
        return {
            self.MLCP: ParkingSiteType.CAR_PARK,
            self.OFF_STREET_OPEN: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_UNDERGROUND: ParkingSiteType.UNDERGROUND,
            self.ON_STREET: ParkingSiteType.ON_STREET,
            self.OPEN_SURFACE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self, ParkingSiteType.OTHER)


class ApcoaNavigationLocationType:
    DEFAULT = 'default'
    CAR_ENTRY = 'CarEntry'


class ApcoaOpeningHoursWeekday(Enum):
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
class ApcoaParkingSitesInput:
    Results: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))


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
    Type: ApcoaParkingSpaceType = EnumValidator(ApcoaParkingSpaceType)
    Count: int = IntegerValidator(allow_strings=True)


@validataclass
class ApcoaOpeningHoursInput:
    Weekday: ApcoaOpeningHoursWeekday = EnumValidator(ApcoaOpeningHoursWeekday)
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
    NavigationLocations: list[ApcoaNavigationLocationsInput] = ListValidator(
        DataclassValidator(ApcoaNavigationLocationsInput),
    )
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
            # We check for Count < 0 here because we don't need urban hubs, and there's a lot of bad data in it
            if capacity.Type != ApcoaParkingSpaceType.URBAN_HUBS and capacity.Count < 0:
                raise ValidationError(reason=f'Invalid capacity {capacity.Count} at type {capacity.Type}')

        for capacity in self.Spaces:
            if capacity.Type == ApcoaParkingSpaceType.TOTAL_SPACES:
                return
        # If no capacity with type PARKING was found, we miss the capacity and therefore throw a validation error
        raise ValidationError(reason='Missing parking spaces capacity')

    def get_osm_opening_hours(self) -> str:
        apcoa_opening_times_by_weekday: dict[ApcoaOpeningHoursWeekday, list[str]] = defaultdict(list)
        check_counter_24_7: int = 0
        check_list_weekday: list[str] = []

        for opening_hours_input in self.OpeningHours:
            # TODO: this validator does no logic check if there are overlapping opening times

            # We don't need closed dates for OSM opening times
            if opening_hours_input.OpeningTimes == 'closed':
                continue

            # OSM has times without spaces, so we remove spaces
            opening_time = opening_hours_input.OpeningTimes.replace(' ', '').replace('-00:00', '-24:00')

            # If it's open all day, add it to our 24/7 check counter, and we change opening_time to the OSM format
            if opening_hours_input.OpeningTimes == '00:00 - 00:00':
                check_counter_24_7 += 1
                opening_time = '00:00-24:00'

            # Add opening times to fallback dict
            apcoa_opening_times_by_weekday[opening_hours_input.Weekday].append(opening_time)

            # If we have a weekday, add it to weekday lust in order to check later if all weekdays have same data
            if opening_hours_input.Weekday in list(ApcoaOpeningHoursWeekday)[:5] and opening_time != 'closed':
                check_list_weekday.append(opening_time)

        # If the check counter is 7, all weekdays are open at all time, which makes it 24/7. No further handling needed in this case.
        if check_counter_24_7 == 7:
            return '24/7'

        osm_opening_hour: list = []
        # If all Mo-Fr entries are the same, we can summarize it to the Mo-Fr entry, otherwise we have to set it separately
        if len(check_list_weekday) == 5 and len(set(check_list_weekday)) == 1:
            osm_opening_hour.append(f'Mo-Fr {check_list_weekday[0]}')
        else:
            for weekday in list(ApcoaOpeningHoursWeekday)[:5]:
                if weekday in list(apcoa_opening_times_by_weekday):
                    osm_opening_hour.append(
                        f'{weekday.to_osm_opening_day_format()} {",".join(apcoa_opening_times_by_weekday[weekday])}',
                    )

        # Weekends are handled separately anyway
        for weekend_day in [ApcoaOpeningHoursWeekday.SATURDAY, ApcoaOpeningHoursWeekday.SUNDAY]:
            if weekend_day in apcoa_opening_times_by_weekday:
                osm_opening_hour.append(
                    f'{weekend_day.to_osm_opening_day_format()} {",".join(apcoa_opening_times_by_weekday[weekend_day])}'
                )

        return '; '.join(osm_opening_hour)
