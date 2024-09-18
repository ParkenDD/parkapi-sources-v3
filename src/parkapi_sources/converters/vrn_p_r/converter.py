"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import requests
from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import VrnParkAndRideMultiguideInput, VrnParkAndRideSonahInput
from .vrn_converter import VrnParkAndRidePullConverter


class VrnParkAndRideMultiguidePullConverter(VrnParkAndRidePullConverter):
    list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    vrn_multiguide_validator = DataclassValidator(VrnParkAndRideMultiguideInput)

    source_info = SourceInfo(
        uid='vrn_p_r_multiguide',
        name='Verkehrsverbund Rhein-Neckar GmbH: Multiguide API - P+R Parkplätze',
        source_url='https://vrn.multiguide.info/api/area',
        has_realtime_data=True,  # ATM it's impossible to get realtime data due rate limit restrictions
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_raw_static_parking_sites()

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        realtime_multiguide_inputs, import_parking_site_exceptions = self._get_raw_realtime_parking_sites()

        for realtime_multiguide_input in realtime_multiguide_inputs:
            realtime_parking_site_inputs.append(realtime_multiguide_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _get_raw_realtime_parking_sites(self) -> tuple[list[VrnParkAndRideMultiguideInput], list[ImportParkingSiteException]]:
        vrn_multiguide_inputs: list[VrnParkAndRideMultiguideInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = requests.get(
            url=self.source_info.source_url,
            auth=(
                self.config_helper.get('PARK_API_VRN_P_R_MULTIGUIDE_USERNAME'),
                self.config_helper.get('PARK_API_VRN_P_R_MULTIGUIDE_PASSWORD'),
            ),
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
                vrn_multiguide_input = self.vrn_multiguide_validator.validate(input_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('Id'),
                        message=f'Invalid data at uid {input_dict.get("Id")}: {e.to_dict()}, ' f'data: {input_dict}',
                    ),
                )
                continue

            vrn_multiguide_inputs.append(vrn_multiguide_input)

        return vrn_multiguide_inputs, import_parking_site_exceptions


class VrnParkAndRideSonahPullConverter(VrnParkAndRidePullConverter):
    list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    vrn_sonah_validator = DataclassValidator(VrnParkAndRideSonahInput)

    source_info = SourceInfo(
        uid='vrn_p_r_sonah',
        name='Verkehrsverbund Rhein-Neckar GmbH: Sonah API - P+R Parkplätze',
        source_url='https://vrnm.dyndns.sonah.xyz/api/v3/rest/json/locations',
        has_realtime_data=True,  # ATM it's impossible to get realtime data due rate limit restrictions
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        return self._get_raw_static_parking_sites()

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        realtime_sonah_inputs, import_parking_site_exceptions = self._get_raw_realtime_parking_sites()

        for realtime_sonah_input in realtime_sonah_inputs:
            realtime_parking_site_inputs.append(realtime_sonah_input.to_realtime_parking_site_input())

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _get_raw_realtime_parking_sites(self) -> tuple[list[VrnParkAndRideSonahInput], list[ImportParkingSiteException]]:
        vrn_sonah_inputs: list[VrnParkAndRideSonahInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        headers: dict[str, str] = {
            'Accept': 'application/json',
            'Authorization': self.config_helper.get('PARK_API_VRN_P_R_SONAH_BEARER_TOKEN'),
        }

        response = requests.get(
            self.source_info.source_url,
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
                vrn_sonah_input = self.vrn_sonah_validator.validate(input_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('LocationID'),
                        message=f'Invalid data at uid {input_dict.get("LocationID")}: {e.to_dict()}, ' f'data: {input_dict}',
                    ),
                )
                continue

            vrn_sonah_inputs.append(vrn_sonah_input)

        return vrn_sonah_inputs, import_parking_site_exceptions
