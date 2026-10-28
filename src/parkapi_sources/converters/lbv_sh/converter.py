"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import InterUrbanParkingSiteMixin, ParkingRecordStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class LbvShPullConverter(
    InterUrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The parking locations of the static data have no coordinates, so no parking site can be imported.
    """

    config_key = 'LBV_SH'
    mobilithek_container = True

    source_info = SourceInfo(
        uid='lbv_sh',
        name='LBV.SH: LKW-Stellplätze auf BAB-Rastanlagen in Schleswig-Holstein',
        public_url='https://mobilithek.info/offers/748478832668725248',
        attribution_contributor='Landesbetrieb Straßenbau und Verkehr Schleswig-Holstein (LBV.SH)',
        attribution_license='Datenlizenz Deutschland – Zero – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/zero-2-0',
        has_realtime_data=True,
    )
