"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum

from shapely import GeometryType, Point
from validataclass.dataclasses import validataclass
from validataclass.validators import (
    AnythingValidator,
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import (
    GeojsonBaseFeatureInput,
    ParkingAudience,
    ParkingSpotRestrictionInput,
    ParkingSpotStatus,
    RealtimeParkingSpotInput,
    StaticParkingSpotInput,
)
from parkapi_sources.util import generate_point, round_7d
from parkapi_sources.validators import CommaSeparatedListValidator, GeoJSONGeometryValidator


class ParkingStatus(Enum):
    AVAILABLE = 0
    TAKEN = 1

    def to_realtime_status(self) -> ParkingSpotStatus:
        return {
            self.AVAILABLE: ParkingSpotStatus.AVAILABLE,
            self.TAKEN: ParkingSpotStatus.TAKEN,
        }.get(self)


@validataclass
class KarlsruheDisabledPropertiesInput:
    id: int = IntegerValidator()
    gemeinde: str = StringValidator()
    stadtteil: str | None = Noneable(StringValidator())
    standort: str = StringValidator()
    parkzeit: str | None = Noneable(StringValidator())
    max_parkdauer: str | None = Noneable(StringValidator())
    stellplaetze: int = IntegerValidator()
    bemerkung: str | None = Noneable(StringValidator())
    sensorenliste: list[str] | None = Noneable(CommaSeparatedListValidator(StringValidator()))
    stand: datetime = DateTimeValidator()


@validataclass
class KarlsruheDisabledFeatureInput(GeojsonBaseFeatureInput):
    properties: KarlsruheDisabledPropertiesInput = DataclassValidator(KarlsruheDisabledPropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])

    def to_static_parking_spot_inputs(self) -> list[StaticParkingSpotInput]:
        static_parking_spot_inputs = []

        descriptions: list[str] = [
            self.properties.parkzeit,
            self.properties.parkzeit,
            self.properties.bemerkung,
        ]
        name = self.properties.standort
        if self.properties.stadtteil:
            name = f'{name}, {self.properties.stadtteil}'
        name = f'{name}, {self.properties.gemeinde}'

        for i in range(self.properties.stellplaetze):
            lat, lon = generate_point(
                lat=round_7d(self.geometry.y),
                lon=round_7d(self.geometry.x),
                number=i,
                max_number=self.properties.stellplaetze,
            )

            if self.properties.stellplaetze > 1:
                item_name = f'{name} ({i + 1} / {self.properties.stellplaetze})'
            else:
                item_name = name

            static_parking_spot_inputs.append(
                StaticParkingSpotInput(
                    uid=f'{self.properties.id}_{i}',
                    name=item_name,
                    address=f'{self.properties.standort}, {self.properties.gemeinde}',
                    static_data_updated_at=self.properties.stand,
                    description=', '.join(description for description in descriptions if description),
                    lat=lat,
                    lon=lon,
                    has_realtime_data=False,
                    restrictions=[ParkingSpotRestrictionInput(type=ParkingAudience.DISABLED)],
                ),
            )

        return static_parking_spot_inputs


@validataclass
class KarlsruheDisabledRealtimeDataInput:
    parking_status: ParkingStatus = EnumValidator(ParkingStatus)


@validataclass
class KarlsruheDisabledRealtimeReadingInput:
    data: KarlsruheDisabledRealtimeDataInput = DataclassValidator(KarlsruheDisabledRealtimeDataInput)
    measured_at: datetime = DateTimeValidator(
        local_timezone=timezone.utc,
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )


@validataclass
class KarlsruheDisabledRealtimeItemInput:
    id: str = StringValidator()
    last_readings: list[KarlsruheDisabledRealtimeReadingInput] = ListValidator(
        DataclassValidator(KarlsruheDisabledRealtimeReadingInput), min_length=1
    )

    def to_realtime_parking_spot_input(self, parking_spot_uid: str) -> RealtimeParkingSpotInput:
        return RealtimeParkingSpotInput(
            uid=parking_spot_uid,
            realtime_status=self.last_readings[0].data.parking_status.to_realtime_status(),
            realtime_data_updated_at=self.last_readings[0].measured_at,
        )


@validataclass
class KarlsruheDisabledRealtimeInput:
    body: list[dict] = ListValidator(AnythingValidator(allowed_types=dict), min_length=1)
