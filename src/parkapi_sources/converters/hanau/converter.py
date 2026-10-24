"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from typing import Any, Optional
from zoneinfo import ZoneInfo

from bs4.element import Tag

from parkapi_sources.converters.base_converter.pull import (
    ParkingSitePullConverter,
    PullScraperMixin,
    StaticGeojsonDataMixin,
)
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import (
    OpeningStatus,
    PurposeType,
    RealtimeParkingSiteInput,
    SourceInfo,
    StaticParkingSiteInput,
)
from parkapi_sources.util import slugify


class HanauPullConverter(ParkingSitePullConverter, StaticGeojsonDataMixin, PullScraperMixin):
    source_info = SourceInfo(
        uid='hanau',
        name='Stadt Hanau',
        public_url='https://parken-hanau.de/',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Hanau',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_static_parking_site_inputs_and_exceptions(
            source_uid=self.source_info.uid,
            purpose=PurposeType.CAR,
        )

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_scraped_realtime_parking_site_inputs_and_exceptions()

    def get_realtime_tags_and_params(self) -> tuple[list[Tag], dict]:
        root = self.load_url_in_soup()

        container = root.find('div', class_='container-fluid')
        realtime_data_updated_at = datetime.strptime(
            container.find('h5').get_text().strip(),
            'Letzte Aktualisierung: %d.%m.%Y %H:%M:%S',
        ).replace(tzinfo=ZoneInfo('Europe/Berlin'))

        return container.find_all('div', class_='well'), {'realtime_data_updated_at': realtime_data_updated_at}

    def realtime_tag_to_dict(self, tag: Tag, realtime_data_updated_at: datetime, **kwargs) -> Optional[dict]:
        realtime_parking_site_dict: dict[str, Any] = {
            'uid': slugify(tag.find('b').get_text().strip()),
            'realtime_data_updated_at': realtime_data_updated_at.isoformat(),
            'realtime_opening_status': OpeningStatus.OPEN.value,
        }

        capacity: Optional[int] = None
        capacity_tag: Optional[Tag] = tag.find('span', class_='badge')
        if capacity_tag is not None and 'Plätze' in capacity_tag.get_text():
            capacity = int(capacity_tag.get_text().split()[0])

        # The second progress bar contains the free capacity
        progress_bars: list[Tag] = tag.find_all('div', role='progressbar')
        if len(progress_bars) < 2 or progress_bars[1].find('b') is None:
            return None
        free_capacity = int(progress_bars[1].find('b').get_text().strip())

        # Capacity zero without free capacity means that the parking site is offline
        if not capacity and not free_capacity:
            return None

        realtime_parking_site_dict['realtime_capacity'] = capacity
        realtime_parking_site_dict['realtime_free_capacity'] = free_capacity

        return realtime_parking_site_dict
