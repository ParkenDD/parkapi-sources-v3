"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    BooleanValidator,
    DateTimeValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import (
    ParkingRestrictionInput,
    ParkingSpotRestrictionInput,
    ParkingSiteRestrictionInput,
    RealtimeParkingSiteInput,
    RealtimeParkingSpotInput,
    StaticParkingSpotInput,
    StaticParkingSiteInput,
)
from parkapi_sources.models.enums import ParkingSpotStatus


@validataclass
class UlmSensorsParkingSiteInput:
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

    def extend_static_parking_site_input(self, static_parking_site_input: StaticParkingSiteInput):
        parking_site_restrictions: list[ParkingSiteRestrictionInput] = []
        for restrictions in static_parking_site_input.restrictions or []:
            if isinstance(restrictions, ParkingSiteRestrictionInput):
                parking_site_restrictions.append(restrictions)

            elif isinstance(restrictions, ParkingRestrictionInput):
                parking_site_restrictions.append(
                    ParkingSiteRestrictionInput(
                        type=restrictions.type,
                        hours=restrictions.hours,
                        max_stay=restrictions.max_stay,
                    )
                )

            elif isinstance(restrictions, dict):
                parking_site_restrictions.append(
                    ParkingSiteRestrictionInput(
                        type=restrictions.get('type'),
                        hours=restrictions.get('hours'),
                        max_stay=restrictions.get('max_stay'),
                    )
                )

        static_parking_site_input.restrictions = parking_site_restrictions
        return static_parking_site_input

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id,
            realtime_capacity=self.maxcarparkfull,
            realtime_free_capacity=self.maxcarparkfull - self.currentcarparkfulltotal
            if self.maxcarparkfull and self.currentcarparkfulltotal
            else None,
            realtime_data_updated_at=self.timestamp,
        )


@validataclass
class UlmSensorsParkingSpotInput:
    id: str = StringValidator(min_length=1, max_length=256)
    occupied: bool = BooleanValidator()
    timestamp: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )

    def extend_static_parking_spot_input(self, static_parking_spot_input: StaticParkingSpotInput):
        parking_spot_restrictions: list[ParkingSpotRestrictionInput] = []
        for restrictions in static_parking_spot_input.restrictions or []:
            if isinstance(restrictions, ParkingSpotRestrictionInput):
                parking_spot_restrictions.append(restrictions)

            elif isinstance(restrictions, ParkingRestrictionInput):
                parking_spot_restrictions.append(
                    ParkingSpotRestrictionInput(
                        type=restrictions.type,
                        hours=restrictions.hours,
                        max_stay=restrictions.max_stay,
                    )
                )

            elif isinstance(restrictions, dict):
                parking_spot_restrictions.append(
                    ParkingSpotRestrictionInput(
                        type=restrictions.get('type'),
                        hours=restrictions.get('hours'),
                        max_stay=restrictions.get('max_stay'),
                    )
                )

        static_parking_spot_input.restrictions = parking_spot_restrictions
        return static_parking_spot_input

    def to_realtime_parking_spot_input(self) -> RealtimeParkingSpotInput:
        if self.occupied:
            realtime_status = ParkingSpotStatus.TAKEN
        else:
            realtime_status = ParkingSpotStatus.AVAILABLE

        return RealtimeParkingSpotInput(
            uid=self.id,
            realtime_data_updated_at=self.timestamp,
            realtime_status=realtime_status,
        )
