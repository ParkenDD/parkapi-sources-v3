"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup
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


class ZuerichPullConverter(ParkingSitePullConverter, StaticGeojsonDataMixin, PullScraperMixin):
    source_info = SourceInfo(
        uid='zuerich',
        name='Parkleitsystem Stadt Zürich',
        public_url='https://data.stadt-zuerich.ch/dataset/parkleitsystem',
        source_url='https://www.pls-zh.ch/plsFeed/rss',
        timezone='Europe/Zurich',
        attribution_contributor='PLS Parkleitsystem Zürich AG',
        attribution_license='Creative-Commons-Null-Lizenz (CC-0)',
        attribution_url='https://www.pls-zh.ch/impressum.jsp',
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
        response = self.request_get(url=self.source_info.source_url)
        root = BeautifulSoup(response.text, features='xml')

        return root.find_all('item'), {}

    def realtime_tag_to_dict(self, tag: Tag, **kwargs) -> Optional[dict]:
        # Description looks like 'open /   41', or '???? / ???' if there is no realtime data
        status, free_capacity = (part.strip() for part in tag.find('description').get_text().split('/'))

        if status == 'open':
            opening_status = OpeningStatus.OPEN
        elif status == 'closed':
            opening_status = OpeningStatus.CLOSED
        else:
            return None

        realtime_parking_site_dict: dict[str, Any] = {
            'uid': parse_qs(urlparse(tag.find('link').get_text().strip()).query)['pid'][0],
            'realtime_data_updated_at': tag.find('dc:date').get_text().strip(),
            'realtime_opening_status': opening_status.value,
        }
        if free_capacity.isdigit():
            realtime_parking_site_dict['realtime_free_capacity'] = int(free_capacity)

        return realtime_parking_site_dict
