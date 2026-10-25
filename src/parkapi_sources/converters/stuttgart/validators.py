"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal

from validataclass.dataclasses import validataclass
from validataclass.validators import (
    DataclassValidator,
    DecimalValidator,
)

from parkapi_sources.converters.base_converter.datex2 import ParkingFacility


@validataclass
class StuttgartLocationForDisplay:
    latitude: Decimal = DecimalValidator(min_value=5000000, max_value=6000000)
    longitude: Decimal = DecimalValidator(min_value=500000, max_value=600000)


@validataclass
class StuttgartFacilityLocation:
    locationForDisplay: StuttgartLocationForDisplay = DataclassValidator(StuttgartLocationForDisplay)

    @property
    def coordinates(self) -> StuttgartLocationForDisplay:
        return self.locationForDisplay


@validataclass
class StuttgartParkingFacility(ParkingFacility):
    facilityLocation: StuttgartFacilityLocation = DataclassValidator(StuttgartFacilityLocation)
