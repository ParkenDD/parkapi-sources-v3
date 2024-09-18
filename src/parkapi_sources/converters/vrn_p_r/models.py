"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import IntegerValidator, NumericValidator, StringValidator

from parkapi_sources.models import RealtimeParkingSiteInput


@validataclass
class VrnParkAndRideMultiguideInput:
    Name: str = StringValidator()
    Id: int = IntegerValidator(allow_strings=True)
    Constructed: int = IntegerValidator(allow_strings=True)
    Available: int = IntegerValidator(allow_strings=True)
    Free: int = IntegerValidator(allow_strings=True)
    Occupied: int = IntegerValidator(allow_strings=True)
    Reserved: int = IntegerValidator(allow_strings=True)
    Defect: int = IntegerValidator(allow_strings=True)

    def __post_init__(self):
        if self.Constructed < self.Occupied:
            raise ValidationError(reason='More occupied sites than capacity')

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.Name,
            realtime_capacity=self.Constructed,
            realtime_free_capacity=self.Free,
            realtime_data_updated_at=datetime.now(timezone.utc),
        )


@validataclass
class VrnParkAndRideSonahInput:
    Name: str = StringValidator()
    LocationID: int = IntegerValidator()
    TotalParking: int = NumericValidator()
    FreeParking: int = NumericValidator()
    OccupiedParking: int = NumericValidator()

    def __post_init__(self):
        if self.TotalParking < self.OccupiedParking:
            raise ValidationError(reason='More occupied sites than capacity')

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.Name,
            realtime_capacity=int(self.TotalParking),
            realtime_free_capacity=int(self.FreeParking),
            realtime_data_updated_at=datetime.now(timezone.utc),
        )
