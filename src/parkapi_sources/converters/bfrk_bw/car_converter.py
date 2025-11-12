"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import ParkingSpotPullConverter
from parkapi_sources.exceptions import ImportParkingSpotException
from parkapi_sources.models import SourceInfo, StaticParkingSpotInput

from .base_converter import BfrkBasePushConverter
from .car_models import BfrkCarInput


class BfrkBwCarPushConverter(BfrkBasePushConverter, ParkingSpotPullConverter):
    bfrk_validator = DataclassValidator(BfrkCarInput)
    source_url_config_key = 'PARK_API_BFRK_BW_CAR_OVERRIDE_SOURCE_URL'

    source_info = SourceInfo(
        uid='bfrk_bw_car',
        name='Barrierefreie Reisekette Baden-Württemberg: PKW-Parkplätze',
        public_url='https://www.mobidata-bw.de/dataset/bfrk-barrierefreiheit-an-bw-haltestellen',
        source_url='https://bfrk-kat-api.efa-bw.de/bfrk_api/parkplaetze',
        has_realtime_data=False,
    )

    def get_static_parking_spots(self) -> tuple[list[StaticParkingSpotInput], list[ImportParkingSpotException]]:
        static_parking_spot_inputs: list[StaticParkingSpotInput] = []
        static_parking_spot_errors: list[ImportParkingSpotException] = []

        source_url = self.config_helper.get(self.source_url_config_key, self.source_info.source_url)
        response = self.request_get(url=source_url, timeout=300)

        input_dicts = response.json()

        for input_dict in input_dicts:
            try:
                input_data: BfrkCarInput = self.bfrk_validator.validate(input_dict)
            except ValidationError as e:
                static_parking_spot_errors.append(
                    ImportParkingSpotException(
                        source_uid=self.source_info.uid,
                        parking_spot_uid=input_dict.get('infraid'),
                        message=f'validation error for {input_dict}: {e.to_dict()}',
                    ),
                )
                continue

            new_static_parking_spot_inputs = input_data.to_static_parking_spot_inputs()
            if new_static_parking_spot_inputs is None:
                continue

            static_parking_spot_inputs += new_static_parking_spot_inputs

        return static_parking_spot_inputs, static_parking_spot_errors
