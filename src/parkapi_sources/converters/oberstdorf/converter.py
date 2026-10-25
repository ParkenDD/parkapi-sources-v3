"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingFacilityMixin, ParkingFacilityStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class OberstdorfPullConverter(
    ParkingFacilityMixin,
    ParkingFacilityStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'OBERSTDORF'

    source_info = SourceInfo(
        uid='oberstdorf',
        name='Markt Oberstdorf',
        public_url='https://mobilithek.info/offers/646664714287235072',
        attribution_contributor='Markt Oberstdorf',
        has_realtime_data=True,
    )
