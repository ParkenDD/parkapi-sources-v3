"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2_v3 import ParkingRecordStatusV3Mixin, UrbanParkingSiteV3Mixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class FrankfurtPullConverter(
    UrbanParkingSiteV3Mixin,
    ParkingRecordStatusV3Mixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The data is not valid DATEX II: it does not validate against its declared profile Parkraummanagement DATEX II v3
    (parkingSpaceOrGroupIdentifier at the static data and parkingStatusValidity at the realtime data are not part of it).
    """

    config_key = 'FRANKFURT'
    mobilithek_datex2_version = 3

    source_info = SourceInfo(
        uid='frankfurt',
        name='Stadt Frankfurt am Main',
        public_url='https://mobilithek.info/offers/919987874795593728',
        attribution_contributor='Stadt Frankfurt am Main',
        has_realtime_data=True,
    )
