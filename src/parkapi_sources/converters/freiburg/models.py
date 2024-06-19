"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, IntegerValidator, StringValidator, UrlValidator

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus
from parkapi_sources.validators import ExcelNoneable, SpacedDateTimeValidator


@validataclass
class FreiburgPropertiesInput:
    obs_id: int = IntegerValidator(allow_strings=True)
    obs_parkid: int = IntegerValidator(allow_strings=True)
    obs_state: int = IntegerValidator(allow_strings=True)
    obs_max: int = IntegerValidator(allow_strings=True)
    obs_free: int = IntegerValidator(allow_strings=True)
    obs_ts: datetime = SpacedDateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    park_name: str = StringValidator()
    park_id: str = StringValidator()
    park_url: Optional[str] = ExcelNoneable(UrlValidator())


@validataclass
class FreiburgFeatureInput:
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
            realtime_opening_status=OpeningStatus.OPEN if self.properties.obs_state else OpeningStatus.CLOSED,
        )
