"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from zoneinfo import ZoneInfo

from shapely import GeometryType, Point
from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, EnumValidator, IntegerValidator, StringValidator, UrlValidator

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus, ParkAndRideType, ParkingSiteType, PurposeType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import ExcelNoneable, GeoJSONGeometryValidator, SpacedDateTimeValidator


@validataclass
class FreiburgPropertiesInput:
    obs_id: int = IntegerValidator(allow_strings=True)
    obs_parkid: int = IntegerValidator(allow_strings=True)
    obs_state: int = IntegerValidator(allow_strings=True)
    obs_max: int = IntegerValidator(min_value=1, allow_strings=True)
    obs_free: int = IntegerValidator(allow_strings=True)
    obs_ts: datetime = SpacedDateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    park_name: str = StringValidator()
    park_id: str = StringValidator()
    park_url: Optional[str] = ExcelNoneable(UrlValidator())


class FreiburgParkingSiteTypeInput(Enum):
    PARKPLATZ = 'Parkplatz'
    PARKHAUS = 'Parkhaus'
    TIEFGARAGE = 'Tiefgarage'
    PARKNRIDE = 'Park&Ride'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        return {
            self.PARKPLATZ: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.PARKHAUS: ParkingSiteType.CAR_PARK,
            self.TIEFGARAGE: ParkingSiteType.UNDERGROUND,
            self.PARKNRIDE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self, ParkingSiteType.OTHER)


@validataclass
class FreiburgParkAndRideStaticPropertiesInput:
    ogc_fid: int = IntegerValidator(allow_strings=True)
    name: str = StringValidator()
    nummer: str = StringValidator()
    kategorie: FreiburgParkingSiteTypeInput = EnumValidator(FreiburgParkingSiteTypeInput)
    kapazitaet: int = IntegerValidator(min_value=1, allow_strings=True)


@validataclass
class FreiburgParkAndRideRealtimePropertiesInput:
    obs_state: int = IntegerValidator(allow_strings=True)
    obs_max: int = IntegerValidator(min_value=1, allow_strings=True)
    obs_free: int = IntegerValidator(allow_strings=True)
    obs_ts: datetime = SpacedDateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    park_name: str = StringValidator()
    park_id: str = StringValidator()


@validataclass
class FreiburgBaseFeatureInput:
    def to_static_parking_site_input(self) -> StaticParkingSiteInput | None:
        return None

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput | None:
        return None


@validataclass
class FreiburgFeatureInput(FreiburgBaseFeatureInput):
    properties: FreiburgPropertiesInput = DataclassValidator(FreiburgPropertiesInput)

    def extend_static_parking_site_input(self, static_parking_site_input: StaticParkingSiteInput):
        static_parking_site_input.capacity = self.properties.obs_max
        static_parking_site_input.public_url = self.properties.park_url

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=str(self.properties.obs_parkid),
            realtime_capacity=self.properties.obs_max,
            realtime_free_capacity=self.properties.obs_free,
            realtime_data_updated_at=self.properties.obs_ts,
            realtime_opening_status=OpeningStatus.OPEN if self.properties.obs_state == 1 else OpeningStatus.CLOSED,
        )


@validataclass
class FreiburgParkAndRideStaticFeatureInput(FreiburgBaseFeatureInput):
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])
    properties: FreiburgParkAndRideStaticPropertiesInput = DataclassValidator(FreiburgParkAndRideStaticPropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        if self.properties.nummer:
            name = f'{self.properties.name} ({self.properties.nummer})'
        else:
            name = f'{self.properties.name}'
        return StaticParkingSiteInput(
            uid=str(self.properties.ogc_fid),
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            name=name,
            capacity=self.properties.kapazitaet,
            type=self.properties.kategorie.to_parking_site_type_input(),
            static_data_updated_at=datetime.now(tz=timezone.utc),
            park_and_ride_type=[ParkAndRideType.YES],
            has_realtime_data=False,
        )


@validataclass
class FreiburgParkAndRideRealtimeFeatureInput(FreiburgBaseFeatureInput):
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])
    properties: FreiburgParkAndRideRealtimePropertiesInput = DataclassValidator(
        FreiburgParkAndRideRealtimePropertiesInput
    )

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.properties.park_id),
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            name=self.properties.park_name,
            capacity=self.properties.obs_max,
            type=ParkingSiteType.OFF_STREET_PARKING_GROUND,
            purpose=PurposeType.CAR,
            park_and_ride_type=[ParkAndRideType.YES],
            static_data_updated_at=self.properties.obs_ts,
            has_realtime_data=True,
        )

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=str(self.properties.park_id),
            realtime_capacity=self.properties.obs_max,
            realtime_free_capacity=self.properties.obs_free,
            realtime_data_updated_at=self.properties.obs_ts,
            realtime_opening_status=OpeningStatus.OPEN if self.properties.obs_state >= 0 else OpeningStatus.CLOSED,
        )
