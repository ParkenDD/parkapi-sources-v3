"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

from validataclass.validators import DataclassValidator

from parkapi_sources.models import SourceInfo

from .base_converter import BfrkBasePushConverter
from .car_models import BfrkCarRowInput


class BfrkBwCarPushConverter(BfrkBasePushConverter, ABC):
    bfrk_row_validator = DataclassValidator(BfrkCarRowInput)

    header_mapping: dict[str, str] = {
        'ID': 'uid',
        'HST_Name': 'name',
        'Art': 'type',
        'Latitude': 'lat',
        'Longitude': 'lon',
        'Stellplatzanzahl_insgesamt': 'capacity',
        'Stellplatzanzahl_Behinderte': 'capacity_disabled',
        'Nutzungsbedingungen': 'description',
        'HST_DHID': 'identifier_dhid',
        'OSM_ID': 'identifier_osm',
        'Parkplatz_Foto': 'photo_url',
    }


class BfrkBwOepnvCarPushConverter(BfrkBwCarPushConverter):
    source_info = SourceInfo(
        uid='bfrk_bw_oepnv_car',
        name='Barrierefreie Reisekette Baden-Württemberg: PKW-Parkplätze an Bushaltestellen',
        public_url='https://www.mobidata-bw.de/dataset/bfrk-barrierefreiheit-an-bw-haltestellen',
        has_realtime_data=False,
    )


class BfrkBwSpnvCarPushConverter(BfrkBwCarPushConverter):
    source_info = SourceInfo(
        uid='bfrk_bw_spnv_car',
        name='Barrierefreie Reisekette Baden-Württemberg: PKW-Parkplätze an Bahnhöfen',
        public_url='https://www.mobidata-bw.de/dataset/bfrk-barrierefreiheit-an-bw-bahnhoefen',
        has_realtime_data=False,
    )
