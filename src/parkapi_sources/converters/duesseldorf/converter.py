"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingFacilityMixin, ParkingFacilityStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class DuesseldorfPullConverter(
    ParkingFacilityMixin,
    ParkingFacilityStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'DUESSELDORF'

    source_info = SourceInfo(
        uid='duesseldorf',
        name='Landeshauptstadt Düsseldorf',
        public_url='https://mobilithek.info/offers/110000000002055003',
        attribution_contributor='Landeshauptstadt Düsseldorf',
        has_realtime_data=True,
    )
