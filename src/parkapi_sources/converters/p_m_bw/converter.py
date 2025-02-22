"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.pull import PullConverter, StaticGeojsonDataMixin
from parkapi_sources.exceptions import ImportParkingSiteException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import PMBWInput


class PMBWPullConverter(PullConverter, StaticGeojsonDataMixin):
    required_config_keys = ['PARK_API_P_M_BW_TOKEN']

    list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    p_m_bw_site_validator = DataclassValidator(PMBWInput)

    source_info = SourceInfo(
        uid='p_m_bw',
        name='Parken und Mitfahren Baden-Württemberg',
        source_url='https://api.cloud-telartec.de/v1/parkings',
        has_realtime_data=True,
    )

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        p_m_bw_parking_site_inputs, static_parking_site_errors = self._get_data()

        geojson_parking_site_inputs, geojson_parking_site_errors = self._get_static_parking_site_inputs_and_exceptions(
            source_uid=self.source_info.uid,
        )

        static_parking_site_errors += geojson_parking_site_errors

        static_parking_site_inputs: list[StaticParkingSiteInput] = []
        static_parking_site_inputs_by_uid: dict[str, StaticParkingSiteInput] = {}
        for p_m_bw_parking_site_input in p_m_bw_parking_site_inputs:
            static_parking_site_input = p_m_bw_parking_site_input.to_static_parking_site()
            static_parking_site_inputs.append(static_parking_site_input)
            static_parking_site_inputs_by_uid[p_m_bw_parking_site_input.id] = static_parking_site_input

        for geojson_parking_site_input in geojson_parking_site_inputs:
            # If the uid is not known in our static data: ignore the realtime data
            if geojson_parking_site_input.uid not in static_parking_site_inputs_by_uid:
                continue

            # Extend API data with static GeoJSON data
            static_parking_site_input = static_parking_site_inputs_by_uid[geojson_parking_site_input.uid]
            static_parking_site_input.name = geojson_parking_site_input.name
            static_parking_site_input.address = geojson_parking_site_input.address
            static_parking_site_input.description = geojson_parking_site_input.description
            static_parking_site_input.type = geojson_parking_site_input.type

        return static_parking_site_inputs, static_parking_site_errors

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        p_m_bw_inputs, realtime_parking_site_errors = self._get_data()

        for p_m_bw_input in p_m_bw_inputs:
            realtime_parking_site_inputs.append(p_m_bw_input.to_realtime_parking_site())

        return realtime_parking_site_inputs, realtime_parking_site_errors

    def _get_data(self) -> tuple[list[PMBWInput], list[ImportParkingSiteException]]:
        p_m_bw_inputs: list[PMBWInput] = []
        parking_site_errors: list[ImportParkingSiteException] = []

        response = self.request_get(
            url=self.source_info.source_url,
            headers={'Authorization': f'Bearer {self.config_helper.get("PARK_API_P_M_BW_TOKEN")}'},
            timeout=60,
        )

        for input_dict in self.list_validator.validate(response.json()):
            try:
                p_m_bw_inputs.append(self.p_m_bw_site_validator.validate(input_dict))
            except ValidationError as e:
                parking_site_errors.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=input_dict.get('id'),
                        message=f'validation error for static data {input_dict}: {e.to_dict()}',
                    ),
                )

        return p_m_bw_inputs, parking_site_errors
