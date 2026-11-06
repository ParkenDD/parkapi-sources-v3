"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2_v3 import ParkingRecordStatusV3Mixin, UrbanParkingSiteV3Mixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class PRHessenPullConverter(
    UrbanParkingSiteV3Mixin,
    ParkingRecordStatusV3Mixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The data is not valid DATEX II: the root element is PayloadPublication instead of payload, so no parking site can be
    imported.
    """

    config_key = 'P_R_HESSEN'
    mobilithek_datex2_version = 3

    source_info = SourceInfo(
        uid='p_r_hessen',
        name='ivm: P+R Hessen',
        public_url='https://mobilithek.info/offers/986574757105147904',
        attribution_contributor='ivm - Integriertes Verkehrs- und Mobilitätsmanagement Region Frankfurt RheinMain GmbH',
        has_realtime_data=True,
    )
