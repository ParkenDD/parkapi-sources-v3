"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import requests
from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import KienzlerInput


class KienzlerPullConverter(PullConverter):
    kienzler_list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    kienzler_item_validator = DataclassValidator(KienzlerInput)

    required_config_keys = ['PARK_API_KIENZLER_USER', 'PARK_API_KIENZLER_PASSWORD', 'PARK_API_KIENZLER_IDS']
    source_info = SourceInfo(
        uid='kienzler',
        name='Kienzler',
        has_realtime_data=True,
        public_url='https://www.bikeandridebox.de',
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        kienzler_parking_sites, static_parking_site_errors = self._get_kienzler_parking_sites()
        for kienzler_parking_site in kienzler_parking_sites:
            static_parking_site_inputs.append(kienzler_parking_site.to_static_parking_site())

        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        kienzler_parking_sites, static_parking_site_errors = self._get_kienzler_parking_sites()
        for kienzler_parking_site in kienzler_parking_sites:
            realtime_parking_site_inputs.append(kienzler_parking_site.to_realtime_parking_site())

        return realtime_parking_site_inputs, static_parking_site_errors

    def _get_kienzler_parking_sites(self) -> tuple[list[KienzlerInput], list[ImportParkingSiteException]]:
        kienzler_item_inputs: list[KienzlerInput] = []
        errors: list[ImportParkingSiteException] = []

        parking_site_dicts = self.kienzler_list_validator.validate(self._request())
        for parking_site_dict in parking_site_dicts:
            try:
                kienzler_item_inputs.append(self.kienzler_item_validator.validate(parking_site_dict))
            except ValidationError as e:
                errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('uid'),
                        message=f'validation error for {parking_site_dict}: {e.to_dict()}',
                    ),
                )
        return kienzler_item_inputs, errors

    def _request(self) -> list[dict]:
        response = requests.post(
            url='https://www.bikeandridebox.de/index.php?eID=JSONAPI',
            json={
                'user': self.config_helper.get('PARK_API_KIENZLER_USER'),
                'password': self.config_helper.get('PARK_API_KIENZLER_PASSWORD'),
                'action': 'capacity',
                'context': 'unit',
                'ids': self.config_helper.get('PARK_API_KIENZLER_IDS').split(','),
            },
            timeout=30,
        )

        return response.json()
