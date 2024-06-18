"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from validataclass.validators import DataclassValidator

from parkapi_sources.models import SourceInfo

from .base_converter import BfrkBasePushConverter
from .bike_models import BfrkBikeRowInput


class BfrkBwBikePushConverter(BfrkBasePushConverter, ABC):
    bfrk_row_validator = DataclassValidator(BfrkBikeRowInput)

    header_mapping: dict[str, str] = {
        'ID': 'uid',
        'HST_Name': 'name',
        'Anlagentyp': 'type',
        'Latitude': 'lat',
        'Longitude': 'lon',
        'Stellplatzanzahl': 'capacity',
        'beleuchtet': 'has_lighting',
        'kostenpflichtig': 'has_fee',
        'ueberdacht': 'has_roof',
        'HST_DHID': 'identifier_dhid',
        'OSM_ID': 'identifier_osm',
        'Anlage_Foto': 'photo_url',
    }


class BfrkBwOepnvBikePushConverter(BfrkBwBikePushConverter):
    source_info = SourceInfo(
        uid='bfrk_bw_oepnv_bike',
        name='Barrierefreie Reisekette Baden-Württemberg: Fahrrad-Parkplätze an Bushaltestellen',
        public_url='https://www.mobidata-bw.de/dataset/bfrk-barrierefreiheit-an-bw-haltestellen',
        has_realtime_data=False,
    )


class BfrkBwSpnvBikePushConverter(BfrkBwBikePushConverter):
    source_info = SourceInfo(
        uid='bfrk_bw_spnv_bike',
        name='Barrierefreie Reisekette Baden-Württemberg: Fahrrad-Parkplätze an Bahnhöfen',
        public_url='https://www.mobidata-bw.de/dataset/bfrk-barrierefreiheit-an-bw-bahnhoefen',
        has_realtime_data=False,
    )
