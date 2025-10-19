"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, time
from enum import Enum
from typing import Any

import pyproj
from isodate import Duration
from shapely import GeometryType, LineString
from validataclass.dataclasses import validataclass
from validataclass.validators import (
    AnyOfValidator,
    BooleanValidator,
    DataclassValidator,
    EnumValidator,
    FloatValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
    TimeFormat,
    TimeValidator,
)

from parkapi_sources.models import (
    ParkingAudience,
    ParkingSiteRestrictionInput,
    StaticParkingSiteInput,
)
from parkapi_sources.models.enums import (
    ParkAndRideType,
    ParkingSiteOrientation,
    ParkingSiteType,
    ParkingType,
)
from parkapi_sources.util import round_7d
from parkapi_sources.validators import (
    GeoJSONGeometryValidator,
    IsoDurationValidator,
    ReplacingStringValidator,
)


class RadolfzellDurationValidator(IsoDurationValidator):
    def validate(self, value: Any, **kwargs) -> Duration:
        self._ensure_type(value, [str])
        if value.endswith(' Std'):
            value = f'PT{value[:-4]}H'
        if value.endswith(' min'):
            value = f'PT{value[:-4]}M'

        return super().validate(value, **kwargs)


class RadolfzellOrientation(Enum):
    PARALLEL = 1
    PERPENDICULAR = 2
    DIAGONAL = 3

    def to_parking_side_orientation(self) -> ParkingSiteOrientation:
        return {
            self.PARALLEL: ParkingSiteOrientation.PARALLEL,
            self.DIAGONAL: ParkingSiteOrientation.DIAGONAL,
            self.PERPENDICULAR: ParkingSiteOrientation.PERPENDICULAR,
        }.get(self)


class RadolfzellProperty(Enum):
    FORBIDDEN = 1
    BIKE_LANE = 2
    TRAFFIC_CALMED = 3
    PARKING_IN_MARKED_AREAS = 4
    NO_PARKING_RULES = 5
    ON_KERB = 6
    PARKING_DISC_PERMANENT = 7
    PARKING_DISC = 8
    PARKING_DISC_4_HOURS = 9
    PARKING_DISC_24_HOURS = 10
    RESIDENT_PARKING = 11
    SHORT_PARKING = 12
    PARKING_DISC_1_HOUR = 13
    FORBIDDEN_TOO_NARROW = 14


KEY_MAPPING = {
    '24/7 geöf': 'is_24_7',
    'Gebü Info': 'fee_description',
    'Längengra': 'lon',
    'Breitengrd': 'lat',
    'Max Dauer': 'max_stay',
    'Max Höh c': 'max_height',
    'Özeit MF1': 'opening_times_weekday_begin',
    'Özeit MF2': 'opening_times_weekday_end',
    'Özeit Sa1': 'opening_times_saturday_begin',
    'Özeit Sa2': 'opening_times_saturday_end',
    'Özeit So1': 'opening_times_sunday_begin',
    'Özeit So2': 'opening_times_sunday_end',
    'P+R': 'park_and_ride',
    'Weite Info': 'more_info',
}


@validataclass
class RadolfzellPropertiesInput:
    is_24_7: bool = BooleanValidator()
    Art_Anlage: str | None = Noneable(StringValidator())
    Behindstlp: int | None = Noneable(IntegerValidator())
    Beleucht: bool = BooleanValidator()
    lon: float = FloatValidator()
    Carsharing: int | None = Noneable(IntegerValidator())
    gebpflicht: bool | None = Noneable(BooleanValidator())
    fee_description: str | None = Noneable(StringValidator())
    Ladeplatz: int | None = Noneable(IntegerValidator())
    lat: float = FloatValidator()
    max_stay: Duration | None = Noneable(RadolfzellDurationValidator())
    max_height: int | None = Noneable(IntegerValidator())
    opening_times_weekday_begin: time | None = Noneable(TimeValidator(time_format=TimeFormat.NO_SECONDS))
    opening_times_weekday_end: time | None = Noneable(TimeValidator(time_format=TimeFormat.NO_SECONDS))
    opening_times_saturday_begin: time | None = Noneable(TimeValidator(time_format=TimeFormat.NO_SECONDS))
    opening_times_saturday_end: time | None = Noneable(TimeValidator(time_format=TimeFormat.NO_SECONDS))
    opening_times_sunday_begin: time | None = Noneable(TimeValidator(time_format=TimeFormat.NO_SECONDS))
    opening_times_sunday_end: time | None = Noneable(TimeValidator(time_format=TimeFormat.NO_SECONDS))
    park_and_ride: str | None = Noneable(StringValidator())
    Regel_Txt: str | None = Noneable(StringValidator())
    Regelung: RadolfzellProperty | None = Noneable(EnumValidator(RadolfzellProperty))
    Richtung: RadolfzellOrientation | None = Noneable(EnumValidator(RadolfzellOrientation))
    Stellpl: int = IntegerValidator()
    StrPLZOrt2: str | None = Noneable(ReplacingStringValidator(mapping={'\n': ', '}))
    more_info: str | None = Noneable(StringValidator())

    @staticmethod
    def __pre_validate__(input_data: Any, **kwargs):
        result: dict[str, Any] = {}
        for key, value in input_data.items():
            key = KEY_MAPPING.get(key, key)

            # Fix broken opening times time values
            if key.startswith('opening_times_') and value and len(value) == 4:
                value = f'0{value}'

            result[key] = value

        return result


