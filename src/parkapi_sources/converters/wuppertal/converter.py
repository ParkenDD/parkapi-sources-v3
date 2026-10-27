"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingFacilityMixin, ParkingFacilityStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class WuppertalPullConverter(
    ParkingFacilityMixin,
    ParkingFacilityStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'WUPPERTAL'

    source_info = SourceInfo(
        uid='wuppertal',
        name='Stadt Wuppertal',
        public_url='https://mobilithek.info/offers/110000000002025002',
        attribution_contributor='Stadt Wuppertal',
        attribution_license='Datenlizenz Deutschland – Zero – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/zero-2-0',
        has_realtime_data=True,
    )
