"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import ParkingFacilityMixin, ParkingFacilityStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo

from .models import DortmundParkingFacility


class DortmundPullConverter(
    ParkingFacilityMixin,
    ParkingFacilityStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The data is published in the Mobilithek container format. The static data is not valid DATEX II, because all
    parking facilities have an empty owner element, which requires a contactName. These are treated as missing owner.
    """

    config_key = 'DORTMUND'
    static_validator = DataclassValidator(DortmundParkingFacility)
    mobilithek_container = True

    source_info = SourceInfo(
        uid='dortmund',
        name='Stadt Dortmund',
        public_url='https://mobilithek.info/offers/555358777795076096',
        attribution_contributor='Stadt Dortmund',
        attribution_license='Datenlizenz Deutschland – Zero – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/zero-2-0',
        has_realtime_data=True,
    )
