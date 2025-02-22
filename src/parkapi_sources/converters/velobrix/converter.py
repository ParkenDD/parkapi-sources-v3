"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.pull import PullConverter
from parkapi_sources.converters.velobrix.models import VelobrixInput
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput


class VelobrixPullConverter(PullConverter):
    required_config_keys = ['PARK_API_VELOBRIX_API_KEY']
    list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    velobrix_validator = DataclassValidator(VelobrixInput)

    source_info = SourceInfo(
        uid='velobrix',
        name='Velobrix',
        source_url='https://admin.velobrix.de/tenantapi/api/v1/locations',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        velobrix_inputs, import_parking_site_exceptions = self._get_data(include_pricing=True)

        for velobrix_input in velobrix_inputs:
            static_parking_site_inputs.append(velobrix_input.to_static_parking_site())

        return static_parking_site_inputs, import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        velobrix_inputs, import_parking_site_exceptions = self._get_data()

        for velobrix_input in velobrix_inputs:
            if velobrix_input.countFreeLogicalBoxes is None:
                continue
            realtime_parking_site_inputs.append(velobrix_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _get_data(self, include_pricing: bool = False) -> tuple[list[VelobrixInput], list[ImportParkingSiteException]]:
        velobrix_inputs: list[VelobrixInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        headers = {'Velobrix-ApiKey': self.config_helper.get('PARK_API_VELOBRIX_API_KEY')}
        if include_pricing:
            headers['IncludePriceModelDescription'] = 'true'

        response = self.request_get(
            url=self.source_info.source_url,
            headers=headers,
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
                velobrix_input = self.velobrix_validator.validate(input_dict)
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

            velobrix_inputs.append(velobrix_input)

        return velobrix_inputs, import_parking_site_exceptions
