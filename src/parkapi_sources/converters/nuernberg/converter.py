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


class NuernbergPullConverter(ParkingSitePullConverter, StaticGeojsonDataMixin, PullScraperMixin):
    source_info = SourceInfo(
        uid='nuernberg',
        name='Stadt Nürnberg',
        public_url='https://tiefbauamt.nuernberg.de/site/parken/parkhausbelegung/parkhaus_belegung.html',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Nürnberg',
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

        realtime_data_updated_at = datetime.strptime(
            root.find('td', width='233').get_text().strip(),
            'Stand vom %d.%m.%Y, %H:%M:%S',
        ).replace(tzinfo=ZoneInfo('Europe/Berlin'))

        # Each parking site is a table row with its name in a bold paragraph
        rows: list[Tag] = [paragraph.find_parent('tr') for paragraph in root.find_all('p', class_='bold')]

        return rows, {'realtime_data_updated_at': realtime_data_updated_at}

    def realtime_tag_to_dict(self, tag: Tag, realtime_data_updated_at: datetime, **kwargs) -> Optional[dict]:
        cells: list[Tag] = tag.find_all('td')

        free_capacity: str = cells[2].get_text().strip()
        capacity: str = cells[3].get_text().strip()
        if not free_capacity.isdigit():
            return None

        realtime_parking_site_dict: dict[str, Any] = {
            # Names contain line breaks and indentation
            'uid': slugify(' '.join(cells[1].get_text().split())),
            'realtime_data_updated_at': realtime_data_updated_at.isoformat(),
            'realtime_opening_status': OpeningStatus.OPEN.value,
            'realtime_free_capacity': int(free_capacity),
        }
        if capacity.isdigit():
            realtime_parking_site_dict['realtime_capacity'] = int(capacity)

        return realtime_parking_site_dict
