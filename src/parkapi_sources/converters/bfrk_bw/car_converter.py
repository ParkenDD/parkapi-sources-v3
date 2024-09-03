"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.validators import DataclassValidator

from parkapi_sources.models import SourceInfo

from .base_converter import BfrkBasePushConverter
from .car_models import BfrkCarInput


class BfrkBwCarPushConverter(BfrkBasePushConverter):
    bfrk_validator = DataclassValidator(BfrkCarInput)
    source_url_config_key = 'PARK_API_BFRK_BW_CAR_OVERRIDE_SOURCE_URL'

    source_info = SourceInfo(
        uid='bfrk_bw_car',
        name='Barrierefreie Reisekette Baden-Württemberg: PKW-Parkplätze',
        public_url='https://www.mobidata-bw.de/dataset/bfrk-barrierefreiheit-an-bw-haltestellen',
        source_url='https://bfrk-kat-api.efa-bw.de/bfrk_api/parkplaetze',
        has_realtime_data=False,
    )
