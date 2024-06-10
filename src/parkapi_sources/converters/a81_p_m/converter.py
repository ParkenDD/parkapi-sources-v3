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

from .models import A81PMInput


class A81PMPullConverter(PullConverter):
    required_config_keys = ['PARK_API_A81_P_M_TOKEN']

    list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    a81_p_m_site_validator = DataclassValidator(A81PMInput)

    source_info = SourceInfo(
        uid='a81_p_m',
        name='A81: P&M',
        source_url='https://api.cloud-telartec.de/v1/parkings',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        a81_p_m_inputs, static_parking_site_errors = self._get_data()

        for a81_p_m_input in a81_p_m_inputs:
            static_parking_site_inputs.append(a81_p_m_input.to_static_parking_site())

        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        a81_p_m_inputs, realtime_parking_site_errors = self._get_data()

        for a81_p_m_input in a81_p_m_inputs:
            realtime_parking_site_inputs.append(a81_p_m_input.to_realtime_parking_site())

        return realtime_parking_site_inputs, realtime_parking_site_errors

    def _get_data(self) -> tuple[list[A81PMInput], list[ImportParkingSiteException]]:
        a81_p_m_inputs: list[A81PMInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        response = requests.get(
            self.source_info.source_url,
            headers={'Authorization': f'Bearer {self.config_helper.get("PARK_API_A81_P_M_TOKEN")}'},
            timeout=60,
        )

        for input_dict in self.list_validator.validate(response.json()):
            try:
                a81_p_m_inputs.append(self.a81_p_m_site_validator.validate(input_dict))
            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('id'),
                        message=f'validation error for static data {input_dict}: {e.to_dict()}',
                    ),
                )

        return a81_p_m_inputs, parking_site_errors
