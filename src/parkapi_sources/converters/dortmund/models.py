"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import DataclassValidator, Noneable

from parkapi_sources.converters.base_converter.datex2 import ParkingFacility
from parkapi_sources.converters.base_converter.datex2.parking_facility_validator import Owner


@validataclass
class DortmundParkingFacility(ParkingFacility):
    # Dortmund publishes empty owner elements, which are not valid DATEX II. They are treated as missing owner.
    owner: Owner | None = Noneable(DataclassValidator(Owner)), Default(None)
