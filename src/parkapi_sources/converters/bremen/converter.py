"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingRecordStatusMixin, UrbanParkingSiteMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class BremenPullConverter(
    UrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'BREMEN'

    source_info = SourceInfo(
        uid='bremen',
        name='Verkehrsmanagementzentrale Bremen',
        public_url='https://mobilithek.info/offers/110000000002500000',
        attribution_contributor='Verkehrsmanagementzentrale Bremen',
        has_realtime_data=True,
    )
