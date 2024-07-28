"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal

from validataclass.dataclasses import validataclass
from validataclass.validators import (
    DataclassValidator,
    DateTimeValidator,
    IntegerValidator,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import ParkingSiteType, RealtimeParkingSiteInput, StaticParkingSiteInput


@validataclass
class BaselCoordinates:
    lat: Decimal = NumericValidator()
    lon: Decimal = NumericValidator()


@validataclass
class BaselParkingSiteInput:
    title: str = StringValidator()
    id2: str = StringValidator()
    name: str = StringValidator()
    total: int = IntegerValidator(min_value=0)
    free: int = IntegerValidator(min_value=0)
    link: str = UrlValidator()
    geo_point_2d: BaselCoordinates = DataclassValidator(BaselCoordinates)
    published: datetime = DateTimeValidator(
        local_timezone=timezone.utc,
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=self.id2,
            name=self.name,
            lat=self.geo_point_2d.lat,
            lon=self.geo_point_2d.lon,
            capacity=self.total,
            public_url=self.link,
            static_data_updated_at=self.published,
            has_realtime_data=True,
            type=ParkingSiteType.CAR_PARK,
        )

    def to_realtime_parking_site(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id2,
            realtime_capacity=self.total,
            realtime_free_capacity=self.free,
            realtime_data_updated_at=self.published,
        )
