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


class HeilbronnPullConverter(ParkingSitePullConverter, StaticGeojsonDataMixin, PullScraperMixin):
    source_info = SourceInfo(
        uid='heilbronn',
        name='Stadt Heilbronn',
        public_url='https://www.heilbronn.de/umwelt-mobilitaet/mobilitaet/parken.html',
        source_url='https://www.heilbronn.de/allgemeine-inhalte/ajax-parkhausbelegung?type=1496993343',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Heilbronn',
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

        realtime_data_updated_at = datetime.strptime(
            root.find('div', class_='col-sm-12').get_text().strip(),
            'Datum: %d.%m.%Y - Uhrzeit: %H:%M:%S',
        ).replace(tzinfo=ZoneInfo('Europe/Berlin'))

        return root.find_all('div', class_='carparkContent'), {'realtime_data_updated_at': realtime_data_updated_at}

    def realtime_tag_to_dict(self, tag: Tag, realtime_data_updated_at: datetime, **kwargs) -> Optional[dict]:
        # The first text is the name, followed by the access road
        name: Optional[str] = next(tag.find('div', class_='carparkLocation').stripped_strings, None)

        # The source lists unnamed and unfinished parking sites, which we ignore
        if name is None or 'nicht fertiggestellt' in name:
            return None

        # Text looks like 'Freie Parkplätze: 195', without number if there is no realtime data
        free_capacity_parts: list[str] = tag.find('div', class_='col-sm-5').get_text().split(':')
        if len(free_capacity_parts) < 2 or not free_capacity_parts[1].strip().isdigit():
            return None

        realtime_parking_site_dict: dict[str, Any] = {
            'uid': slugify(name),
            'realtime_data_updated_at': realtime_data_updated_at.isoformat(),
            'realtime_opening_status': OpeningStatus.OPEN.value,
            'realtime_free_capacity': int(free_capacity_parts[1].strip()),
        }

        return realtime_parking_site_dict
