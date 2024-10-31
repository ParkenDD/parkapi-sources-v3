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

    boxTypes: list[VelobrixBoxTypeInput] = ListValidator(DataclassValidator(VelobrixBoxTypeInput))

    priceModelDescription: VelobrixPriceModelDescriptionInput = DataclassValidator(VelobrixPriceModelDescriptionInput)

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=self.logicalUnitId,
            name=self.publicName,
            description=' ; '.join([boxType.name for boxType in self.boxTypes]),
            lat=self.locationLat,
            lon=self.locationLon,
            address=f'{self.locationName}, {self.street} {self.streetNumber}, {self.zipCode} {self.city}',
            operator_name=self.tenantName,
            capacity=self.countLogicalBoxes,
            has_realtime_data=self.countFreeLogicalBoxes is not None,
            has_fee=True,
            fee_description=self.priceModelDescription.description,
        )


# @validataclass
# class VelobrixRealtimeDataInput:
#     parkingupdates: list[dict] = ListValidator(AnythingValidator(allowed_types=dict))
#     updated: datetime = Rfc1123DateTimeValidator()
