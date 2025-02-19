"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from parkapi_sources.converters.base_converter.datex2 import ParkingFacilityMixin
from parkapi_sources.converters.base_converter.datex2.parking_record_status_mixin import ParkingRecordStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekPullConverter
from parkapi_sources.models import SourceInfo, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkAndRideType


class VrsBasePullConverter(ParkingFacilityMixin, ParkingRecordStatusMixin, MobilithekPullConverter, ABC):
    def modify_static_parking_site_input(self, static_parking_site_input: StaticParkingSiteInput) -> None:
        static_parking_site_input.park_and_ride_type = [ParkAndRideType.YES]
        static_parking_site_input.opening_hours = '24/7'


class VrsBondorfPullConverter(VrsBasePullConverter):
    config_key = 'VRS_BONDORF'

    source_info = SourceInfo(
        uid='vrs_bondorf',
        name='Verband Region Stuttgart: Bondorf',
        public_url='https://mobilithek.info',
        source_url='https://mobilithek.info',
        attribution_contributor='Verband Region Stuttgart',
        attribution_license='Datenlizenz Deutschland – Namensnennung – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/by-2-0',
        has_realtime_data=True,
    )


class VrsKirchheimPullConverter(VrsBasePullConverter):
    config_key = 'VRS_KIRCHHEIM'

    source_info = SourceInfo(
        uid='vrs_kirchheim',
        name='Verband Region Stuttgart: Kirchheim',
        public_url='https://mobilithek.info',
        source_url='https://mobilithek.info',
        attribution_contributor='Verband Region Stuttgart',
        attribution_license='Datenlizenz Deutschland – Namensnennung – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/by-2-0',
        has_realtime_data=True,
    )


class VrsNeustadtPullConverter(VrsBasePullConverter):
    config_key = 'VRS_NEUSTADT'

    source_info = SourceInfo(
        uid='vrs_neustadt',
        name='Verband Region Stuttgart: Neustadt',
        public_url='https://mobilithek.info',
        source_url='https://mobilithek.info',
        attribution_contributor='Verband Region Stuttgart',
        attribution_license='Datenlizenz Deutschland – Namensnennung – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/by-2-0',
        has_realtime_data=True,
    )


class VrsVaihingenPullConverter(VrsBasePullConverter):
    config_key = 'VRS_VAIHINGEN'

    source_info = SourceInfo(
        uid='vrs_vaihingen',
        name='Verband Region Stuttgart: Vaihingen',
        public_url='https://mobilithek.info',
        source_url='https://mobilithek.info',
        attribution_contributor='Verband Region Stuttgart',
        attribution_license='Datenlizenz Deutschland – Namensnennung – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/by-2-0',
        has_realtime_data=True,
    )
