"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse
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


class DresdenPullConverter(ParkingSitePullConverter, StaticGeojsonDataMixin, PullScraperMixin):
    source_info = SourceInfo(
        uid='dresden',
        name='Landeshauptstadt Dresden',
        public_url='https://www.dresden.de/parken',
        source_url='https://www.dresden.de/apps_ext/ParkplatzApp/',
        timezone='Europe/Berlin',
        attribution_contributor='Landeshauptstadt Dresden',
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
        root = self.load_url_in_soup(self.source_info.source_url)

        realtime_data_updated_at: Optional[datetime] = None
        for headline in root.find_all('h3'):
            if headline.get_text().strip() == 'Letzte Aktualisierung':
                realtime_data_updated_at = datetime.strptime(
                    headline.find_next_sibling('div').get_text().strip(),
                    '%d.%m.%Y %H:%M:%S',
                ).replace(tzinfo=ZoneInfo('Europe/Berlin'))

        tags: list[Tag] = []
        for table in root.find_all('table'):
            if table.find('thead') is None:
                continue
            tags += table.find('tbody').find_all('tr')

        return tags, {'realtime_data_updated_at': realtime_data_updated_at}

    def realtime_tag_to_dict(self, tag: Tag, realtime_data_updated_at: datetime, **kwargs) -> Optional[dict]:
        cells: list[Tag] = tag.find_all('td')
        detail_url: str = tag.find('a').attrs.get('href')

        realtime_parking_site_dict: dict[str, Any] = {
            'uid': parse_qs(urlparse(detail_url).query)['id'][0],
            'realtime_data_updated_at': realtime_data_updated_at.isoformat(),
        }

        capacity: str = cells[2].find('div', class_='content').get_text().strip()
        free_capacity: str = cells[3].find('div', class_='content').get_text().strip()

        if 'park-closed' in cells[0].attrs.get('class', []):
            realtime_parking_site_dict['realtime_opening_status'] = OpeningStatus.CLOSED.value
        elif free_capacity == '':
            # Blue icon without numbers means that there is no realtime data available
            return None
        else:
            realtime_parking_site_dict['realtime_opening_status'] = OpeningStatus.OPEN.value

        if capacity.isdigit() and int(capacity) > 0:
            realtime_parking_site_dict['realtime_capacity'] = int(capacity)
        if free_capacity.isdigit():
            realtime_parking_site_dict['realtime_free_capacity'] = int(free_capacity)

        return realtime_parking_site_dict