@validataclass
class RadolfzellParkingSiteInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: RadolfzellPropertiesInput = DataclassValidator(RadolfzellPropertiesInput)
    geometry: LineString = GeoJSONGeometryValidator(
        allowed_geometry_types=[GeometryType.MULTILINESTRING, GeometryType.LINESTRING],
    )

    def to_static_parking_site(
        self,
        static_data_updated_at: datetime,
        proj: pyproj.Proj,
    ) -> StaticParkingSiteInput | None:
        if self.properties.Regelung in [RadolfzellProperty.FORBIDDEN, RadolfzellProperty.FORBIDDEN_TOO_NARROW]:
            return None

        coordinates = proj(
            float(self.properties.lon),
            float(self.properties.lat),
            inverse=True,
        )

        descriptions: list[str] = [
            self.properties.Regel_Txt,
            self.properties.more_info,
        ]

        static_parking_site_input = StaticParkingSiteInput(
            uid=f'{self.properties.lat}_{self.properties.lon}',
            name=self.properties.StrPLZOrt2 or 'Parkplatz',
            address=self.properties.StrPLZOrt2,
            static_data_updated_at=static_data_updated_at,
            type=ParkingSiteType.ON_STREET,
            lat=round_7d(coordinates[1]),
            lon=round_7d(coordinates[0]),
            capacity=self.properties.Stellpl,
            geojson=self.geometry,
            has_realtime_data=False,
            has_lighting=self.properties.Beleucht,
            has_fee=self.properties.gebpflicht,
            fee_description=self.properties.fee_description,
            max_height=self.properties.max_height,
            description=', '.join(description for description in descriptions if description),
            restrictions=[],
        )

        if self.properties.Behindstlp is not None:
            static_parking_site_input.restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.DISABLED,
                    capacity=self.properties.Behindstlp,
                ),
            )
        if self.properties.Ladeplatz is not None:
            static_parking_site_input.restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                    capacity=self.properties.Ladeplatz,
                ),
            )
        if self.properties.Carsharing is not None:
            static_parking_site_input.restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CARSHARING,
                    capacity=self.properties.Carsharing,
                ),
            )

        if self.properties.max_stay:
            static_parking_site_input.max_stay = int(self.properties.max_stay.total_seconds()) // 60

        if self.properties.Richtung:
            static_parking_site_input.orientation = self.properties.Richtung.to_parking_side_orientation()

        if self.properties.Art_Anlage == 'Parkplatz':
            static_parking_site_input.type = ParkingSiteType.OFF_STREET_PARKING_GROUND

        if self.properties.park_and_ride:
            static_parking_site_input.park_and_ride_type = [ParkAndRideType.YES]

        if self.properties.is_24_7:
            static_parking_site_input.opening_hours = '24/7'
        else:
            opening_hour_fragments = []
            for timeframe, osm_output in [('weekday', 'Mo-Fr'), ('saturday', 'Sa'), ('sunday', 'Su')]:
                begin: time | None = getattr(self.properties, f'opening_times_{timeframe}_begin')
                end: time | None = getattr(self.properties, f'opening_times_{timeframe}_end')
                if begin is not None and end is not None and begin < end:
                    opening_hour_fragments.append(f'{osm_output} {begin.strftime("%H:%M")}-{end.strftime("%H:%M")}')

            if len(opening_hour_fragments):
                # Catch situation where all opening times are equal
                if all(x[-11:] == opening_hour_fragments[0][-11:] for x in opening_hour_fragments):
                    opening_hour_fragments = [
                        f'Mo-Su {self.properties.opening_times_saturday_begin.strftime("%H:%M")}'
                        f'-{self.properties.opening_times_saturday_end.strftime("%H:%M")}'
                    ]
                static_parking_site_input.opening_hours = '; '.join(opening_hour_fragments)

        if self.properties.Regelung == RadolfzellProperty.ON_KERB:
            static_parking_site_input.parking_type = ParkingType.ON_KERB
        elif self.properties.Regelung == RadolfzellProperty.RESIDENT_PARKING:
            static_parking_site_input.restrictions = [ParkingSiteRestrictionInput(type=ParkingAudience.RESIDENT)]

        return static_parking_site_input
