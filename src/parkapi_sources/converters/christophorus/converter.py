"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2_v3 import ParkingRecordStatusV3Mixin, UrbanParkingSiteV3Mixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class ChristophorusPullConverter(
    UrbanParkingSiteV3Mixin,
    ParkingRecordStatusV3Mixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The data is not valid DATEX II: it does not validate against its declared profile Parkraummanagement DATEX II v3. The
    payload is wrapped in a messageContainer, the static data uses a hierarchyElementGeneral of type ParkingArea instead
    of parking records and the realtime data uses parkingStatusInformation instead of parking record status, which are
    not part of the profile. So no parking site can be imported.
    """

    config_key = 'CHRISTOPHORUS'
    mobilithek_datex2_version = 3

    source_info = SourceInfo(
        uid='christophorus',
        name='Florence Knuellwald: Lkw-Parkplatz Christophorus',
        public_url='https://mobilithek.info/offers/872174540205998080',
        attribution_contributor='Florence Knuellwald GmbH',
        attribution_license='Datenlizenz Deutschland – Namensnennung – Version 2.0',
        attribution_url='https://www.govdata.de/dl-de/by-2-0',
        has_realtime_data=True,
    )
