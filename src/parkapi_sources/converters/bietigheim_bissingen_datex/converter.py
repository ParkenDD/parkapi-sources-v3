"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingRecordStatusMixin, UrbanParkingSiteMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class BietigheimBissingenDatexPullConverter(
    UrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'BIETIGHEIM_BISSINGEN'

    source_info = SourceInfo(
        uid='bietigheim_bissingen_datex',
        name='Bietigheim Bissingen Datex II',
        public_url='https://mobilithek.info/offers/110000000003300000',
        has_realtime_data=True,
    )
