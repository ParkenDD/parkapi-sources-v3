"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import HeidelbergInput


class HeidelbergPullConverter(PullConverter):
    required_config_keys = ['PARK_API_HEIDELBERG_API_KEY']
    list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    heidelberg_validator = DataclassValidator(HeidelbergInput)

    source_info = SourceInfo(
        uid='heidelberg',
        name='Stadt Heidelberg',
        public_url='https://parken.heidelberg.de',
        source_url='https://api.datenplattform.heidelberg.de/ckan/or/mobility/main/offstreetparking/v2/entities',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Heidelberg',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        heidelberg_inputs, import_parking_site_exceptions = self._get_data()

        for heidelberg_input in heidelberg_inputs:
            static_parking_site_inputs.append(heidelberg_input.to_static_parking_site())

        return static_parking_site_inputs, import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        heidelberg_inputs, import_parking_site_exceptions = self._get_data()

        for heidelberg_input in heidelberg_inputs:
            if heidelberg_input.availableSpotNumber is None:
                continue
            realtime_parking_site_inputs.append(heidelberg_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _get_data(self) -> tuple[list[HeidelbergInput], list[ImportParkingSiteException]]:
        heidelberg_inputs: list[HeidelbergInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = self.request_get(
            url=self.source_info.source_url,
            params={'api-key': self.config_helper.get('PARK_API_HEIDELBERG_API_KEY'), 'limit': 50},
            headers={'X-Gravitee-Api-Key': self.config_helper.get('PARK_API_HEIDELBERG_API_KEY')},
            timeout=30,
        )

        response_data = response.json()
        try:
            input_dicts = self.list_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid Input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

        for input_dict in input_dicts:
            try:
                heidelberg_input = self.heidelberg_validator.validate(input_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('staticParkingSiteId'),
                        message=f'Invalid data at uid {input_dict.get("staticParkingSiteId")}: {e.to_dict()}, '
                        f'data: {input_dict}',
                    ),
                )
                continue

            heidelberg_inputs.append(heidelberg_input)

        return heidelberg_inputs, import_parking_site_exceptions
