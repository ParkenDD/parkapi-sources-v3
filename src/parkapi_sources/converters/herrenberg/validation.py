"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum

from validataclass.dataclasses import validataclass, DefaultUnset
from validataclass.helpers import OptionalUnsetNone
from validataclass.validators import (
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models.enums import ParkingSiteType, ParkAndRideType


class HerrenbergParkingSiteType(Enum):
    Parkplatz = 'Parkplatz'
    Parkhaus = 'Parkhaus'
    Wohnmobilparkplatz = 'Wohnmobilparkplatz'
    Park_Carpool = 'Park-Carpool'
    Barrierefreier_Parkplatz = 'Barrierefreier-Parkplatz'
    Tiefgarage = 'Tiefgarage'

    def to_parking_site_input_type(self) -> ParkingSiteType:
        return {
            self.Parkplatz: ParkingSiteType.ON_STREET,
            self.Parkhaus: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.Wohnmobilparkplatz: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.Park_Carpool: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.Barrierefreier_Parkplatz: ParkingSiteType.ON_STREET,
            self.Tiefgarage: ParkingSiteType.ON_STREET
        }.get(HerrenbergParkingSiteType)

    def to_parking_site_input_ride(self) -> ParkAndRideType:
        return {
            self.Parkhaus: ParkAndRideType.YES,
            self.Park_Carpool: ParkAndRideType.CARPOOL,

        }.get(HerrenbergParkingSiteType)


class HerrenbergParkingRideType(Enum):
    Parkhaus = 'Parkhaus'
    Park_Carpool = 'Park-Carpool'


@validataclass
class HerrenbergNotesInput:
    de: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=512)), DefaultUnset
    en: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=512)), DefaultUnset


@validataclass
class HerrenbergCoordsInput:
    lat: OptionalUnsetNone[str] = NumericValidator(), DefaultUnset
    lng: OptionalUnsetNone[str] = NumericValidator(), DefaultUnset


@validataclass
class HerrenbergParkingSiteInput:
    id: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(min_length=1, max_length=256)
    lot_type: OptionalUnsetNone[HerrenbergParkingSiteType] = Noneable(
        EnumValidator(HerrenbergParkingSiteType)), DefaultUnset
    ride: OptionalUnsetNone[HerrenbergParkingSiteType] = Noneable(
        EnumValidator(HerrenbergParkingRideType)), DefaultUnset,
    total: OptionalUnsetNone[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), DefaultUnset
    url: OptionalUnsetNone[str] = Noneable(UrlValidator(max_length=4096)), DefaultUnset
    fee_hours: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=4096)), DefaultUnset
    opening_hours: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=512)), DefaultUnset
    address: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=512)), DefaultUnset
    notes: OptionalUnsetNone[HerrenbergNotesInput] = Noneable(DataclassValidator(HerrenbergNotesInput)), DefaultUnset
    coords: OptionalUnsetNone[HerrenbergCoordsInput] = Noneable(DataclassValidator(HerrenbergCoordsInput)), DefaultUnset
