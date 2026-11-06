"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingRecordStatusMixin, UrbanParkingSiteMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class KoelnPullConverter(
    UrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'KOELN'

    source_info = SourceInfo(
        uid='koeln',
        name='Stadt Köln',
        public_url='https://mobilithek.info/offers/110000000002898000',
        attribution_contributor='Stadt Köln',
        attribution_license='Datenlizenz Deutschland – Zero – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/zero-2-0',
        has_realtime_data=True,
    )
