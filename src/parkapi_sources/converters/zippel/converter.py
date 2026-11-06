"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import InterUrbanParkingSiteMixin, ParkingRecordStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class ZippelPullConverter(
    InterUrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'ZIPPEL'

    source_info = SourceInfo(
        uid='zippel',
        name='Zippel Logistik: LKW-Parkplatz Dummerstorf',
        public_url='https://mobilithek.info/offers/1047107739624091648',
        attribution_contributor='Zippel Logistik GmbH',
        has_realtime_data=True,
    )
