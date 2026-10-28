"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingRecordStatusMixin, UrbanParkingSiteMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class NrwDisabledPullConverter(
    UrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The data is not valid DATEX II: the data offer declares DATEX II 2.3 as XML, but the publication is JSON in the
    structure of a DATEX II v3 ParkingPublicationLight. So no parking site can be imported. There is no realtime data,
    so just the static subscription is needed.
    """

    config_key = 'NRW_DISABLED'

    source_info = SourceInfo(
        uid='nrw_disabled',
        name='NRW.Mobidrom: Behindertenparkplätze NRW',
        public_url='https://mobilithek.info/offers/1029367261516726272',
        attribution_contributor='NRW.Mobidrom',
        attribution_license='CC BY 4.0',
        attribution_url='https://creativecommons.org/licenses/by/4.0/',
        has_realtime_data=False,
    )
