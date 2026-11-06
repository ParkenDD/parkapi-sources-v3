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


class MagdeburgPullConverter(ParkingSitePullConverter, StaticGeojsonDataMixin, PullScraperMixin):
    source_info = SourceInfo(
        uid='magdeburg',
        name='Landeshauptstadt Magdeburg',
        public_url='https://www.movi.de/parkinfo/uebersicht.shtml',
        timezone='Europe/Berlin',
        attribution_contributor='ifak e.V. Magdeburg',
        attribution_url='https://www.movi.de/service/copyright.shtml',
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

        # The first inner table is the navigation, the second one contains the parking sites
        rows: list[Tag] = root.find('table').find_all('table')[1].find_all('tr')

        # Every parking site row links to a detail page, all other rows are headers, spacers or the map link
        return [row for row in rows if row.find('a') is not None and len(row.find_all('td')) >= 5], {}

    def realtime_tag_to_dict(self, tag: Tag, **kwargs) -> Optional[dict]:
        cells: list[Tag] = tag.find_all('td')

        # The first row of each area has an additional cell with the area name
        offset: int = 1 if len(cells) > 5 else 0

        try:
            realtime_data_updated_at = datetime.strptime(
                cells[offset + 4].get_text().strip(),
                '%d.%m.%Y %H:%M Uhr',
            ).replace(tzinfo=ZoneInfo('Europe/Berlin'))
        except ValueError:
            # Instead of a date, the source says that there is no realtime data available
            return None

        free_capacity: str = cells[offset + 1].get_text().strip()
        if not free_capacity.isdigit():
            return None

        realtime_parking_site_dict: dict[str, Any] = {
            'uid': tag.find('a').attrs.get('href').split('/')[-1].removesuffix('.shtml'),
            'realtime_data_updated_at': realtime_data_updated_at.isoformat(),
            'realtime_opening_status': OpeningStatus.OPEN.value,
            'realtime_free_capacity': int(free_capacity),
        }

        return realtime_parking_site_dict
