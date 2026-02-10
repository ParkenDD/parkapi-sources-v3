"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import requests
from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.pull import ParkingSitePullConverter
from parkapi_sources.converters.basel.models import BaselParkingSiteInput
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput


class BaselPullConverter(ParkingSitePullConverter):
    parking_sites_input_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    parking_site_validator = DataclassValidator(BaselParkingSiteInput)

    source_info = SourceInfo(
        uid='basel',
        name='Stadt Basel',
        public_url='https://www.parkleitsystem-basel.ch',
        source_url='https://data.bs.ch/api/v2/catalog/datasets/100088/exports/json',
        timezone='Europe/Berlin',
        attribution_contributor='Stadt Basel',
        attribution_license='CC BY 4.0',
        attribution_url='https://creativecommons.org/licenses/by/4.0/',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        parking_site_inputs, parking_site_errors = self._get_parking_site_inputs()

        for parking_site_input in parking_site_inputs:
            static_parking_site_inputs.append(parking_site_input.to_static_parking_site())

        return static_parking_site_inputs, parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        parking_site_inputs, parking_site_errors = self._get_parking_site_inputs()

        for parking_site_input in parking_site_inputs:
            realtime_parking_site_inputs.append(parking_site_input.to_realtime_parking_site())

        return realtime_parking_site_inputs, parking_site_errors

    def _get_parking_site_inputs(self) -> tuple[list[BaselParkingSiteInput], list[ImportParkingSiteException]]:
        parking_site_inputs: list[BaselParkingSiteInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        response = requests.get(self.source_info.source_url, timeout=60)
        parking_sites_dicts: list[dict] = self.parking_sites_input_validator.validate(response.json())

        for parking_site_dict in parking_sites_dicts:
            try:
                parking_site_inputs.append(self.parking_site_validator.validate(parking_site_dict))
            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=parking_site_dict.get('id'),
                        message=f'validation error for static data {parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return parking_site_inputs, parking_site_errors
