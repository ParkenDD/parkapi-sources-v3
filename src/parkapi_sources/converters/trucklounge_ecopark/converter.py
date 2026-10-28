"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import InterUrbanParkingSiteMixin, ParkingRecordStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class TruckloungeEcoparkPullConverter(
    InterUrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The static data has no number of spaces, so no parking site can be imported. Additionally, it is not valid DATEX II:
    latitude and longitude of the parking location are swapped.
    """

    config_key = 'TRUCKLOUNGE_ECOPARK'

    source_info = SourceInfo(
        uid='trucklounge_ecopark',
        name='ENMO: Trucklounge Ecopark',
        public_url='https://mobilithek.info/offers/953737601668071424',
        attribution_contributor='ENMO GmbH & Co.KG',
        attribution_license='Open Data Commons Open Database License (ODbL)',
        attribution_url='https://opendatacommons.org/licenses/odbl/',
        has_realtime_data=True,
    )
