"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any, Optional

from bs4.element import PageElement, Tag

from parkapi_sources.converters.base_converter.pull import PullConverter, PullScraperMixin, StaticGeojsonDataMixin
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput


class UlmPullConverter(PullConverter, StaticGeojsonDataMixin, PullScraperMixin):
    source_info = SourceInfo(
        uid='ulm',
        name='Stadt Ulm',
        public_url='https://www.parken-in-ulm.de',
        timezone='Europe/Berlin',
        attribution_contributor='Ulmer Parkbetriebs-GmbH',
        attribution_url='https://www.parken-in-ulm.de/impressum.php',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_static_parking_site_inputs_and_exceptions(source_uid=self.source_info.uid)

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_scraped_realtime_parking_site_inputs_and_exceptions()

    def get_realtime_tags_and_params(self) -> tuple[list[Tag], dict]:
        root = self.load_url_in_soup()

        section = root.find('section', class_='s_live_counter')
        return section.find_all('div', class_='card-container'), {}

    def realtime_tag_to_dict(self, tag: Tag, **kwargs) -> Optional[dict]:
        realtime_parking_site_dict: dict[str, Any] = {
            'realtime_data_updated_at': datetime.now(tz=timezone.utc).isoformat(),
            'uid': tag.find('a', class_='stretched-link').attrs.get('href').split('/')[-1],
        }

        parking_data_box: list[PageElement] = list(tag.find('div', class_='counter-text').find('p'))
        if len(parking_data_box) == 0:
            return None

        parking_data: list[str] = parking_data_box[0].get_text().strip().split(' / ')
        realtime_parking_site_dict['realtime_capacity'] = int(parking_data[1])
        if parking_data[0].strip() == '?':
            realtime_parking_site_dict['realtime_free_capacity'] = None
        else:
            realtime_parking_site_dict['realtime_free_capacity'] = int(parking_data[0])

        return realtime_parking_site_dict
