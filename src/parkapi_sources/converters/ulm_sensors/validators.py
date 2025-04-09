"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.dataclasses import validataclass, Default
from validataclass.validators import (
    AnyOfValidator,
    AnythingValidator,
    BooleanValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    DateTimeValidator,
    StringValidator,
    UrlValidator,
    Noneable,
)

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo
from decimal import Decimal

from parkapi_sources.models import (
    ExcelOpeningTimeInput,
    ExcelStaticParkingSiteInput,
    RealtimeParkingSiteInput,
    SourceInfo,
    StaticParkingSiteInput,
)

from parkapi_sources.models import ParkingRestrictionInput, RealtimeParkingSpotInput, StaticParkingSpotInput
from parkapi_sources.models.enums import ParkingSpotStatus, PurposeType

@validataclass
class UlmSensorsParkingSiteInput:
    # As Friedrichshafen uses a parking site model for parking spots, we have to ensure that the capacity is always 1
    id: str = StringValidator(min_length=1, max_length=256)
    maxcarparkfull: int | None = Noneable(IntegerValidator(allow_strings=True)), Default(None)
    maxcarparkfullwithreservation: int | None = Noneable(IntegerValidator(allow_strings=True)), Default(None)
    currentcarparkfulltotal: int | None = Noneable(IntegerValidator(allow_strings=True)), Default(None)
    currentcarparkfullwithoutreservation: int | None = Noneable(IntegerValidator(allow_strings=True)), Default(None)
    currentcarparkfullwithreservation: int | None = Noneable(IntegerValidator(allow_strings=True)), Default(None)
    currentshorttermparker: int | None = Noneable(IntegerValidator(allow_strings=True)), Default(None)
    timestamp: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=str(self.id),
            realtime_capacity=self.maxcarparkfull,
            realtime_free_capacity=self.currentcarparkfulltotal,
            realtime_data_updated_at=self.timestamp,
        )


@validataclass
class UlmSensorsParkingSpotInput:
    # As Friedrichshafen uses a parking site model for parking spots, we have to ensure that the capacity is always 1
    uid: str = StringValidator(min_length=1, max_length=256)
    name: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    purpose: PurposeType = EnumValidator(PurposeType), Default(PurposeType.CAR)
    has_realtime_data: bool = BooleanValidator()
    restricted_to: list[ParkingRestrictionInput] | None = (
        Noneable(ListValidator(DataclassValidator(ParkingRestrictionInput))),
        Default(None),
    )

    def to_static_parking_spot_input(self) -> StaticParkingSpotInput:
        
        restricted_to: list[ParkingRestrictionInput] = []
        if self.assignedParkingAmongOthers:
            for user in self.assignedParkingAmongOthers.applicableForUser:
                restricted_to.append(ParkingRestrictionInput(type=user.to_parking_audience()))

        return StaticParkingSpotInput(
            uid=self.id,
            name=self.name,
            purpose=PurposeType.CAR,
            has_realtime_data=True,
            lat=self.parkingLocation.pointByCoordinates.pointCoordinates.latitude,
            lon=self.parkingLocation.pointByCoordinates.pointCoordinates.longitude,
            static_data_updated_at=self.parkingRecordVersionTime,
            restricted_to=restricted_to if len(restricted_to) else None,
        )
    
    def to_realtime_parking_spot_input(self) -> RealtimeParkingSpotInput:
        if self.parkingOccupancy.parkingNumberOfVacantSpaces:
            realtime_status = ParkingSpotStatus.AVAILABLE
        else:
            realtime_status = ParkingSpotStatus.TAKEN

        return RealtimeParkingSpotInput(
            uid=self.parkingRecordReference.id.split('[')[0],
            realtime_data_updated_at=self.parkingStatusOriginTime,
            realtime_status=realtime_status,
        )
