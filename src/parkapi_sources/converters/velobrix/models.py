"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import decimal
from datetime import datetime, timezone
from typing import Optional

from validataclass.dataclasses import validataclass
from validataclass.validators import (
    DataclassValidator,
    DateTimeValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    NumericValidator,
    StringValidator,
)

from parkapi_sources.models import StaticParkingSiteInput


@validataclass
class VelobrixBoxTypeInput:
    name: str = StringValidator()
    countLogicalBoxes: int = IntegerValidator()
    countFreeLogicalBoxes: int = IntegerValidator()


@validataclass
class VelobrixPriceModelDescriptionInput:
    description: str = StringValidator()
    validUntil: Optional[datetime] = Noneable(
        DateTimeValidator(local_timezone=timezone.utc, target_timezone=timezone.utc)
    )


@validataclass
class VelobrixInput:
    logicalUnitId: int = IntegerValidator()
    publicName: str = StringValidator()
    locationLat: decimal = NumericValidator()
    locationLon: decimal = NumericValidator()
    locationName: str = StringValidator()
    street: str = StringValidator()
    streetNumber: str = StringValidator()
    city: str = StringValidator()
    zipCode: str = StringValidator()
    tenantName: str = StringValidator()
    countLogicalBoxes: int = IntegerValidator()
    countFreeLogicalBoxes: int = IntegerValidator()

    boxTypes: list = ListValidator(DataclassValidator(VelobrixBoxTypeInput))

    priceModelDescription: str = DataclassValidator(VelobrixPriceModelDescriptionInput)

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        return None


# @validataclass
# class VelobrixRealtimeDataInput:
#     parkingupdates: list[dict] = ListValidator(AnythingValidator(allowed_types=dict))
#     updated: datetime = Rfc1123DateTimeValidator()
