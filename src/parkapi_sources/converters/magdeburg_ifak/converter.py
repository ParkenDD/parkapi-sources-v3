"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingFacilityMixin, ParkingFacilityStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class MagdeburgIfakPullConverter(
    ParkingFacilityMixin,
    ParkingFacilityStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The data is not valid DATEX II: the documents lack the required modelBaseVersion attribute, and the realtime data
    contains negative numbers of occupied spaces.
    """

    config_key = 'MAGDEBURG_IFAK'

    source_info = SourceInfo(
        uid='magdeburg_ifak',
        name='Landeshauptstadt Magdeburg: ifak',
        public_url='https://mobilithek.info/offers/683633364717989888',
        attribution_contributor='ifak e.V.',
        has_realtime_data=True,
    )
