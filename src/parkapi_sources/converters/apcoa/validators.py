"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from enum import Enum
from typing import Optional

from validataclass.dataclasses import Default, validataclass
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


class ApcoaParkingSiteType(Enum):
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


class ApcoaParkingPurpose:
    CAR = 'CAR'
    BIKE = 'BIKE'
    ITEM = 'ITEM'


class NavigationLocationType:
    DEFAULT = 'default'
    CAR_ENTRY = 'CarEntry'


class OpeningHoursWeekdays:
    Weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    OpeningTime = '00:00 - 00:00'


@validataclass
class ApcoaIdInput:
    CarParkId: int = IntegerValidator(allow_strings=True)


@validataclass
class ApcoaNameInput:
    CarparkLongName: str = StringValidator()
    CarparkShortName: str = StringValidator()


@validataclass
class ApcoaTypeNameInput:
    Name: ApcoaParkingSiteType = EnumValidator(ApcoaParkingSiteType)


@validataclass
class ApcoaTypeInput:
    CarparkType: ApcoaTypeNameInput = DataclassValidator(ApcoaTypeNameInput)


@validataclass
class ApcoaLocationGeocoordinatesInput:
    Longitude: Decimal = NumericValidator()
    Latitude: Decimal = NumericValidator()


@validataclass
class ApcoaNavigationLocationsInput:
    Geocoordinates: ApcoaLocationGeocoordinatesInput = DataclassValidator(ApcoaLocationGeocoordinatesInput)
    LocationType: NavigationLocationType = EnumValidator(NavigationLocationType)


@validataclass
class ApcoaAdressInput:
    Street: str = StringValidator()
    Zip: str = StringValidator()
    City: str = StringValidator()
    Region: Optional[str] = Noneable(StringValidator())
    NavigationLocations: list[ApcoaNavigationLocationsInput] = ListValidator(DataclassValidator(ApcoaNavigationLocationsInput))


@validataclass
class ApcoaParkingSpaceInput:
    Type: ApcoaParkingSpaceType = EnumValidator(ApcoaParkingSpaceType)
    Count: int = IntegerValidator(allow_strings=True, min_value=0)


@validataclass
class ApcoaSpacesInput:
    Spaces: list[ApcoaParkingSpaceInput] = ListValidator(ApcoaParkingSpaceInput)


@validataclass
class ApcoaOpeningHoursWeekdayInput:
    Weekday: str = StringValidator()
    OpeningTimes: str = StringValidator()


@validataclass
class ApcoaOpeningHoursInput:
    OpeningHours: list[ApcoaOpeningHoursWeekdayInput] = ListValidator(ApcoaOpeningHoursWeekdayInput)


@validataclass
class ApcoaParkingSiteInput:
    id: ApcoaIdInput = DataclassValidator(ApcoaIdInput)
    name: ApcoaNameInput = DataclassValidator(ApcoaNameInput)
    url: Optional[str] = UrlValidator(), Default(None)
    type: ApcoaTypeInput = DataclassValidator(ApcoaTypeInput)
    purpose: ApcoaParkingPurpose = EnumValidator(ApcoaParkingPurpose)
    address: ApcoaAdressInput = DataclassValidator(ApcoaAdressInput)
    capacity: ApcoaSpacesInput = DataclassValidator(ApcoaSpacesInput)
    opening_hours: ApcoaOpeningHoursInput = DataclassValidator(ApcoaOpeningHoursInput)
    # TODO: ignored multiple attributes which do not matter so far

    def __post_init__(self):
        for capacity in self.capacity:
            if capacity.Type == ApcoaParkingSpaceType.TOTAL_SPACES:
                return
        # If no capacity with type PARKING was found, we miss the capacity and therefore throw a validation error
        raise ValidationError(reason='Missing parking spaces capacity')
