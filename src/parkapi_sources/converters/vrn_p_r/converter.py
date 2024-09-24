"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC

import requests
from validataclass.exceptions import ValidationError
from validataclass.validators import AnythingValidator, DataclassValidator, ListValidator

from parkapi_sources.converters.base_converter.pull import GeojsonInput, PullConverter
from parkapi_sources.exceptions import ImportParkingSiteException, ImportSourceException
from parkapi_sources.models import RealtimeParkingSiteInput, SourceInfo, StaticParkingSiteInput

from .models import VrnParkAndRideFeaturesInput, VrnParkAndRideMultiguideInput, VrnParkAndRideSonahInput


class VrnParkAndRidePullConverter(PullConverter, ABC):
    list_validator = ListValidator(AnythingValidator(allowed_types=[dict]))
    geojson_validator = DataclassValidator(GeojsonInput)
    vrn_p_r_feature_validator = DataclassValidator(VrnParkAndRideFeaturesInput)
    vrn_multiguide_validator = DataclassValidator(VrnParkAndRideMultiguideInput)
    vrn_sonah_validator = DataclassValidator(VrnParkAndRideSonahInput)

    source_info = SourceInfo(
        uid='vrn_p_r',
        name='Verkehrsverbund Rhein-Neckar GmbH - P+R Parkplätze',
        public_url='https://www.vrn.de/opendata/datasets/pr-parkplaetze-mit-vrn-parksensorik',
        timezone='Europe/Berlin',
        has_realtime_data=True,
    )

    def _get_feature_inputs(self) -> tuple[list[VrnParkAndRideFeaturesInput], list[ImportParkingSiteException]]:
        feature_inputs: list[VrnParkAndRideFeaturesInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        response = requests.get(
            url='https://spatial.vrn.de/data/rest/services/Hosted/p_r_parkapi_static/FeatureServer/5/query?where=objectid%3E0&outFields=*&returnGeometry=true&f=geojson',
            timeout=30,
        )
        response_data = response.json()

        try:
            geojson_input = self.geojson_validator.validate(response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid Input at source {self.source_info.uid}: {e.to_dict()}, data: {response_data}',
            ) from e

        for feature_dict in geojson_input.features:
            if self._should_ignore_dataset(feature_dict):
                continue

            try:
                feature_input = self.vrn_p_r_feature_validator.validate(feature_dict)
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=feature_dict.get('properties', {}).get('id'),
                        message=f'Invalid data at uid {feature_dict.get("properties", {}).get("id")}: '
                        f'{e.to_dict()}, data: {feature_dict}',
                    ),
                )
                continue

            feature_inputs.append(feature_input)

        return feature_inputs, import_parking_site_exceptions

    def _should_ignore_dataset(self, feature_dict: dict) -> bool:
        if self.config_helper.get('PARK_API_VRN_P_R_IGNORE_MISSING_CAPACITIES'):
            return feature_dict.get('properties', {}).get('capacity') is None

        return False

    def get_static_parking_sites(self) -> tuple[list[StaticParkingSiteInput], list[ImportParkingSiteException]]:
        feature_inputs, import_parking_site_exceptions = self._get_feature_inputs()
        static_parking_site_inputs: list[StaticParkingSiteInput] = []

        realtime_vrn_p_r_inputs, import_realtime_parking_site_exceptions = self._get_raw_realtime_parking_sites()
        import_parking_site_exceptions += import_realtime_parking_site_exceptions

        static_parking_site_inputs_by_uid: dict[str, StaticParkingSiteInput] = {}
        for feature_input in feature_inputs:
            static_parking_site_inputs_by_uid[str(feature_input.properties.vrn_sensor_id)] = feature_input.to_static_parking_site_input()

        for realtime_vrn_p_r_input in realtime_vrn_p_r_inputs:
            # If the realtime group_uid is not known in our static data: ignore the static data
            parking_site_uid = str(realtime_vrn_p_r_input.uid)
            if parking_site_uid in static_parking_site_inputs_by_uid:
                # Update static data with only parking places having realtime data
                static_parking_site_inputs.append(static_parking_site_inputs_by_uid[parking_site_uid])

        return static_parking_site_inputs, import_parking_site_exceptions

    def _get_raw_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []
        import_parking_site_exceptions: list[ImportParkingSiteException] = []

        multiguide_response_data = self._request_vrn_multiguide()
        sonah_response_data = self._request_vrn_sonah()

        try:
            multiguide_parking_site_dicts = self.list_validator.validate(multiguide_response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid Input at source {self.source_info.uid}: {e.to_dict()}, data: {multiguide_response_data}',
            ) from e

        for multiguide_parking_site_dict in multiguide_parking_site_dicts:
            try:
                realtime_parking_site_inputs.append(
                    self.vrn_multiguide_validator.validate(multiguide_parking_site_dict).to_realtime_parking_site_input()
                )
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=multiguide_parking_site_dict.get('Id'),
                        message=f'validation error for {multiguide_parking_site_dict}: {e.to_dict()}',
                    ),
                )

        try:
            sonah_parking_site_dicts = self.list_validator.validate(sonah_response_data)
        except ValidationError as e:
            raise ImportSourceException(
                source_uid=self.source_info.uid,
                message=f'Invalid Input at source {self.source_info.uid}: {e.to_dict()}, data: {sonah_response_data}',
            ) from e

        for sonah_parking_site_dict in sonah_parking_site_dicts:
            try:
                realtime_parking_site_inputs.append(
                    self.vrn_sonah_validator.validate(sonah_parking_site_dict).to_realtime_parking_site_input()
                )
            except ValidationError as e:
                import_parking_site_exceptions.append(
                    ImportParkingSiteException(
                        source_uid=self.source_info.uid,
                        parking_site_uid=sonah_parking_site_dict.get('LocationID'),
                        message=f'validation error for {sonah_parking_site_dict}: {e.to_dict()}',
                    ),
                )

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def get_realtime_parking_sites(self) -> tuple[list[RealtimeParkingSiteInput], list[ImportParkingSiteException]]:
        static_parking_site_inputs, import_parking_site_exceptions = self.get_static_parking_sites()
        realtime_parking_site_inputs: list[RealtimeParkingSiteInput] = []

        realtime_vrn_p_r_inputs, import_parking_site_exceptions = self._get_raw_realtime_parking_sites()
        static_parking_site_inputs_by_uid: dict[str, StaticParkingSiteInput] = {}

        for static_parking_site_input in static_parking_site_inputs:
            static_parking_site_inputs_by_uid[static_parking_site_input.group_uid] = static_parking_site_input

        for realtime_vrn_p_r_input in realtime_vrn_p_r_inputs:
            # If the realtime group_uid is not known in our static data: ignore the realtime data
            parking_site_uid = str(realtime_vrn_p_r_input.uid)
            if parking_site_uid in static_parking_site_inputs_by_uid:
                # Update realtime data with only parking places having static data
                realtime_vrn_p_r_input.uid = static_parking_site_inputs_by_uid[parking_site_uid].uid
                realtime_parking_site_inputs.append(realtime_vrn_p_r_input)

        return realtime_parking_site_inputs, import_parking_site_exceptions

    def _request_vrn_multiguide(self) -> list[dict]:
        response = requests.get(
            url='https://vrn.multiguide.info/api/area',
            auth=(
                self.config_helper.get('PARK_API_VRN_P_R_MULTIGUIDE_API_USERNAME'),
                self.config_helper.get('PARK_API_VRN_P_R_MULTIGUIDE_API_PASSWORD'),
            ),
            timeout=30,
        )

        return response.json()

    def _request_vrn_sonah(self) -> list[dict]:
        headers: dict[str, str] = {
            'Accept': 'application/json',
            'Authorization': self.config_helper.get('PARK_API_VRN_P_R_SONAH_API_BEARER_TOKEN'),
        }

        response = requests.get(
            url='https://vrnm.dyndns.sonah.xyz/api/v3/rest/json/locations',
            headers=headers,
            timeout=30,
        )

        return response.json()
