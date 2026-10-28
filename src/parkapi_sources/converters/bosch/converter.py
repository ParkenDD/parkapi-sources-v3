"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.converters.base_converter import ParkingSiteBaseConverter
from parkapi_sources.converters.base_converter.datex2 import InterUrbanParkingSiteMixin, ParkingRecordStatusMixin
from parkapi_sources.converters.base_converter.pull import MobilithekParkingSitePullConverter
from parkapi_sources.models import SourceInfo


class BoschThiersheimPullConverter(
    InterUrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The static data is not valid DATEX II: the parking location has the coordinates 0 / 0, so no parking site can be
    imported.
    """

    config_key = 'BOSCH_THIERSHEIM'

    source_info = SourceInfo(
        uid='bosch_thiersheim',
        name='Bosch Service Solutions: Autohof Thiersheim',
        public_url='https://mobilithek.info/offers/608434098878160896',
        attribution_contributor='Bosch Service Solutions',
        attribution_license='CC BY 4.0',
        attribution_url='https://creativecommons.org/licenses/by/4.0/',
        has_realtime_data=True,
    )


class BoschSecureTruckParkingPullConverter(
    InterUrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    """
    The static data is not valid DATEX II: latitude and longitude of the parking locations are swapped.
    """

    config_key = 'BOSCH_SECURE_TRUCK_PARKING'

    source_info = SourceInfo(
        uid='bosch_secure_truck_parking',
        name='Bosch Service Solutions: Bosch Secure Truck Parking',
        public_url='https://mobilithek.info/offers/608434988204843008',
        attribution_contributor='Bosch Service Solutions',
        attribution_license='CC BY 4.0',
        attribution_url='https://creativecommons.org/licenses/by/4.0/',
        has_realtime_data=True,
    )


class BoschKindingPullConverter(
    InterUrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'BOSCH_KINDING'

    source_info = SourceInfo(
        uid='bosch_kinding',
        name='Bosch Service Solutions: Parkareal Kinding',
        public_url='https://mobilithek.info/offers/852486667684970496',
        attribution_contributor='Bosch Service Solutions',
        has_realtime_data=True,
    )


class BoschRastpark24PullConverter(
    InterUrbanParkingSiteMixin,
    ParkingRecordStatusMixin,
    MobilithekParkingSitePullConverter,
    ParkingSiteBaseConverter,
):
    config_key = 'BOSCH_RASTPARK_24'

    source_info = SourceInfo(
        uid='bosch_rastpark_24',
        name='Bosch Service Solutions: Rastpark 24',
        public_url='https://mobilithek.info/offers/925787550685814784',
        attribution_contributor='Bosch Service Solutions',
        has_realtime_data=True,
    )
