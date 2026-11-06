"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingRecordStatusMixin, UrbanParkingSiteMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import ParkingSiteRestrictionInput, SourceInfo, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingAudience


class HamburgPortAuthorityPullConverter(
    UrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'HAMBURG_PORT_AUTHORITY'

    source_info = SourceInfo(
        uid='hamburg_port_authority',
        name='Hamburg Port Authority: LKW-Parkplätze Hamburger Hafen',
        public_url='https://mobilithek.info/offers/658426993588482048',
        attribution_contributor='Hamburg Port Authority AöR',
        has_realtime_data=True,
    )

    def modify_static_parking_site_input(self, static_parking_site_input: StaticParkingSiteInput):
        # All parking sites are truck parking sites, which the urban parking site model cannot express
        static_parking_site_input.restrictions = [ParkingSiteRestrictionInput(type=ParkingAudience.TRUCK)]
