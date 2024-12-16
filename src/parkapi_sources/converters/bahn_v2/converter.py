"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import requests
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .mapper import BahnMapper
from .validators import BahnParkingSiteInput


class BahnV2PullConverter(PullConverter):
    _base_url = 'https://apis.deutschebahn.com/db-api-marketplace/apis/parking-information/db-bahnpark/v2'
    required_config_keys = ['PARK_API_BAHN_API_CLIENT_ID', 'PARK_API_BAHN_API_CLIENT_SECRET']

    mapper = BahnMapper()
    bahn_parking_site_validator = DataclassValidator(BahnParkingSiteInput)

    source_info = SourceInfo(
        uid='bahn_v2',
        name='Deutsche Bahn Parkplätze',
        public_url='https://www.dbbahnpark.de',
        has_realtime_data=False,  # ATM it's impossible to get realtime data due rate limit restrictions
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list = []
        static_parking_site_errors: list[ImportParkingSiteException] = []

        parking_site_dicts = self.get_data()

        for parking_site_dict in parking_site_dicts.get('_embedded', []):
            try:
                parking_site_input: BahnParkingSiteInput = self.bahn_parking_site_validator.validate(parking_site_dict)
            except ValidationError as e:
                static_parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('id'),
                        message=f'validation error for data {parking_site_dict}: {e.to_dict()}',
                    ),
                )
                continue

            static_parking_site_inputs.append(
                self.mapper.map_static_parking_site(parking_site_input),
            )
        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        return [], []  # ATM it's impossible to get realtime data due rate limit restrictions

    def get_data(self) -> dict:
        headers: dict[str, str] = {
            'DB-Client-Id': self.config_helper.get('PARK_API_BAHN_API_CLIENT_ID'),
            'DB-Api-Key': self.config_helper.get('PARK_API_BAHN_API_CLIENT_SECRET'),
            'Accept': 'application/vnd.parkinginformation.db-bahnpark.v1+json',
            'accept': 'application/json',
        }

        response = requests.get(
            f'{self.config_helper.get("PARK_API_BAHN_URL", self._base_url)}/parking-facilities',
            headers=headers,
            timeout=60,
        )
        return response.json()
