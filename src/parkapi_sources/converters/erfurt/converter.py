"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingFacilityMixin, ParkingFacilityStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class ErfurtPullConverter(
    ParkingFacilityMixin,
    ParkingFacilityStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The data is not valid DATEX II: the static and realtime documents lack the required exchange element.
    """

    config_key = 'ERFURT'

    source_info = SourceInfo(
        uid='erfurt',
        name='Stadt Erfurt',
        public_url='https://mobilithek.info/offers/110000000002746001',
        attribution_contributor='Stadt Erfurt, TVA',
        has_realtime_data=True,
    )
